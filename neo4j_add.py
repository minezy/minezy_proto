import sys
import json
import time
import email
import email.utils
import itertools
import neo4j_conn
from py2neo import cypher, node, rel


class neo4jLoader:
    session = None
    tx = None
    opCount = 0
    targetCount = 1000
    names = {}
    unknownMsgId = 1
    
    def __init__(self):
        self.session = neo4j_conn.connect()
        return
    
    def _append(self, cypher, props=None, opCount=0):
        if self.tx is None:
            self.tx = self.session.create_transaction()
            
        self.tx.append(cypher, props)
        self.opCount += opCount
        
        if self.opCount > self.targetCount:
            self._write_batch()
        if len(self.names) > 500:
            self._write_names()
        return
    
    def _write_batch(self):
        sys.stdout.write("Writing batch ("+str(self.opCount)+")... ")
        t0 = time.time()
        try:
            self.tx.execute()
        except Exception, e:
            print e
            pass
        
        # size commits so they target 1-second to write
        t1 = time.time()
        dT = t1 - t0
        if (self.opCount > self.targetCount) or (dT > 1.0): 
            adj = (1.0 + dT) / 2
            self.targetCount = self.opCount / adj
            if self.targetCount < 100:
                self.targetCount = 100
        self.opCount = 0
             
        _write_time(dT)
        return
        
    def _write_names(self):
        sys.stdout.write("Writing names ("+str(len(self.names))+")... ")
        t0 = time.time()
        
        # transform names dict to lists of lists so cypher can consume
        props = []
        opCount = 0
        for e in self.names:
            names = self.names[e]
            for name in names:
                props.append( { 'email':e, 'name':name, 'count':names[name] } )
                opCount += 1
        
        cypher = "FOREACH (item in {props} | "
        cypher +=  "MERGE (a:Actor {email:item.email}) "
        cypher +=  "MERGE (n:Name {name:item.name}) "
        cypher +=  "MERGE (a)-[r:Name]->(n) ON CREATE SET r.count=item.count ON MATCH SET r.count=r.count+item.count) "
                 
        try:
            self.tx.append(cypher, { "props" : props })
            self.tx.execute()
            self.names.clear()
        except Exception, e:
            print e
            pass
        
        t1 = time.time()
        _write_time(t1-t0)
        return
    
    def commit(self):
        if not self.tx is None:
            self._write_batch()
            self._write_names()
            self.tx.commit()
            self.tx = None
        return

    def add(self, email_msg, count=0):
        try:
            msgSubject = _get_decoded(email_msg['Subject'])
            msgDate = _get_decoded(email_msg['Date'])
            msgID = _get_decoded(email_msg['Message-ID'])
            msgIDParent = _get_decoded(email_msg['In-Reply-To'])
            date = email.utils.parsedate_tz(msgDate)
            timestamp = email.utils.mktime_tz(date)
            
            if len(msgID) == 0 or msgID == "None":
                msgID = "Unknown_%05d" % self.unknownMsgId
                self.unknownMsgId += 1
            
            msgID = msgID.strip("<>")
            msgIDParent = msgIDParent.strip("<>")
            
            # Add From actor
            msgFrom = email.utils.getaddresses(email_msg.get_all('From', ['']))
            msgXFrom = email_msg.get_all('X-From', [''])
            self._collect_name(msgFrom[0], msgXFrom[0])
        
            msgEmail = str.lower(msgFrom[0][1])
            props = {"props" : { "id":msgID, "parentId":msgIDParent, "email":msgEmail, "subject":msgSubject, "date":msgDate, "timestamp":timestamp, "year":date[0], "month":date[1], "day":date[2] } }
    
            opCount = 0
            
            # Add Email
            cypher = "MERGE (e:Email {id:{props}.id}) "
            cypher += "SET e.subject={props}.subject, e.date={props}.date, e.timestamp={props}.timestamp, e.year={props}.year, e.month={props}.month, e.day={props}.day "
            # Add From Actor
            cypher += "MERGE (a:Actor {email:{props}.email}) "
            cypher += "CREATE UNIQUE (a)-[:Sent]->(e), (e)-[:SentBy]->(a) "
            opCount += 4
            
            # Email Thread Relation
            if msgIDParent != "None":
                cypher += "MERGE (ePar:Email {id:{props}.parentId}) "
                cypher += "CREATE UNIQUE (e)-[:InReplyTo]->(ePar), (ePar)-[:Reply]->(e) "
                opCount += 3
            
            # Email Thread References
            refs = []
            msgRefs = email.utils.getaddresses(email_msg.get_all('References', []))
            for msgIDRef in msgRefs:
                msgIDRef = msgIDRef[1].strip("<>")
                refs.append(msgIDRef)
            if len(refs):
                props['refs'] = refs
                cypher += "FOREACH (ref in {refs} | MERGE (eRef:Email {id:ref}) CREATE UNIQUE (e)-[:Refs]->(eRef)) "
                opCount += 2*len(refs)
        
            # Add TO relations
            tos = []
            msgTo = email.utils.getaddresses(email_msg.get_all('To', ['']))
            msgXTo = email_msg.get_all('X-To', [''])
            for msg,msgX in itertools.izip_longest(msgTo,msgXTo,fillvalue=''):
                if len(msg) > 0:
                    tos.append(str.lower(msg[1]))
                self._collect_name(msg, msgX)
            if len(tos):
                props['tos'] = tos
                cypher += "FOREACH (to IN {tos} | "
                cypher += "MERGE (aTo:Actor {email:to}) MERGE (e)-[:TO]->(aTo)) "
                opCount += 2*len(tos)
        
            # Add CC relations
            ccs = []
            msgCC = email.utils.getaddresses(email_msg.get_all('Cc', ['']))
            msgXCC = email_msg.get_all('X-Cc', [''])
            for msg,msgX in itertools.izip_longest(msgCC,msgXCC,fillvalue=''):
                if len(msg) > 0:
                    ccs.append(str.lower(msg[1]))
                self._collect_name(msg,msgX)
            if len(ccs):
                props['ccs'] = ccs
                cypher += "FOREACH (cc in {ccs} | MERGE (aCc:Actor {email:cc}) CREATE UNIQUE (e)-[:CC]->(aCc)) "
                opCount += 2*len(ccs)
            
            # Add BCC relations
            bccs = []
            msgBCC = email.utils.getaddresses(email_msg.get_all('bcc', []))
            msgXBCC = email_msg.get_all('X-bcc', [])
            for msg,msgX in itertools.izip_longest(msgBCC,msgXBCC,fillvalue=''):
                if len(msg) > 0:
                    bccs.append(str.lower(msg[1]))
                self._collect_name(msg,msgX)
            if len(bccs):
                props['bccs'] = bccs
                cypher += "FOREACH (bcc in {bccs} | MERGE (aBcc:Actor {email:bcc}) CREATE UNIQUE (e)-[:BCC]->(aBcc)) "
                opCount += 2*len(bccs)
        
            self._append(cypher, props, opCount)
            
        except Exception, e:
            print e
            pass    
    
        return
              
    def complete(self):
        print "Completing:"
    
        self.commit()
        tx = self.session.create_transaction()
        
        sys.stdout.write("Processing Names... ")
        cypher =  "MATCH (a:Actor) WITH a "
        cypher += "MATCH (a)-[r:Name]->() WITH a,MAX(r.count) as nmax " 
        cypher += "MATCH (a)-[r:Name]->(n:Name) WHERE r.count = nmax "
        cypher += "SET a.name=n.name"
        tx.append(cypher)
        t0 = time.time()
        tx.execute()
        t1 = time.time()
        _write_time(t1-t0)
        
        sys.stdout.write("Processing Sent Counts... ")
        tx.append("MATCH (n:Actor)-[r:Sent]->() WITH n,count(r) AS rc SET n.sent=rc")
        tx.append("MATCH (n:Actor) WHERE NOT (n)-[:Sent]->() SET n.sent=0")
        t0 = time.time()
        tx.execute()
        t1 = time.time()
        _write_time(t1-t0)
    
        sys.stdout.write("Processing TO Counts... ")
        tx.append("MATCH (n:Actor)<-[r:TO]-() WITH n,count(r) AS rc SET n.to=rc")
        tx.append("MATCH (n:Actor) WHERE NOT (n)<-[:TO]-() SET n.to=0")
        t0 = time.time()
        tx.execute()
        t1 = time.time()
        _write_time(t1-t0)
    
        sys.stdout.write("Processing CC Counts... ")
        tx.append("MATCH (n:Actor)<-[r:CC]-() WITH n,count(r) AS rc SET n.cc=rc")
        tx.append("MATCH (n:Actor) WHERE NOT (n)<-[:CC]-() SET n.cc=0")
        t0 = time.time()
        tx.execute()
        t1 = time.time()
        _write_time(t1-t0)
    
        sys.stdout.write("Processing BCC Counts... ")
        tx.append("MATCH (n:Actor)<-[r:BCC]-() WITH n,count(r) AS rc SET n.bcc=rc")
        tx.append("MATCH (n:Actor) WHERE NOT (n)<-[:BCC]-() SET n.bcc=0")
        t0 = time.time()
        tx.commit()
        t1 = time.time()
        _write_time(t1-t0)
        return
    
    def _collect_name(self, msgAddr, msgXAddr):
        
        if msgAddr is None or len(msgAddr) == 0:
            return
        
        msgEmail = str.lower(msgAddr[1])
        
        msgName = _get_decoded(msgAddr[0])
        if len(msgName) == 0:
            msgName = _get_decoded(msgXAddr)
                
        msgName = msgName.lower()
        msgName = msgName.replace(msgEmail,'').replace('()', '').replace('to:', '').replace('cc:', '')
        msgName = msgName.strip(" \"',<>").title()
        msgName = " ".join(msgName.split())
        msgName = " ".join(msgName.split(", ")[::-1])
        
        nameLen = len(msgName)
        if (nameLen > 0) and (nameLen < 100) and not (msgName == 'None'):
            names = self.names.setdefault(msgEmail, {})
            names[msgName] = names.get(msgName,0)+1

        return
    
    
def _get_decoded(strIn):
    strOut = strIn
    
    try:
        decVal = email.Header.decode_header(strIn)
        if not decVal[0][1] == None:
            strOut = unicode(decVal[0][0], decVal[0][1])
        else:
            strOut = unicode(decVal[0][0], "utf-8", errors='replace')
    except Exception, e:
        print e
        pass

    return strOut

def _write_time(dT):
    sys.stdout.write("    \t" + str(dT) + " seconds\n")
    return


    