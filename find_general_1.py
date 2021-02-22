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
from check_records import sentence_check, log_sentence, load_model
# suppress Pandas FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

s = Sentence('The α-Fe2O3 possess excellent band gap (2.2 eV) which leads to better photocatalytic degradation . ')

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



'''load snowball model'''
home_path = 'D:\Cambridge\PhD\Snowball_model'
folder = 'General'
model_name =  'general'

# load model
snowball = Snowball.load('{}\{}\{}.pkl'.format(home_path, folder, model_name))
    
snowball.minimum_relation_confidence = 0.001
# snowball.minimum_cluster_similarity_score = 0.85
snowball.max_candidate_combinations = 100
snowball.save_file_name = model_name
snowball.set_learning_rate(0.0)
# BandGap.parsers = [snowball]



def run(file_path, article):
    '''
    use snowball to serialize an article
    '''
    
    results = []
    
    # load a paper
    try:
        d = Document.from_file(file_path)
    except:
        print('unable to read document')
        return
        
    if article[-3:] == 'txt':
        publisher = 'Springer'
    elif article[-3:] == 'xml':
        publisher = 'Elsevier'
    elif article[-3:] == 'tml':
        publisher = 'RSC'
    
    # process a paper
    for p in d.paragraphs:
        for s in p.sentences:
            if s.end - s.start > 300:
                continue       
                
            results_snow = []
            results_auto = []
            snow_85 = False
            
            # auto
            BandGap.parsers = [AutoSentenceParser()]
            s.models = [BandGap]
            auto = s.records.serialize()
            for i in auto:
                if 'BandGap' in i.keys():
                    if 'raw_value' in i['BandGap'].keys() and 'compound' in i['BandGap'].keys():
                        if 'names' in i['BandGap']['compound']['Compound'].keys():
                            i['BandGap']['text'] = s.text
                            i['BandGap']['doi'] = article.replace('_', '/').replace('.html', '').replace('.xml', '').replace('.txt', '')
                            results_auto.append(i)
                            
            # snow
            snowball.minimum_cluster_similarity_score = 0.85
            BandGap.parsers = [snowball]
            s.models = [BandGap]
            snow = s.records.serialize()
            for i in snow:
                if 'BandGap' in i.keys():
                    snow_85 = True
                    i['BandGap']['text'] = s.text
                    i['BandGap']['doi'] = article.replace('_', '/').replace('.html', '').replace('.xml', '').replace('.txt', '')
                    results_snow.append(i)
            
            if snow_85 == False:
                snowball.minimum_cluster_similarity_score = 0.65
                BandGap.parsers = [snowball]
                s.models = [BandGap]
                snow = s.records.serialize()
                for i in snow:
                    if 'BandGap' in i.keys():
                        i['BandGap']['text'] = s.text
                        i['BandGap']['doi'] = article.replace('_', '/').replace('.html', '').replace('.xml', '').replace('.txt', '')
                        results_snow.append(i)

            # combine results from Snowball to AutoSentenceParser
            for i in results_auto:
                i['BandGap']['AutoSentenceParser'] = 1
                i['BandGap']['Snowball'] = 0
                for j in range(len(results_snow)):
                    if i['BandGap']['compound']['Compound']['names'] == results_snow[j]['BandGap']['compound']['Compound']['names']:
                        i['BandGap'] = results_snow[j]['BandGap']
                        # i['BandGap']['value'] = results_snow[j]['BandGap']['value']
                        # i['BandGap']['raw_value'] = results_snow[j]['BandGap']['raw_value']
                        # i['BandGap']['raw_units'] = results_snow[j]['BandGap']['raw_units']
                        i['BandGap']['Snowball'] = 1
                        i['BandGap']['AutoSentenceParser'] = 1
                        # i['BandGap']['confidence'] = results_snow[j]['BandGap']['confidence']
                        results_snow[j]['BandGap']['match'] = 1
                        # temperature needs work
                        if 'value' in results_snow[j]['BandGap']['temp']['Temperature'].keys():
                            i['BandGap']['temp'] = results_snow[j]['BandGap']['temp']
                        continue
            
            # Snowball only results
            for x in results_snow:
                if 'match' not in x['BandGap'].keys():
                    x['BandGap']['Snowball'] = 1
                    x['BandGap']['AutoSentenceParser'] = 0
                    results_auto.append(x)
            
            if results_auto:
                for i in results_auto:
                    i['BandGap']['publisher'] = publisher
                    results.append(i)
    
    
    return results
    
    
# get list of articles
folder = r'D:\Cambridge\PhD\Web-scraping\Springer\articles'
file_list = os.listdir(folder)

# load already found records
save_name = 'records_general_all_spr1.sav'
try:
    records = joblib.load(save_name)
    print('load existing records')
except:
    records = []
    print('no records found') 
    
# start
for i in range(0, len(file_list), 6):
    article = file_list[i]
    print(i, '/', len(file_list), ',', article)
    file_path = r'{}\{}'.format(folder, article)
        
    temp = run(file_path, article)
        
    # save records
    if temp:
        pprint(temp)
        for i in temp:
            records.append(i)
        joblib.dump(records, save_name)
        
        






