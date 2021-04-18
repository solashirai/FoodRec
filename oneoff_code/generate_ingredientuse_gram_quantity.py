import rdflib
import re
from frex.stores import LocalGraph
from food_rec.models import *
from fractions import Fraction
from food_rec.services.food import LocalGraphFoodKgQueryService
from food_rec.utils import FoodKgInredientUseParser
from food_rec.utils.path import *
from food_rec.services import FoodKgQueryService
from food_rec.services.exceptions import MalformedIngredientException, IngredientUseNotFoundException


g_save_file = (DATA_DIR / '5k_recipes' / 'recipes-1-addgrams.ttl').resolve()
g_file = (DATA_DIR /  '5k_recipes' / 'recipes-1.ttl').resolve()
links_file = (DATA_DIR /  '5k_recipes' / 'usda-links-1.ttl').resolve()
usda = (DATA_DIR / 'simplified_usda.ttl').resolve()

fkg = LocalGraphFoodKgQueryService(file_paths=(g_file, links_file, usda))

print('files loaded')


usda_ing_density_dict = {}
usda_ing_default_weight_dict = {}
no_dense_match=[]



def n_inguri_find_gmwt_match(usda_uri, usda_ing_density_dict, usda_ing_default_weight_dict):

    if usda_uri not in usda_ing_density_dict.keys():
        nut = fkg.get_usda_nutrition_by_uri(usda_food_uri=usda_uri)

        if nut.gm_wt__desc1:
            d1 = nut.gm_wt__desc1.replace("-", " ").replace("(", " ").replace(")", " ").replace(
                ",", "").split(" ")
        else:
            d1 = ''
        # special case to fix when quantities start as ".5" instead of "0.5"
        if d1 and d1[0] and d1[0][0] == ".":
            d1[0] = "0"+d1[0]

        if nut.gm_wt__desc2:
            d2 = nut.gm_wt__desc2.replace("-", " ").replace("(", " ").replace(")", " ").replace(
                ",", "").split(" ")
        else:
            d2 = ''

        if d2 and d2[0] and d2[0][0] == ".":
            d2[0] = "0"+d1[0]

        # special case that i'm lazily putting here because it's pretty edge case...
        if d1 == ['1', 'cubic', 'inch']:
            d1 = ['16.4', 'ml']
        elif d2 == ['1', 'cubic', 'inch']:
            d2 = ['16.4', 'ml']

        got_density = False
        amount = 0
        convert_amount = 0
        new_default_wt = 0
        for i in range(len(d1)):
            if FoodKgInredientUseParser.unit_synonyms.get(d1[i], 0):
                # edge case for fl oz
                if d1[i - 1] in {'fl', 'fluid'}:
                    amount = FoodKgInredientUseParser.parse_ingredient_use_quantity(d1[i - 2], unit='aaa')
                    convert_amount = float(nut.gm_wt_1) / (amount * FoodKgInredientUseParser.unit_conversion_dict[
                        FoodKgInredientUseParser.unit_synonyms[d1[i-1]+" "+d1[i]]])
                else:
                    amount = FoodKgInredientUseParser.parse_ingredient_use_quantity(d1[i - 1], unit='aaa')
                    # calculate density as g/ml
                    convert_amount = float(nut.gm_wt_1) / (amount * FoodKgInredientUseParser.unit_conversion_dict[
                        FoodKgInredientUseParser.unit_synonyms[d1[i]]])
                got_density = True
                break

        if not got_density:
            new_default_wt = nut.gm_wt_1

        if convert_amount == 0:  # special case, if convert amount is 0 which occurs for some small measurements
            for i in range(len(d2)):
                if FoodKgInredientUseParser.unit_synonyms.get(d2[i], 0):
                    # edge case for fl oz
                    if d2[i - 1] in {'fl', 'fluid'}:
                        amount = FoodKgInredientUseParser.parse_ingredient_use_quantity(d2[i - 2], unit='aaa')
                        convert_amount = float(nut.gm_wt_1) / (amount * FoodKgInredientUseParser.unit_conversion_dict[
                            FoodKgInredientUseParser.unit_synonyms[d2[i-1]+" "+d2[i]]])
                    else:
                        amount = FoodKgInredientUseParser.parse_ingredient_use_quantity(d2[i - 1], unit='aaa')
                        # calculate density as g/ml
                        convert_amount = float(nut.gm_wt_2) / (amount * FoodKgInredientUseParser.unit_conversion_dict[
                            FoodKgInredientUseParser.unit_synonyms[d2[i]]])
                    # print(d2)
                    got_density = True
                    if not new_default_wt:
                        new_default_wt = nut.gm_wt_1
                    break

        if got_density and not new_default_wt:
            new_default_wt = nut.gm_wt_2
        if not new_default_wt:
            new_default_wt = 100
        usda_ing_default_weight_dict[usda_uri] = new_default_wt
        if usda_uri == rdflib.URIRef('http://idea.rpi.edu/heals/kb/usda#11352'):
            print("potato: ", new_default_wt)

        if not got_density:
            no_dense_match.append(nut.shrt__desc)
            # no gramweights specified, use 1g/ml as is default for nutrition values
            convert_amount = 1
            # # no density found, so set a default gram weight
            # if d1 == d2 == ['']:
            #     # no gramweights specified, use 1g/ml as is default for nutrition values
            #     convert_amount = 1
            #
            # # otherise use gmwt 1 as the default weight
            # elif d1[0].isdigit():
            #     convert_amount = float(nut.gm_wt_1) / int(d1[0])
            # else:
            #     # print(d1)
            #     convert_amount = float(nut.gm_wt_1)
        usda_ing_density_dict[usda_uri] = (got_density, convert_amount)


        if len(usda_ing_density_dict.keys()) % 50 == 0:
            print(len(usda_ing_density_dict.keys()))
        elif len(usda_ing_density_dict.keys()) < 10:
            print(len(usda_ing_density_dict.keys()))


