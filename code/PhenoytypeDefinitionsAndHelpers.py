import numpy as np
import re
import os

path = ""
def getfile(x):
    return(os.path.join(path,x))

make_regex = lambda x: re.compile("|".join(x))


chf_icd09 = ["(428.)", "(39891)", "(402[019]1)","(404[019][13])", "(425[456789])"]
chf_icd10 = ["(I099)", "(I110)", "(I13[02])", "(I255)", "(I42[056789])", "(I43.)", "(I50.)"]

mi_icd09  = ["(410.)", "(412)"]
mi_icd10  = ["(I21.)", "(I22.)"]

stroke_icd09 = ["(434)", "(433.1)","(V1254)"]
stroke_icd10 = ["(I6[123456].)"]

ckd_icd09 = ["(585)", "(585[0123456789])"]
ckd_icd10 = ["(N18[1234569])"]

ra_icd09 = ["(714[0123])"]
ra_icd10 = ["M06[089]", "M05[0123456789]"]

dia_t1_icd09 = ["(250[0123456789][139])", "(2500)", "(25000)", "(250)"]
dia_t1_icd10 = ["(E109)"]

dia_t2_icd09 = ["(250[0123456789][02])"]
dia_t2_icd10 = ["(E119)"]

hypercholesterolemia_icd09 = ["(2720)"]
hypercholesterolemia_icd10 = ["(E7801)"]

hypertension_icd09 = ["(401)|(401[019])"]
hypertension_icd10 = ["(I10)"]

hyperlipidemia_icd09 = ["(272[24])"]
hyperlipidemia_icd10 = ["(E784)"]

tobacco_icd09 = ["(3051)"]
tobacco_icd10 = ["(F17200)"]

class Definitions:
    def __init__(self):
        self.chf      = chf_icd09 + chf_icd10
        self.chf_regx = make_regex(self.chf)

        self.mi       = mi_icd09 + mi_icd10
        self.mi_regx  = make_regex(self.mi)

        self.stroke      = stroke_icd09 + stroke_icd10
        self.stroke_regx = make_regex(self.stroke)

        self.ckd      = ckd_icd09 + ckd_icd10
        self.ckd_regx = make_regex(self.ckd)

        self.ra      = ra_icd09 + ra_icd10
        self.ra_regx = make_regex(self.ra)

        self.dia_t1 = dia_t1_icd09 + dia_t1_icd10
        self.dia_t1_regx = make_regex(self.dia_t1)

        self.dia_t2 = dia_t2_icd09 + dia_t2_icd10
        self.dia_t2_regx = make_regex(self.dia_t2)

        self.hyperchol = hypercholesterolemia_icd09 + hypercholesterolemia_icd10
        self.hyperchol_regx = make_regex(self.hyperchol)

        self.hypertension = hypertension_icd09 + hypertension_icd10
        self.hypertension_regx = make_regex(self.hypertension)

        self.hyperlipidemia = hyperlipidemia_icd09 + hyperlipidemia_icd10
        self.hyperlipidemia_regx = make_regex(self.hyperlipidemia)

        self.tobacco = tobacco_icd09 + tobacco_icd10
        self.tobacco_regx = make_regex(self.tobacco)

        self.medclasses = {
            "Insulin" : "682008",
            "Statin":  "240608",
            "Sulfonylureas": "682020",
            "Thiazolidinediones": "682028",
            "ACEInhibitor": "243204",
            "BBlocker": "242400",
            "ABlocker": "242000",
            "Statin": "240608",
            "Dihydropyridines" : "242808", # hypertension
            "Antiinflammatory" : "840600",
            "Antiinflammatory2": "563600",
            "Biguanides" : "175735",
            "CalciumChannelBlockers" : "242892",
            "LoopDiuretics" : "402808",
            "AntiCoagulants" : "201204",
            "CholesterolAbsorptionInhibitors" : "240605",
            "NitrateNitrite" : "241208",
            "Cardiotonic": "240408"
        }
