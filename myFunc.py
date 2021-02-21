'''
custom functions to facilitate the database generation
'''

import os, sys, shutil, re
import pickle
import joblib


def backup(folder_name, model_name):

    '''
    save a backup copy of a trained snowball model
    '''
    
    if not os.path.exists('{}/Backup'.format(folder_name)):
        os.makedirs('{}/Backup'.format(folder_name))
    shutil.copyfile('{}/{}_clusters.txt'.format(folder_name, model_name), '{}/Backup/{}_clusters.txt'.format(folder_name, model_name))
    shutil.copyfile('{}/{}_patterns.txt'.format(folder_name, model_name), '{}/Backup/{}_patterns.txt'.format(folder_name, model_name))
    shutil.copyfile('{}/{}_relations.txt'.format(folder_name, model_name), '{}/Backup/{}_relations.txt'.format(folder_name, model_name))
    shutil.copyfile('{}/{}.pkl'.format(folder_name, model_name), '{}/Backup/{}.pkl'.format(folder_name, model_name))
    shutil.copyfile('{}/log_trained.txt'.format(folder_name), '{}/Backup/log_trained.txt'.format(folder_name))
    pass


def restore(folder_name, model_name):

    '''
    overwrite the current snowball model with a backup copy
    '''
    
    try:
        os.remove('{}/{}_clusters.txt'.format(folder_name, model_name))
        os.remove('{}/{}_patterns.txt'.format(folder_name, model_name))
        os.remove('{}/{}_relations.txt'.format(folder_name, model_name))
        os.remove('{}/{}.pkl'.format(folder_name, model_name))
    except:
        print('delete failure, files do not exist')
    shutil.copyfile('{}/Backup/{}_clusters.txt'.format(folder_name, model_name), '{}/{}_clusters.txt'.format(folder_name, model_name))
    shutil.copyfile('{}/Backup/{}_patterns.txt'.format(folder_name, model_name), '{}/{}_patterns.txt'.format(folder_name, model_name))
    shutil.copyfile('{}/Backup/{}_relations.txt'.format(folder_name, model_name), '{}/{}_relations.txt'.format(folder_name, model_name))
    shutil.copyfile('{}/Backup/{}.pkl'.format(folder_name, model_name), '{}/{}.pkl'.format(folder_name, model_name))
    shutil.copyfile('{}/Backup/{}_trained_set.txt'.format(folder_name, model_name), '{}/{}_trained_set.txt'.format(folder_name, model_name))
    pass


def rt_replace(filename):

    '''
    replace the string "room temperature" with "300 K" so that CDE can extract the data
    '''
    
    with open(filename, 'r', encoding='utf-8') as file :
        oldarticle = file.read()
    
    newarticle = oldarticle.replace('room temperature', '300 K')

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(newarticle)
    
    return
    

def insert_eV(old_text):
    '''
    insert bandgap units to sentences that contain multiple tuples (which has only one unit)
    '''
    
    # define the sentence patterns
    pattern_2 = r'(\d{1,2}\.?\d*)(\sand\s\d{1,2}\.?\d*\s?eV\s?[\D\s]*,\s?respectively)'
    pattern_3 = r'(\d{1,2}\.?\d*)(\s?,\s\d{1,2}\.?\d*)(\s?,?\sand\s\d{1,2}\.?\d*\seV\s?[\D\s]*,\s?respectively)'
    pattern_4 = r'(\d{1,2}\.?\d*)(\s?,\s\d{1,2}\.?\d*)(\s?,\s\d{1,2}\.?\d*)(\s?,?\sand\s\d{1,2}\.?\d*\seV\s?[\D\s]*,\s?respectively)'

    # insert electronvolt
    text_1 = re.sub(pattern_4, r'\1 eV\2 eV\3 eV\4', old_text)
    text_2 = re.sub(pattern_3, r'\1 eV\2 eV\3', text_1)
    text_3 = re.sub(pattern_2, r'\1 eV\2', text_2)
        
    return text_3
    
    
def add_doi(results, file):
    
    '''
    add article DOI to records found by CDE for tracking
    input: CDE results from one article as a list of dicts
    '''
    
    for result in results:
        for key in result.keys():
            result[key]['doi'] = file.replace('_', '/')
    
    return results


def mod_confidence(model_name):
    
    '''
    change the pattern's confidence in trained snowball model to 1.0
    '''
    
    folder_name = 'Snowball_model'
    # model_name = 'BandGap'
    new_model_name = 'test'
    with open(r'D:\Cambridge\Project\Main\Codes\{}\{}.pkl'.format(folder_name, model_name), 'rb') as f:
        snowball = pickle.load(f)

    for c in snowball.clusters:
        if c.pattern.confidence == 0.0:
            c.pattern.confidence = 1.0
            
    with open(r'D:\Cambridge\Project\Main\Codes\{}\{}.pkl'.format(folder_name, model_name), 'wb') as f:
                pickle.dump(snowball, f)
    
    return


def count_key(results, key_name):

    '''
    count how many records have the specified key name
    '''

    # keys = ['journal', 'publication_date', 'source', 'title', 'url', 'compound', 'article_doi', 'confidence', 'publisher', 'specifier', 'units', 'value', 'temperature_value', 'temperature_unit', 'error']

    i = 0
    for result in results:
        if key_name in result.keys():
            i += 1
    
    return i


if __name__ == "__main__":
    keys = ['journal', 'publication_date', 'source', 'title', 'url', 'compound', 'article_doi', 'confidence', 'publisher', 'specifier', 'unit', 'value', 'temperature_value', 'temperature_unit', 'error']
    results = joblib.load('combined_records.sav')
    for key in keys:
        num = count_key(results, key)
        print(key, num)
    
    