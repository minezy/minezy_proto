import sys
from py2neo import neo4j, node, rel
import neo4j_conn

    
def find_cliques1(rootAddr):
    query_str = "MATCH (n:Contact)-->(:Email)-[:TO]->(m:Contact) "
    query_str += "WHERE (m)-[:SENT]->() "
    query_str += "AND not n.email = '" + rootAddr + "' AND NOT m.email = '" + rootAddr + "'  "
    #query_str += "WHERE not n.email = '" + rootAddr + "' "
    query_str += "WITH n, collect(distinct id(m)) AS mc WHERE length(mc) > 2 and length(mc) < 11 "
    query_str += "RETURN id(n),mc AS mc ORDER BY length(mc) ASC "
    
    tx = neo4j_conn.g_session.create_transaction()
    tx.append(query_str)
    results = tx.commit()
    
    cliques = []
    merge_counts = []
    
    for record in results[0]:
        frm = int(record[0])
        tset = set(record[1])
            
        if len(tset) > 2:
            for i, cset in enumerate(cliques):
                #if cset >= tset or tset >= cset:
                overlap = len(cset.intersection(tset))
                lentset = len(tset)
                if overlap >= ((lentset+1)/2):
                    cset |= tset
                    merge_counts[i] += 1
                    break
            else:
                cliques.append(tset)
                merge_counts.append(1)

    sorted_cliques = [x for (y,x) in sorted(zip(merge_counts,cliques), reverse=True)]
    return sorted_cliques


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
    cliques = find_cliques1(sys.argv[1])
    
    for i, cset in enumerate(cliques):
        print "Clique (" + str(i+1) + '/' + str(len(cliques)) + "): " + str(len(cset))
        for c in cset:
            tx.append("MATCH n WHERE id(n)={id} RETURN n", { 'id':c })
            results = tx.execute()
            
            for record in results[0]:
                n = record[0]
                print n['email'] + '\t\t' + unicode(n['name'])
        print
    print "All Done"
    
    
