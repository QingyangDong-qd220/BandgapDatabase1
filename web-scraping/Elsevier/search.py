import os, sys, shutil
import json
import requests
from pprint import pprint
import joblib
import time


# function that requests the response from Elsevier
def get_response(url, Data, Headers):
    response = requests.put(url, data=json.dumps(Data), headers=Headers)
    response = response.text.replace('false', 'False').replace('true', 'True')
    
    return eval(response) # eval convert a big string into 2 small strings


# keywords for searching
api_key = ''
base_url = 'https://api.elsevier.com/content/search/sciencedirect'
query_text = 'band gap'
Offset = 0
Show = 100
Headers = {'x-els-apikey': api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}

# set journal
Pub_list = ['Results in Physics', 'Thin Solid Films', 'Optical Materials', 'Materials Today Proceedings', 'Chemical Engineering Journal', 'Physica Condensed Matter']
Pub = Pub_list[0]


def search_journal(Date):
    '''
    search for article metadata, save them in a series of files tagged by offset
    '''
    for Offset in range(0, 1000, Show):
        Data = {'qs': query_text, 'pub': Pub, 'date': Date, 'filter': {"openAccess": True}, 'display': {'show': Show, 'offset': Offset, 'sortBy': 'date'}} # 'pub': Pub, 
        save_name = 'metadata/elsevier_pub={}_date={}_offset={}.sav'.format(Pub, Date, Offset)
        response = get_response(base_url, Data, Headers) # contains 'results' and 'resultsFound'

        try:
            print('year=', Date, 'offset=', Offset, ', num of articles=', len(response['results']))
            joblib.dump(response['results'], save_name)
            time.sleep(1)
        except KeyError:
            print('nothing more')
            break
            
    return


def search_title():


    '''
    search for article title, save them in a series of files tagged by offset
    '''
    for Offset in range(0, 10000, Show):
        Data = {'title': 'band gap', 'filter': {"openAccess": True}, 'display': {'show': Show, 'offset': Offset, 'sortBy': 'date'}}
        save_name = 'metadata/elseviertitle_offset={}.sav'.format(Offset)
        response = get_response(base_url, Data, Headers) # contains 'results' and 'resultsFound'

        try:
            print('offset=', Offset, ', num of articles=', len(response['results']))
            joblib.dump(response['results'], save_name)
            time.sleep(2)
        except KeyError:
            print('nothing more')
            break
            
    return


if __name__ == "__main__":
    search_title()
