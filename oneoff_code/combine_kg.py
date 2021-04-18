import rdflib

g = rdflib.ConjunctiveGraph()

g.bind('np', 'http://www.nanopub.org/nschema#')
g.bind('ns1', 'urn:x-rdflib:')
g.bind('owl', 'http://www.w3.org/2002/07/owl#')
g.bind('prov', 'http://www.w3.org/ns/prov#')
g.bind('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
g.bind('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
g.bind('recipe-kb', 'http://idea.rpi.edu/heals/kb/')
g.bind('xml', 'http://www.w3.org/XML/1998/namespace')
g.bind('xsd', 'http://www.w3.org/2001/XMLSchema#')
g.bind('dc', 'http://purl.org/dc/elements/1.1/')
g.bind('obo', 'http://purl.obolibrary.org/obo/')
g.bind('oboInOwl', 'http://www.geneontology.org/formats/oboInOwl#')

g.parse('foodkg_10k/10k_foodkg.trig', format='trig')
g.parse('foodkg_100k/foodon-links.trig', format='trig')
g.parse('foodkg_100k/usda-links.trig', format='trig')
g.serialize('foodkg_10k/10k_foodkg_dataset_triples.trig', format='trig')
quit()

u = rdflib.ConjunctiveGraph()
u.parse('../data/usda.rdf', format='trig')

query_result = g.query("""
    prefix recipe-kb: <http://idea.rpi.edu/heals/kb/>
    prefix simple-sub: <http://idea.rpi.edu/heals/simplesub/>
    SELECT ?o
    WHERE {
        ?s <http://www.w3.org/2002/07/owl#equivalentClass> ?o.
        filter (strstarts(str(?o), "http://idea.rpi.edu/heals/kb/usda#")).
    }
    """)

food_ids = []
for res in query_result:
    food_ids.append(int(res[0][len("http://idea.rpi.edu/heals/kb/usda#"):]))
    #print(int(res[0][len("http://idea.rpi.edu/heals/kb/usda#"):]))
print("---")

#        ?s a <http://dbpedia.org/resource/Food>.
prepq = rdflib.plugins.sparql.prepareQuery("""
    prefix recipe-kb: <http://idea.rpi.edu/heals/kb/>
    prefix simple-sub: <http://idea.rpi.edu/heals/simplesub/>
    prefix sio: <http://semanticscience.org/resource/>
    SELECT ?s ?p ?o
    WHERE {
        ?s sio:hasValue ?id.
        ?s sio:hasValue ?o.
        ?s ?p ?id.
    }
    """)
id_triple_results = []
for id in food_ids:
    #print(id)
    query_result = u.query(prepq,
                           initBindings={'?id': rdflib.term.Literal(id, datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#integer'))})
    #print(len(query_result))
    for res in query_result:
        id_triple_results.append(res)
print('---')

used_contexts = []
for res in id_triple_results:
    used_contexts.append(list(u.contexts(triple=res))[0])
unused_contexts = []
for c in u.contexts():
    if c not in used_contexts:
        unused_contexts.append(c)
print("===")
print(len(used_contexts))
print(len(set(used_contexts)))
print(len(unused_contexts))
print(len(set(unused_contexts)))
print("-----")
print(len(u))
for c in unused_contexts:
    u.remove_context(c)
print(len(u))
u.serialize('foodkg_10k/10k_usda_dataset.rdf', format='trig')
