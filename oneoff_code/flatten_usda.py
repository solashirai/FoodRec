import rdflib
from rdflib.namespace import Namespace
import stringcase

g = rdflib.ConjunctiveGraph()
g.parse('../data/usda_test_dataset.trig', format='trig')
# g.parse('../data/usda.rdf', format='trig')

new_g = rdflib.Graph()
print(len(g))
hasValue = rdflib.term.URIRef('http://semanticscience.org/resource/hasValue')
sio_ns = Namespace('http://semanticscience.org/resource/')
hasAttrLink = sio_ns['hasAttribute']
isAttr = sio_ns['Attribute']
rdfstype = rdflib.namespace.RDF['type']
rdfslabel = rdflib.namespace.RDFS['label']
usda_kb = Namespace('http://idea.rpi.edu/heals/kb/usda#')
usda_onto = Namespace('http://idea.rpi.edu/heals/kb/usda-ontology#')
new_g.bind('usda-kb', usda_kb)
new_g.bind('usda-ontology', usda_onto)
new_g.bind('sio', sio_ns)
first_ss = None

attribute_types = []

quer = g.query("""
SELECT DISTINCT ?o
WHERE {
?s a ?o.
FILTER ( strstarts(str(?o), "http://idea.rpi.edu/heals/kb/usda#") )
}
""")
old_to_new_attributes = dict()
for res in quer:
    attribute_original = res.o
    if attribute_original == usda_kb['id']:
        continue
    # new_attribute = rdflib.URIRef(attribute_original[:34]+"has_"+attribute_original[34:])
    new_attribute = usda_onto[stringcase.camelcase(attribute_original[34:]).replace("_", "")]

    new_g.add((new_attribute, rdfstype, sio_ns['Attribute']))

    attr_label = g.query("""
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?o
    WHERE {{
    ?s a {0};
      rdfs:label ?o.
    }}
    """.format(attribute_original.n3()))
    for res in attr_label:
        print(res.o)
        # special case for description attribute, because the USDA data has errors in how its labeled
        if new_attribute == usda_onto['description']:
            if res.o.value != "Shrt Desc":
                continue
        new_g.add((new_attribute, rdfslabel, res.o))
    #else:
        # special case for description attribute, because the USDA data has errors in how its labeled
        # new_g.add((new_attribute, rdfslabel, "Shrt Desc"))

    attr_units = g.query("""
    prefix sio: <http://semanticscience.org/resource/> 
    SELECT DISTINCT ?o
    WHERE {{
    ?s a {0};
     sio:hasUnit ?o.
    }}
    """.format(attribute_original.n3()))
    for res in attr_units:
        new_g.add((new_attribute, sio_ns['hasUnit'], res.o))

    old_to_new_attributes[attribute_original] = new_attribute

context_to_id = dict()
for quad in g.quads((None, None, rdflib.term.URIRef('http://idea.rpi.edu/heals/kb/usda#id'), None)):
    doneonce = False
    for quad_2 in g.quads((quad[0], hasValue, None, None)):
        if doneonce:
            print("!!?!?!?!")
        target_id = usda_kb[quad_2[2].zfill(5)]
        # print(usda_kb[target_id])
        context_to_id[quad_2[3].identifier] = target_id
        new_g.add((target_id, rdfstype, usda_onto['Food']))

print('number of contexts: ', len(context_to_id.keys()))

counter = 0
for ctx in context_to_id.keys():
    target_id =  context_to_id[ctx]
    if not target_id:
        continue
    counter += 1
    if counter % 50 == 0:
        print(counter)
    subgraph = g.get_context(identifier=ctx)

    for old_att in old_to_new_attributes.keys():

        for q in subgraph.triples((None, None, old_att)):
            target = q[0]
            for val_quad in subgraph.triples((target, sio_ns['hasValue'], None)):
                new_g.add((target_id, old_to_new_attributes[old_att], val_quad[2]))
        # if q[1] == rdflib.term.URIRef('http://semanticscience.org/resource/isAttributeOf'):
        #     continue
        # new_g.add((q[0], q[1], q[2]))
        # new_g.add((target_id, hasAttrLink, q[0]))


new_g.serialize('simplified_usda.ttl', format='ttl')