import sys
from pageRank import pageRank, pageRank2
from py2neo import neo4j, node, rel
import neo4j_conn

nodeToIndex = {}
indexToNode = {}

def nodemap(nodeId):
    global nodeToIndex
    global indexToNode
    
    index = nodeToIndex.setdefault(nodeId, len(nodeToIndex))
    indexToNode[index] = nodeId
    return index
    
def create_email_links():
    query = neo4j.CypherQuery(neo4j_conn.g_graph,
#        "MATCH (n:Contact)-->(:Email)-[r:TO|CC]->(m:Contact) return id(n),type(r),collect(id(m)) order by id(n)"
        "MATCH (n:Contact)-->(:Email)-[r:TO|CC]->(m:Contact) where not n.email = 'paul@paulquinn.com' and not m.email = 'paul@paulquinn.com'  return id(n),type(r),collect(id(m)) order by id(n)"
        )
    
 
#    query = neo4j.CypherQuery(neo4j_conn.g_graph,
#        "MATCH (n:Contact)-->(:Email)-[r:TO|CC]->(m:Contact) return id(m),collect(id(n))"
#        )
           
    linksTo = []
    linksCc = []
    for record in query.stream():
        frm = int(record[0])
        r = str(record[1])
        to = [t for t in record[2] if t != frm]
        
        frmIdx = nodemap(frm)
        toIdx = [nodemap(t) for t in to]
        if len(toIdx) > 0:
            extend = max(frmIdx - len(linksTo), max(toIdx) - len(linksTo)) + 1
            for i in range(extend):
                linksTo.append([])
            extend = max(frmIdx - len(linksCc), max(toIdx) - len(linksCc)) + 1
            for i in range(extend):
                linksCc.append([])
                
            if r == 'TO':
                linksTo[frmIdx] = toIdx
            else:
                linksCc[frmIdx] = toIdx
        
    return linksTo,linksCc
        
    
if __name__ == '__main__':
    if len(sys.argv) != 1:
        print "Usage: " + sys.argv[0]
        exit(1)

    neo4j_conn.connect()

    print "Loading all email links..."
    linksTo, linksCc = create_email_links()
    
    print "Calculating PageRank..."
#    pr = pageRank(links, alpha=0.85, convergence=0.00001, checkSteps=10)
    pr = pageRank2(linksTo, linksCc, alpha=1.0, convergence=0.00001, checkSteps=10)
    sum = 0
    for i in range(len(pr)):
        print i, "=", pr[i]
        sum = sum + pr[i]
    print "s = " + str(sum)
    
    print "Storing ranks per Contact..."
    batch = neo4j.WriteBatch(neo4j_conn.g_graph)
    for i in range(len(pr)):
        n = neo4j_conn.g_graph.node(indexToNode[i])
        if n is not None:
            batch.set_property(n, 'rank', pr[i])
            batch.set_property(n, 'rankIdx', i)
    batch.submit()
    print "All Done"
    
    

