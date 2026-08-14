from neo4j import GraphDatabase
uri = 'neo4j://127.0.0.1:7687'
auth = ('neo4j', 'abcd1234')
with GraphDatabase.driver(uri, auth=auth) as driver:
    with driver.session(database='kb-hops') as session:
        print('documents', session.run('MATCH (d:Document) RETURN count(d) AS count').single()['count'])
        print('document_relations', session.run('MATCH (:Document)-[r]->(:Document) RETURN count(r) AS count').single()['count'])
        print('chunks', session.run('MATCH (c:Chunk) RETURN count(c) AS count').single()['count'])
        print('parent_relations', session.run('MATCH ()-[r:PARENT_OF]->() RETURN count(r) AS count').single()['count'])
        print('next_relations', session.run('MATCH ()-[r:NEXT]->() RETURN count(r) AS count').single()['count'])
