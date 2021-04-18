import rdflib
import random
import spacy
from collections import defaultdict

# 1-off script for fixing ingredients that are listed as separate things because of lemmatization

input_file = '../data/10k_foodkg_dataset_triples.trig'#'../data/food_kg_test_dataset.trig'#'../data/smaller_foodkg_dataset_triples.trig'

output_file = input_file# = 'foodkg_10k/foodkg-food_kg.trig'

nlp = spacy.load('en_core_web_lg')

g = rdflib.Graph()
g.parse(input_file, format='trig')


ing_quer = g.query("""
prefix kb: <http://idea.rpi.edu/heals/kb/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?ingr ?lab
WHERE {
?ingr a kb:ingredientname;
    rdfs:label ?lab.
}
""")
print(len(ing_quer))

bad_dict = defaultdict(list)
unchanged = {}
for i in ing_quer:
    words = nlp(i.lab.value)
    lem = " ".join([w.lemma_ for w in words])
    bad_dict[lem].append(i.ingr)
    if i.lab.value == lem:
        unchanged[lem] = i.ingr

print('bd:',len(bad_dict.keys()))
for k in bad_dict.keys():
    if len(bad_dict[k]) > 1:
        print(k)
        if k in unchanged.keys():
            correct_ing = unchanged[k]
            incorrect = bad_dict[k]
            incorrect.remove(correct_ing)
            for inc_ing in incorrect:
                for s,p,o in g.triples((None, None, inc_ing)):
                    g.remove((s, p, o))
                    g.add((s, p, correct_ing))
                g.remove((inc_ing, None, None))
        else:
            print(bad_dict[k])
            good_choice = input("select index to keep")
            good_choice = int(good_choice)
            if good_choice >= 0:
                correct_ing = bad_dict[k][good_choice]
                incorrect = bad_dict[k]
                incorrect.remove(correct_ing)
                for inc_ing in incorrect:
                    for s, p, o in g.triples((None, None, inc_ing)):
                        g.remove((s, p, o))
                        g.add((s, p, correct_ing))
                    g.remove((inc_ing, None, None))
if len(g) > 0:
    g.serialize(destination=output_file, format='trig')
