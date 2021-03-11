from pprint import pprint
import os, sys
import joblib
from chemdataextractor2.relex import Snowball
from chemdataextractor2.model.units import EnergyModel, TemperatureModel
from chemdataextractor2.model import BaseModel, StringType, ListType, ModelType, Compound
from chemdataextractor2.parse import R, I, W, Optional, merge, join, AutoSentenceParser
from chemdataextractor2.parse.template import QuantityModelTemplateParser, MultiQuantityModelTemplateParser
from chemdataextractor2.doc import Sentence, Document
import warnings
import re
import numpy as np
import csv
import json
# suppress Pandas FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

'''
combine, normalize, and clean data records
'''

# define a nested model
class Temperature(TemperatureModel):
    specifier_expression =(I('at') | W('T')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=False, updatable=False)
    compound = ModelType(Compound, required=True, updatable=False)
    parsers = [AutoSentenceParser()]

# define a parent model
class BandGap(EnergyModel):
    specifier_expression =((I('band') + R('gaps?')) | I('bandgap') | I('band-gap') | I('Eg')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)
    temp = ModelType(Temperature, required=False)
    parsers = [AutoSentenceParser()]


empty_entry = {
    'Name': None, 
    'Value': None, 
    'Unit': None, 
    'Raw_value': None, 
    'Raw_unit': None, 
    'Temperature_value': None, 
    'Temperature_unit': None, 
    'Temperature_raw_value': None, 
    'Temperature_raw_unit': None, 
    'AutoSentenceParser': None, 
    'Snowball': None, 
    'BandgapDB': None, 
    'Confidence': None, 
    'Text': None, 
    'Publisher': None, 
    'DOI': None, 
    'Notes': None}


def count_names(key, records):
    names = []
    count = 0
    for i in records:
        if key in i.keys() and 'del' not in i.keys():
            count += 1
            if i[key] not in names:
                names.append(i[key])
    print(key, 'has values:', names, '; Total count:', count)
    return


'''load'''
folder = r'Results'
file_list = os.listdir(folder)
ru_db = joblib.load('Results\BandGapDB.sav')
special = joblib.load('Results\special.sav')
# print('num of russianDB records:', len(ru_db), '\n')

results = []
for i in file_list:
    if 'records_general_all' in i:
        temp = joblib.load('{}\{}'.format(folder, i))
        for j in temp:
            results.append(j)

print('num of all CDE records:', len(results), '\n')




'''combine'''
combined_records = []
count = 0
for i in results:
    temp = empty_entry.copy()


    temp['Name'] = i['BandGap']['compound']['Compound']['names'][0]
    temp['Raw_value'] = i['BandGap']['raw_value']
    temp['Raw_unit'] = i['BandGap']['raw_units']
    temp['Value'] = i['BandGap']['value']
    temp['Unit'] = i['BandGap']['units']
    if i['BandGap']['Snowball'] == 1:
        temp['Snowball'] = True
        temp['Confidence'] = i['BandGap']['confidence']
    else:
        temp['Snowball'] = False
    if i['BandGap']['AutoSentenceParser'] == 1:
        temp['AutoSentenceParser'] = True
    else:
        temp['AutoSentenceParser'] = False
    temp['BandgapDB'] = False
    temp['Text'] = i['BandGap']['text']
    temp['Publisher'] = i['BandGap']['publisher']
    temp['DOI'] = i['BandGap']['doi']
    if 'temp' in i['BandGap'].keys():
        if 'value' in i['BandGap']['temp']['Temperature'].keys():
            temp['Temperature_raw_value'] = i['BandGap']['temp']['Temperature']['raw_value']
            temp['Temperature_value'] = i['BandGap']['temp']['Temperature']['value']
            temp['Temperature_raw_unit'] = i['BandGap']['temp']['Temperature']['raw_units']
            # some records have raw_unit but no unit
            if 'units' in i['BandGap']['temp']['Temperature'].keys():
                temp['Temperature_unit'] = i['BandGap']['temp']['Temperature']['units']
            else:
                if 'K' in i['BandGap']['temp']['Temperature']['raw_units']:
                    temp['Temperature_unit'] = 'Kelvin^(1.0)'
                elif 'C' in i['BandGap']['temp']['Temperature']['raw_units']:
                    temp['Temperature_unit'] = 'Celsius^(1.0)'
    combined_records.append(temp)
    count += 1