ing_q = fkg.queryable.graph.query("""
prefix usda-ontology: <http://idea.rpi.edu/heals/kb/usda-ontology#>
    SELECT DISTINCT ?usda_uri
    WHERE {{
        ?usda_uri a usda-ontology:Food
    }}
""")
for ing in ing_q:
    n_inguri_find_gmwt_match(ing.usda_uri, usda_ing_density_dict, usda_ing_default_weight_dict)

print('usda food keys: ', len(usda_ing_density_dict.keys()))
print('usda foods with no density calculated: ', len(no_dense_match))
# use density/default amounts to generate gram weights of each ingredientuse

ing_use_q = fkg.queryable.graph.query("""
prefix recipe-kb: <http://idea.rpi.edu/heals/kb/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?inguse
    WHERE {{
        ?inguse a recipe-kb:ingredientuse
    }}
""")

inguse_gram_units = {}

no_cont = 0
has_cont = 0
vol_to_vol = 0
vol_to_def = 0
na_to_na = 0
na_to_fake_def = 0
na_to_def = 0
wt_in_use = 0
ing_counter = 0
pinch_or_dash = 0
inguri_to_ing = dict()
for res in ing_use_q:
    inguse_uri = res.inguse
    if inguse_gram_units.get(inguse_uri, 0):
        continue

    #ig = fkg.get_ingredient_use(ingredient_use_uri=inguse_uri)

    #messy workaround to get ingredientuse
    find_ingredient_query = fkg.queryable.graph.query("""
    prefix recipe-kb: <http://idea.rpi.edu/heals/kb/>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
SELECT ?ing ?quant ?unit ?comment
WHERE {{
    {0} recipe-kb:ing_name ?ing;
        recipe-kb:ing_quantity ?quant;
    OPTIONAL {{
        {0} recipe-kb:ing_unit ?unit.
        }}
    OPTIONAL {{
        {0} rdfs:comment ?comment
    }}
}}
    """.format(inguse_uri.n3()))
    if find_ingredient_query:
        # some ingredientuse have multiple values for gram_quantity/units.
        # the first entry is probably the correct one here, but just grabbing all results can give incorrect
        # gram_quantity/unit combinations, e.g. "2 cups", "2 tablespoon", "1/2 cups", "1/2 tablespoon"
        for res in find_ingredient_query:
            ing = res.ing
            quant = res.quant.value
            if res.unit:
                unit = res.unit.value
                unit = unit.replace(".", "")
            else:
                unit = ''
                # this should be fixed in foodkg code now
                if res.comment:
                    if " g " in res.comment.value:
                        unit = 'g'
                    elif " kg " in res.comment.value:
                        unit = 'kg'
                    elif ' lb ' in res.comment.value:
                        unit = 'lb'
            if res.comment:
                cmt = res.comment.value
            else:
                cmt = ''
            quant = FoodKgInredientUseParser.parse_ingredient_use_quantity(quant=quant, unit=unit)
    else:
        continue
    ingredient = inguri_to_ing.get(ing, '')
    if not ingredient:
        ingredient = fkg.get_ingredient_by_uri(ing_uri=ing)
        inguri_to_ing[ing] = ingredient

    # try:
    #     ing_use_obj = fkg.get_ingredient_use_by_uri(ing_use_uri=inguse_uri)
    # except IngredientUseNotFoundException:
    #     continue
    # ingredient = ing_use_obj.ingredient

    if not ingredient.usda_equiv:
        continue
    context_id, nutrition_inf = ingredient.usda_equiv, ingredient.nutrition_info
    if context_id is None:
        no_cont += 1
    else:
        has_cont += 1


    # print(inguse_uri)
    usda_l_res = usda_ing_density_dict[ingredient.usda_equiv]
    unt = unit
    if FoodKgInredientUseParser.weight_units.get(unt, 0):  # inguse is in units of mass
        inguse_gram_units[inguse_uri] = FoodKgInredientUseParser.weight_conversion[
                                            FoodKgInredientUseParser.weight_units[unt]] * quant
        wt_in_use += 1
    elif FoodKgInredientUseParser.unit_synonyms.get(unt, 0):  # inguse uses volume
        if (usda_l_res[0]):  # got density
            inguse_gram_units[inguse_uri] = FoodKgInredientUseParser.unit_conversion_dict[
                                                FoodKgInredientUseParser.unit_synonyms[unt]] * usda_l_res[1] *\
                                            quant
            vol_to_vol += 1
        else:  # didn't get density, use default density
            inguse_gram_units[inguse_uri] = usda_l_res[1] * quant
            vol_to_def += 1
    else:  # units in inguse are not volume or weight, check for match
        if cmt:
            paren_content_search = re.search(r'\((.*?)\)', cmt)
            if paren_content_search:
                # only use parenthesis contents if its seen early on in the comment.
                #  e.g. "1 (8 ounce) can of ..." as opposed to instances like "4 chicken thighs (about 1.5 lb)"
                if cmt.find("(") < len(cmt)/3:
                    paren_content = paren_content_search.group(1).split(" ")
                    if any([content in FoodKgInredientUseParser.weight_units.keys() for content in paren_content]):
                        comment_unit = ''
                        comment_quant = 0.0
                        for token in paren_content:
                            try:
                                # print(Fraction(token))
                                comment_quant += Fraction(token)
                            except:
                                pass
                            if token in FoodKgInredientUseParser.weight_units.keys():
                                comment_unit = FoodKgInredientUseParser.weight_units[token]


                        inguse_gram_units[inguse_uri] = FoodKgInredientUseParser.weight_conversion[comment_unit] * comment_quant * quant
                        wt_in_use += 1
                        continue
        basic_lemmas = {'cans': 'can', 'packages': 'package', 'slices': 'slice'}
        unt = basic_lemmas.get(unt, unt)

        nut = ingredient.nutrition_info
        if nut.gm_wt__desc1:
            d1 = nut.gm_wt__desc1.replace(".", "").replace("-", " ").replace("(", " ").replace(")", " ").replace(
                ",", "").split(" ")
        else:
            d1 = ''
        if nut.gm_wt__desc2:
            d2 = nut.gm_wt__desc2.replace(".", "").replace("-", " ").replace("(", " ").replace(")", " ").replace(
                ",", "").split(" ")
        else:
            d2 = ''

        # use gmwt 1 as the default weight when there is no units, or 100g if gmwt 1 doesnt exist
        default_weight = usda_ing_default_weight_dict[ingredient.usda_equiv]

        if unt == '':
            inguse_gram_units[inguse_uri] = default_weight * quant
            na_to_def += 1
        elif unt == 'pinch' or unt == 'pinches' or unt == 'dash':
            inguse_gram_units[inguse_uri] = 0.3  # assuming a pinch is 0.3 grams
            pinch_or_dash += 1
        elif unt in d1:
            inguse_gram_units[inguse_uri] = nut.gm_wt_1 * quant
            na_to_na += 1
        elif unt in d2:
            inguse_gram_units[inguse_uri] = nut.gm_wt_2 * quant
            na_to_na += 1
        else:
            # no measurement match, use default value
            inguse_gram_units[inguse_uri] = default_weight * quant
            na_to_fake_def += 1

    ing_counter += 1
    if ing_counter % 500 == 0:
        print(ing_counter)

print('resulting counts of situations')
print('vol. in foodkg, vol in usda: ',vol_to_vol)
print('vol. in foodkg to default value: ', vol_to_def)
print('foodkg quant in usda gmwt description:', na_to_na)
print('no explicit foodkg quant, use default value in usda: ', na_to_def)
print('foodkg quant not matched to any gmwt in usda, use default value in usda: ',na_to_fake_def)
print('foodkg amount contains weight: ', wt_in_use)
print('foodkg amount pinch or dash: ',pinch_or_dash)


print("has cont vs no cont: ", has_cont, " | ", no_cont)
#---

# write and save results
#food_kg_test_dataset.trig'#
g = rdflib.Graph()
g.parse(str(g_file), format='ttl')

g.remove((None, rdflib.term.URIRef('http://idea.rpi.edu/heals/kb/ing_computed_gram_quantity'), None))
for k in inguse_gram_units.keys():
    g.add((k, rdflib.term.URIRef('http://idea.rpi.edu/heals/kb/ing_computed_gram_quantity'),
           rdflib.Literal(round(inguse_gram_units[k], 6), datatype=rdflib.XSD.float)))
g.serialize(str(g_save_file), format='ttl')
