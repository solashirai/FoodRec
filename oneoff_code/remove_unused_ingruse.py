import rdflib


g.query("""
prefix recipe-kb: <http://idea.rpi.edu/heals/kb/>
SELECT ?unused
WHERE {
    ?unused a recipe-kb:ingredientuse .
    MINUS { ?anything recipe-kb:uses ?unused .}
}""")