for i in ru_db:
    temp = empty_entry.copy()
    
    temp['Name'] = i['Compound']
    temp['Value'] = [i['Band gap (eV)']]
    temp['Unit'] = 'ElectronVolt^(1.0)'
    temp['BandgapDB'] = True
    temp['Snowball'] = False
    temp['AutoSentenceParser'] = False
    temp['Temperature_value'] = [i['Temperature (K)']]
    temp['Temperature_unit'] = 'Kelvin^(1.0)'
    if 'DOI' in i.keys():
        temp['DOI'] = i['DOI']
    else:
        temp['Notes'] = i['Notes']
    combined_records.append(temp)
    
print('num of combined records:', len(combined_records), '\n')



'''normalize'''
for i in combined_records:
    if 'Temperature_unit' in i.keys():
        if i['Temperature_unit'] == 'Celsius^(1.0)':
            i['Temperature_unit'] = 'Kelvin^(1.0)'
            if type(i['Temperature_value']) == float:
                i['Temperature_value'] = i['Temperature_value'] + 273.15
            elif type(i['Temperature_value']) == list:
                for j in range(len(i['Temperature_value'])):
                    i['Temperature_value'][j] = i['Temperature_value'][j] + 273.15
        elif i['Temperature_unit'] == 'Fahrenheit^(1.0)':
            i['del'] = True
        elif i['Temperature_unit'] == '(10^3.0) * Kelvin^(1.0)':
            i['Temperature_unit'] = 'Kelvin^(1.0)'
            i['Temperature_value'] = i['Temperature_value'] * 1000
    
    if i['Unit'] == '(10^-3.0) * ElectronVolt^(1.0)':
        i['Unit'] = 'ElectronVolt^(1.0)'
        if type(i['Value']) == float:
            i['Value'] = i['Value'] / 1000
        elif type(i['Value']) == list:
            for j in range(len(i['Value'])):
                i['Value'][j] = i['Value'][j] / 1000

print('normalize done')


'''clean'''
for i in combined_records:
    if i['BandgapDB'] == False:
        if i['Unit'] in ['(10^3.0) * ElectronVolt^(1.0)', '(10^6.0) * ElectronVolt^(1.0)', 'Joule^(1.0)', '(10^-3.0) * Joule^(1.0)', '(10^3.0) * Joule^(1.0)']:
            i['del'] = True
            continue
            
        if i['Name'] in ['brookite', 'Brookite', 'nitrogen', 'Nitrogen', 'oxygen', 'Oxygen', 'VB', 'VBM', 'TM', 'transition metal', 'VOC']:
            i['del'] = True
            continue
        elif i['Name'][-1] in ['+', '-']:
            i['del'] = True
            continue
        elif len(i['Name']) in [1, 2] and i['Name'] not in ['Ge', 'Sn', 'Si', 'Se', 'Te', 'C', 'S']:
            i['del'] = True
            continue
            
        if np.mean(i['Value']) < 0 or np.mean(i['Value']) > 20:
            i['del'] = True
            continue
            
        if 'Text' in i.keys():
            if 'by {} {}'.format(i['Raw_value'], i['Raw_unit']) in i['Text']:
                # print(i['Text'], '\n')
                i['del'] = True
        
        for j in special:
            if i['Name'] == j['BandGap']['compound']['Compound']['names'][0] and i['Raw_value'] == j['BandGap']['raw_value'] and i['Text'] == j['BandGap']['text']:
                i['del'] = True
                continue



# count_names('Unit', combined_records)
# count_names('Temperature_unit', combined_records)



'''save'''
temp = []
c = 0
for i in combined_records:
    if 'del' not in i.keys():
        temp.append(i)
    if 'del' in i.keys() and i['BandgapDB'] == True:
        c += 1
print(len(temp))  
 
joblib.dump(temp, 'Results/database.sav')

with open('Results/database.json', 'w', encoding='utf-8') as f:
    json.dump(results, f)

with open('Results/database.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['Name', 'Value', 'Unit', 'Raw_value', 'Raw_unit', 'Snowball', 'Confidence', 'AutoSentenceParser', 'BandgapDB', 'Text', 'Publisher', 'DOI', 'Temperature_value', 'Temperature_unit', 'Temperature_raw_value', 'Temperature_raw_unit', 'Notes']
    thewriter = csv.DictWriter(f, fieldnames = fieldnames)
    
    thewriter.writeheader()
    for i in combined_records:
        if 'del' not in i.keys():
            thewriter.writerow(i)








