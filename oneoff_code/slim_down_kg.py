import rdflib
import random

# 1-off script for cleaning up data from running FoodKG code to generate KG. mainly getting rid of prov/nanopub things

input = 'foodkg_100k/foodkg-core.trig'
output = 'foodkg_10k/foodkg-food_kg.trig'

g = rdflib.ConjunctiveGraph()

print("parsing trig files")
g.parse(input, format='trig')
print("loading completed")
print(len(g))

g.remove((None, rdflib.term.URIRef('http://www.w3.org/ns/prov#generatedAtTime'), None))
print("r1")
g.remove((None, rdflib.term.URIRef('http://www.nanopub.org/nschema#hasProvenance'), None))
print("r2")
g.remove((None, rdflib.term.URIRef('http://www.nanopub.org/nschema#hasPublicationInfo'), None))
print("r3")
g.remove((None, rdflib.term.URIRef('http://www.nanopub.org/nschema#hasAssertion'), None))
print("r4")
g.remove((None, None, rdflib.term.URIRef('http://www.nanopub.org/nschema#Nanopublication')))
print("r5")
g.remove((None, rdflib.term.URIRef('http://hadatac.org/ont/hasco#hasPosition'), None))
print("r6")

q = rdflib.ConjunctiveGraph()
q.bind('np', 'http://www.nanopub.org/nschema#')
q.bind('ns1', 'urn:x-rdflib:')
q.bind('owl', 'http://www.w3.org/2002/07/owl#')
q.bind('prov', 'http://www.w3.org/ns/prov#')
q.bind('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
q.bind('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
q.bind('recipe-kb', 'http://idea.rpi.edu/heals/kb/')
q.bind('xml', 'http://www.w3.org/XML/1998/namespace')
q.bind('xsd', 'http://www.w3.org/2001/XMLSchema#')

for ((s,p,o)) in g:
    q.add((s,p,o))

q.remove((None, rdflib.term.URIRef('http://www.w3.org/ns/prov#wasGeneratedBy'), None))

q.remove((None, rdflib.term.URIRef('http://www.w3.org/ns/prov#wasDerivedFrom'), None))
print(len(q))

# q.serialize(destination=output, format='trig')

triplist = set()
keeplist = set()
removelist = set()
for (s,p,o) in g.triples((None, None, rdflib.term.URIRef('http://idea.rpi.edu/heals/kb/recipe'))):
    triplist.add((s,p,o))
keeplist = set(random.sample(triplist, k=10000))
removelist = triplist - keeplist
len(removelist)

for rem_trip in removelist:
    rem_s = rem_trip[0]
    for (s,p,o) in q.triples((rem_s, rdflib.term.URIRef('http://idea.rpi.edu/heals/kb/uses'), None)):
        q.remove((s,None, None))
        q.remove((None, None, s))
        q.remove((None, None, o))
        q.remove((o, None, None))

print(len(q))
q.serialize(destination=output, format='trig')