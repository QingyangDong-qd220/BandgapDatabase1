# coding=utf-8
from MaterialParser.material_parser import MaterialParser
import json
import regex as re
from pprint import pprint
from collections import OrderedDict
import os, sys
import joblib
import csv



mp = MaterialParser(verbose=False, pubchem_lookup=False, fails_log=False)

# testing
material_strings = ["Ag1/8Pr5/8MoO4", "CuCrO2 / Ag2O", "CuCrO2", "hematite ( Fe2O3 )", "Indium sulfide ( In2S3 )", "CdS @ TiO2 / Ni2P", "MIL-53(Fe)", "UiO-66-(COOH)2", "SPEs", " "]


def parse_compound(material_string):

    # print(f'material_string = {material_string}')
    parts = [p for p in re.split(r'\s?/\s?|\s\(\s|\s\)|\s@\s', material_string) if p != '' and p is not None]
    # print(f'parts = {parts}')


    composition_list = {}
    for part in parts:
        material = mp.reconstruct_list_of_materials(part)
        material = material if material != [] else [(part, '')]
        # pprint(material)
        
        for m, val in material:
            try:
                result = mp.parse_material(m)
            except KeyError:
                print("KeyError: ", m)
                result = dict(material_string=m,
                    composition=[dict(formula=m, amount='1.0', elements={})])

        for i in result['composition']:
            for j in i['elements'].items():
                if j[0] not in composition_list.keys():
                    try:
                        composition_list[j[0]] = float(j[1])
                    except ValueError:
                        composition_list[j[0]] = 1
                else:
                    try:
                        composition_list[j[0]] += float(j[1])
                    except ValueError:
                        composition_list[j[0]] += 1

    # pprint(composition_list) # could be empty
    # print("\n\n\n")

    return composition_list



# adding composition into existing database_v1 and save as a new one
'''
database = joblib.load(r'D:\Cambridge\PhD\Auto_generated_Database_of_Semiconductor_Band_Gaps_Using_ChemDataExtractor\Results\database.sav')
print('finished loading database.\n')

yes, no = 0, 0
for i, record in enumerate(database[:]):
    composition = parse_compound(record['Name'])
    if composition:
        record['Composition'] = composition
        yes += 1
    else:
        record['Composition'] = None
        no += 1
    if i % 1000 == 0:
        print(i)

joblib.dump(database, "new_database.sav")
print("finished dumping")
print(f"yes = {yes}, no = {no}") # yes = 87553, no = 12683
'''


# saving as other formats
new_database = joblib.load("new_database.sav")
print("finished loading new_database.\n")

# count
not_empty = 0
parsable_name = 0
list_of_names = []
for record in new_database:
    if record['Name'] not in list_of_names:
        list_of_names.append(record['Name'])
        if record['Composition']:
            parsable_name += 1

    if record['Composition']:
        not_empty += 1


filled = not_empty / len(new_database)
parsable = parsable_name / len(list_of_names)
print(f"{filled:.2f} of {len(new_database)} records can be parsed;\n{parsable:.2f} of {len(list_of_names)} compound_names can be parsed.\n")



# save
with open('new_database.json', 'w', encoding='utf-8') as f:
    json.dump(new_database, f)
print("finished writing json.\n")

with open('new_database.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['Name', 'Composition', 'Value', 'Unit', 'Raw_value', 'Raw_unit', 'Snowball', 'Confidence', 'AutoSentenceParser', 'BandgapDB', 'Text', 'Publisher', 'DOI', 'Temperature_value', 'Temperature_unit', 'Temperature_raw_value', 'Temperature_raw_unit', 'Notes']
    thewriter = csv.DictWriter(f, fieldnames = fieldnames)
    
    thewriter.writeheader()
    for i in new_database:
        thewriter.writerow(i)
print("finished writing csv.\n")
