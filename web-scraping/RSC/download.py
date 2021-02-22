import os, sys, shutil
import json
import requests
from pprint import pprint
import joblib
import time
import re
import urllib


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


def insert_replace(file):
    '''
    replace room temperature with 300 K, and insert eV for respectively, convert binary to string
    input: file name without directory
    '''
    
    source = r'{}\{}'.format(folder, file)
    with open(source, 'rb') as f:
        text = f.read().decode('utf-8').replace('room temperature', '300 K')
        text_2 = insert_eV(text)
    
    target = r'{}\{}'.format(destination, file)
    with open(target, 'w', encoding='utf-8') as f:
        f.write(text)


def download(metadata_path):
    '''
    download RSC articles from metadata
    '''
    results = joblib.load(metadata_path)
    
    i = 0
    partial = results[60000:]
    for result in partial:
        
        # check if article has a link (some articles are retracted and are not accessible)
        if 'html_url' not in result:
            print('url not exist')
            continue
        
        url = result['html_url']
        doi  = result['doi']
        
        # convert from url to content
        webcontent = urllib.request.urlopen(url).read()
        text = webcontent.decode('utf-8').replace('room temperature', '300 K')
        text_2 = insert_eV(text)

        # the / in doi interfere with naming the file
        file_name = r'D:\Cambridge\PhD\Web-scraping\RSC\articles\{}.html'.format(doi.replace('/', '_'))
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(text_2)
        
        i += 1
        print(i, '/', len(partial), ', size: ', int(os.path.getsize(file_name)/1024), 'kb')
        # time.sleep(1)
    
    return


    



if __name__ == "__main__":

    download('rsc_metadata.sav')
    




