import os, sys, shutil
import json
import requests
from pprint import pprint
import joblib
import time
import re


api_key = ''
journal_name = 'Title'


def insert_eV(old_text):
    '''
    insert band gap units to sentences that contain multiple tuples (which has only one unit)
    '''
    
    # define the sentence patterns
    pattern_2 = r'(\d{1,2}\.?\d*)(\sand\s\d{1,2}\.?\d*\s?eV\s?[\D\s]*,?\s?respectively)'
    pattern_3 = r'(\d{1,2}\.?\d*)(\s?,\s\d{1,2}\.?\d*)(\s?,?\sand\s\d{1,2}\.?\d*\seV\s?[\D\s]*,\s?respectively)'
    pattern_4 = r'(\d{1,2}\.?\d*)(\s?,\s\d{1,2}\.?\d*)(\s?,\s\d{1,2}\.?\d*)(\s?,?\sand\s\d{1,2}\.?\d*\seV\s?[\D\s]*,\s?respectively)'

    # insert electronvolt
    text_1 = re.sub(pattern_4, r'\1 eV\2 eV\3 eV\4', old_text)
    text_2 = re.sub(pattern_3, r'\1 eV\2 eV\3', text_1)
    text_3 = re.sub(pattern_2, r'\1 eV\2', text_2)
        
    return text_3


def download(result):
    '''
    download articles from Elsevier
    '''

    # DOI is used for naming files
    doi = result['doi']
    
    # article location
    file_path = r'D:\Cambridge\Project\Main\Codes\web_scrapping\Elsevier\articles\{}'.format(journal_name)
    file_name = '{}\{}.xml'.format(file_path, doi.replace('/', '_'))
    
    request_url = 'https://api.elsevier.com/content/article/doi/{}?apiKey={}&httpAccept=text%2Fxml'.format(doi, api_key)
    
    # write article content into file
    with open(file_name, 'w', encoding='utf-8') as f:
        text_1 = requests.get(request_url).text.replace('room temperature', '300 K')
        text_2 = insert_eV(text_1)
        f.write(text_2)
    
    return


# metadata location
meta_dir = r'D:\Cambridge\Project\Main\Codes\web_scrapping\Elsevier\metadata\{}'.format(journal_name)
meta_name = r'combined.sav'
search_results = joblib.load('{}\{}'.format(meta_dir, meta_name))

# number of articles
total_num_article = len(search_results)
print('total number of articles:', total_num_article)



# start downloading (note: articles prior to year 2000 are likely scanned, not good!)
for i in range(0, total_num_article):
    search_result = search_results[i]
    download(search_result)
    print(journal_name, ',', i, '/', total_num_article, ',', search_result['publicationDate'])
print('done')
