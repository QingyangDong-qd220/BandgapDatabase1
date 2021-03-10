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



# define a nested model
class Temperature(TemperatureModel):
    specifier_expression =(I('at') | W('T')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=False, updatable=False)
    compound = ModelType(Compound, required=True, updatable=False)
    parsers = [AutoSentenceParser()]

# define a parent model
class BandGap(EnergyModel):
    specifier_expression =((I('band') + R('gaps?')) | I('bandgap') | I('band-gap') | W('Eg')).add_action(join)
    specifier = StringType(parse_expression=specifier_expression, required=True, updatable=True)
    compound = ModelType(Compound, required=True, contextual=True, binding=True, updatable=False)
    temp = ModelType(Temperature, required=False)
    parsers = [AutoSentenceParser()]



# s = Sentence('The band gap of ZnTe was reduced by 0.38 eV due to O+ doping. ')


'''load snowball model'''
home_path = 'Snowball_model'
folder = 'General'
model_name =  'general'

try:
    snowball = Snowball.load('{}\{}\{}.pkl'.format(home_path, folder, model_name))
    print('load existing model')
except:
    snowball = Snowball(model=BandGap, tc=0.01, tsim=0.90, prefix_weight=0.0, middle_weight=1.0, suffix_weight=0.0, max_candidate_combinations=100, save_dir='{}\{}'.format(home_path, folder)+r'/')
    snowball.save_file_name = model_name
    print('make a new model')
    if not os.path.exists(snowball.save_dir):
        os.makedirs(snowball.save_dir)
    
BandGap.parsers = [snowball]
print('tsim =', snowball.minimum_cluster_similarity_score)



'''get list of training articles'''
training_folder = r'Web-scraping\evaluation'
file_list = os.listdir(training_folder)

# get the list of articles that have been processed
log_name = r'{}\log_trained.txt'.format(r'D:\Cambridge\PhD')
try:
    with open(log_name, 'r', encoding='utf-8') as f:
        finished_list = f.read().splitlines()
except:
    finished_list = []
print('Number of processed papers:', len(finished_list))

articles = []
for file in file_list:
    if file not in finished_list:
        articles.append(file)

print('Number of papers left:', len(articles))



'''start training'''
i = 0
for article in articles:
    print(article)
    d = Document.from_file('{}\{}'.format(training_folder, article))
    # print(article)
    
    for p in d.paragraphs:
        for s in p.sentences:
            if s.end - s.start > 300:
                continue       
                
            # train
            snowball.train_from_sentence(s)
            c_list = []
            
            for c in snowball.clusters:
                # if c.pattern.confidence == 0.0:
                c.pattern.confidence = 1.0
                c_list.append(c.pattern.confidence)
            
    print(len(c_list))
            
    # with open('log_trained.txt', 'a+', encoding='utf-8') as f:
        # f.write(article + "\n")
    
    i += 1



