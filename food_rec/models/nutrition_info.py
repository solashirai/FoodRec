from typing import Dict
from rdflib.term import URIRef
from typing import Optional, NamedTuple
import json


class NutritionInfo(NamedTuple):
    """
    Class to store nutrition information from USDA foods.

    All fields are optional and have defaults, since not all usda foods are guaranteed to contain the info.
    """

    # for documentation on nutrition info https://data.nal.usda.gov/system/files/sr27_doc.pdf
    # nutrients seem to be showing as amount present in 100g of the food product, so no normalization needed
    shrt__desc: Optional[str] = None
    gm_wt__desc1: Optional[str] = None
    gm_wt__desc2: Optional[str] = None
    folate__tot_micro_g: Optional[float] = 0
    vit__c_mg: Optional[float] = 0
    vit__b6_mg: Optional[float] = 0
    food__folate_micro_g: Optional[float] = 0
    thiamin_mg: Optional[float] = 0
    phosphorus_mg: Optional[float] = 0
    cholestrl_mg: Optional[float] = 0
    lipid__tot_g: Optional[float] = 0
    gm_wt_1: Optional[float] = 0
    folate__d_f_e_micro_g: Optional[float] = 0
    sodium_mg: Optional[float] = 0
    alpha__carot_micro_g: Optional[float] = 0
    ash_g: Optional[float] = 0
    retinol_micro_g: Optional[float] = 0
    beta__crypt_micro_g: Optional[float] = 0
    f_a__sat_g: Optional[float] = 0
    vit__a__r_a_e: Optional[float] = 0
    carbohydrt_g: Optional[float] = 0
    vit__b12_micro_g: Optional[float] = 0
    gm_wt_2: Optional[float] = 0
    lut__zea__micro_g: Optional[float] = 0
    choline__tot__mg: Optional[float] = 0
    protein_g: Optional[float] = 0
    water_g: Optional[float] = 0
    niacin_mg: Optional[float] = 0
    magnesium_mg: Optional[float] = 0
    f_a__mono_g: Optional[float] = 0
    iron_mg: Optional[float] = 0
    beta__carot_micro_g: Optional[float] = 0
    manganese_mg: Optional[float] = 0
    vit__d__i_u: Optional[float] = 0
    refuse__pct: Optional[float] = 0
    vit__k_micro_g: Optional[float] = 0
    fiber__t_d_g: Optional[float] = 0
    potassium_mg: Optional[float] = 0
    selenium_micro_g: Optional[float] = 0
    lycopene_micro_g: Optional[float] = 0
    copper_mg: Optional[float] = 0
    riboflavin_mg: Optional[float] = 0
    calcium_mg: Optional[float] = 0
    vit__d_micro_g: Optional[float] = 0
    panto__acid_mg: Optional[float] = 0
    zinc_mg: Optional[float] = 0
    sugar__tot_g: Optional[float] = 0
    vit__e_mg: Optional[float] = 0
    energ__kcal: Optional[float] = 0
    f_a__poly_g: Optional[float] = 0
    folic__acid_micro_g: Optional[float] = 0
    vit__a__i_u: Optional[float] = 0
