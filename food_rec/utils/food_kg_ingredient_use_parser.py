from fractions import Fraction


class FoodKgInredientUseParser:

    unit_synonyms = {
        "cups": "cup",
        "cup": "cup",
        "c": "cup",
        "teaspoon": "tsp",
        "teaspoons": "tsp",
        "tsp": "tsp",
        "tsps": "tsp",
        "tablespoon": "tbsp",
        "tablespoons": "tbsp",
        "tbsps": "tbsp",
        "tbsp": "tbsp",
        "fl oz": "fl oz",
        "fluid ounce": "fl oz",
        "fluid ounces": "fl oz",
        "ounce, fluid": "fl oz",
        "ounces, fluid": "fl oz",
        "gal": "gallon",
        "gals": "gallon",
        "gallon": "gallon",
        "gallons": "gallon",
        "ml": "ml",
        "mls": "ml",
        "milliliter": "ml",
        "milliliters": "ml",
        "liters": "liter",
        "litre": "liter",
        "litres": "liter",
        "liter": "liter",
        "l": "liter",
        "qts": "qt",
        "quart": "qt",
        "quarts": "qt",
        "qt": "qt",
        "pint": "pint",
        "pints": "pint",
        "ping": "ping",
    }
    weight_units = {
        "g": "g",
        "gram": "g",
        "grams": "g",
        "kg": "kg",
        "kgs": "kg",
        "kilogram": "kg",
        "kilograms": "kg",
        "pound": "lb",
        "pounds": "lb",
        "lbs": "lb",
        "lb": "lb",
        "oz": "oz",
        "ounce": "oz",
        "ounces": "oz",
    }
    weight_conversion = {"lb": 453.6, "g": 1, "kg": 1000, "oz": 28.3}
    unit_conversion_dict = {
        "cup": 236.6,
        "tsp": 4.9,
        "tbsp": 14.8,
        "fl oz": 29.6,  # fluid ounces
        "gallon": 3785.4,
        "liter": 1000,
        "qt": 946.4,  # quart
        "pint": 473.2,
        "ml": 1,
        "l": 1000,
    }
    vague_measures = {"pinch", "dash", "pinches"}

    @staticmethod
    def parse_ingredient_use_quantity(quant: str, unit: str) -> float:
        """
        Parse an ingredient usage quantity and convert it into a float.
        E.g. quantity may be expressed as "1/2", which must be parsed into "0.5".
        Current considerations:
        just a number "1"
        fractions, "1/2"
        int+fractions, "4-1/2"
        erroneous: "1 4-", "2/00" (almost certainly "200"), ".2/5" (probably 2/5?)
        "1 4-" was broken off of "1 4-inch-long rosemary sprig". perhaps cases like this should assume to drop the
        second to last number of there's a -
        for cases like 2/00, maybe just return nothing

        nutrition is listed for 100g of the food

        :param quant: The raw input of the quantity, possibly string, float, or int
        :return: A float representing the gram_quantity of ingredient used
        """

        def ignore_zero_frac(s):
            # erroneous fractions with 0 or . in the denominator
            if s.find("/0") > -1 or s[-1] == ".":
                return 1
            else:
                return Fraction(s)

        if "/" in quant and "." in quant:
            # if fraction and decimal both are in, assume decimal is incorrect
            quant = quant.replace(".", " ")
        # - usually is used to show a range of quantitites, e.g. 4-5 pieces of ...
        #  so split the quant, calculate separately, and return the average.
        if "-" in quant:
            quant = quant.replace("--", "-")
            quant_parts = quant.split("-")
            final_quant = FoodKgInredientUseParser.parse_ingredient_use_quantity(
                quant=quant_parts[0].strip(), unit=unit
            ) + FoodKgInredientUseParser.parse_ingredient_use_quantity(
                quant=quant_parts[1].strip(), unit=unit
            )
            return final_quant / 2.0
        else:
            split_quant = quant.split()
            # slightly jerry-rigged method of handling when quantities are parsed incorrectly and end up with too many
            # numbers. if the last number's not a fraction less than 1, there probably was a parsing error, so ignore it.
            if len(split_quant) > 1 and ignore_zero_frac(split_quant[-1]) > 1:
                if (
                    len(split_quant[-1]) == 2
                ):  # e.g. 1/2 could be incorrectly parsed into 12.
                    if split_quant[-1][1] != "0":
                        split_quant = split_quant[:-1] + [
                            split_quant[-1][0] + "/" + split_quant[-1][1]
                        ]
                    else:
                        split_quant = split_quant[:-1]
                else:
                    split_quant = split_quant[:-1]
            try:
                if unit == "" and len(split_quant) == 1 and len(split_quant[0]) == 2:
                    # special case of common incorrect parse where missing units leads to quantities like "1/2" being
                    # parsed into "12"
                    split_quant[0] = split_quant[0][0] + "/" + split_quant[0][1]
                if len(split_quant) == 1 and "/" not in split_quant[0]:
                    quant = float(split_quant[0])
                else:
                    quant = float(sum(ignore_zero_frac(f) for f in split_quant))
                if quant > 0:
                    return quant
                else:
                    return 1
            except:
                # exception likely will occur if quantity is either empty (ie. "") or parsed incorrect (e.g. "2/00").
                # we don't really have a good way of handing this besides manually fixing the data, so just set to 1 for now
                return 1
