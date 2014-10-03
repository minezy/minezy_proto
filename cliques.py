import sys
from py2neo import neo4j, node, rel
import neo4j_conn

    
def find_cliques(rootAddr):
    query = neo4j.CypherQuery(neo4j_conn.g_graph,
        "MATCH (n:Contact)-->(:Email)-->(m:Contact) "
        "WHERE (m)-[:Sent]->() "
#        "WHERE not n.email = '" + rootAddr + "' and not m.email = '" + rootAddr + "'  "
#        "WHERE not n.email = '" + rootAddr + "' "
        "WITH n, collect(distinct id(m)) as mc "
        "RETURN id(n),mc as mc order by length(mc)"
        )
    
    cliques = []
    
    for record in results[0]:
        frm = int(record[0])
        tset = set(record[1])
            
        if len(tset) > 2:
            for cset in cliques:
                #if cset >= tset or tset >= cset:
                overlap = len(cset.intersection(tset))
                lentset = len(tset)
                if overlap >= ((lentset+1)/2):
                    cset |= tset
                    break
            else:
                cliques.append(tset)

    return cliques


def find_cliques2(rootAddr):
    query_str = "MATCH (n:Contact)-->(e:Email)-->(m:Contact) "
    query_str += "RETURN id(n),id(e),collect(id(m)) "
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(query_str)
    results = tx.commit()
    
    cliques = []
    
    for record in results[0]:
        frm = int(record[0])
        tset = set(record[2])
            
        if len(tset) > 2:
            for cset in cliques:
                #if cset >= tset or tset >= cset:
                #overlap = len(cset.intersection(tset))
                #lenTset = len(tset)
                if cset >= tset:
                    break
                if tset >= cset:
                    tset -= cset 
            else:
                if len(tset) > 2:
                    cliques.append(tset)

    for i, cG in enumerate(cliques):
        popset = []
        for j, cL in enumerate(cliques):
            if not i == j:
                if cG >= cL:
                    popset.append(j)
                    
        popset.sort(reverse=True)
        for p in popset:
            cliques.pop(p)
                
    return cliques
    
def find_cliques3(rootAddr):
    query_str = "MATCH (n:Contact)-->(e:Email)-->(m:Contact) "
    query_str += "WHERE m-->()-->n "
    query_str += "RETURN id(n),id(e),collect(id(m)) "
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(query_str)
    results = tx.commit()
    
    cliques = []
    
    for record in results[0]:
        frm = int(record[0])
        tset = set(record[2])
            
        if len(tset) > 2:
            for cset in cliques:
                #if cset >= tset or tset >= cset:
                #overlap = len(cset.intersection(tset))
                #lenTset = len(tset)
                if cset >= tset:
                    break
                if tset >= cset:
                    tset -= cset 
            else:
                if len(tset) > 2:
                    cliques.append(tset)

    for i, cG in enumerate(cliques):
        popset = []
        for j, cL in enumerate(cliques):
            if not i == j:
                if cG >= cL:
                    popset.append(j)
                    
        popset.sort(reverse=True)
        for p in popset:
            cliques.pop(p)
                
    return cliques


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " <root_email>"
        exit(1)

    neo4j_conn.connect()
    tx = neo4j_conn.g_session.create_transaction()

    print "Finding all cliques..."
    cliques = find_cliques3(sys.argv[1])
    
    for i, cset in enumerate(cliques):
        print "Clique (" + str(i+1) + '/' + str(len(cliques)) + "): " + str(len(cset))
        for c in cset:
            tx.append("MATCH n WHERE id(n)={id} RETURN n", { 'id':c })
            results = tx.execute()
            
            for record in results[0]:
                n = record[0]
                print n['email'] + '\t\t' + str(n['name'])
        print
    print "All Done"
    
    
