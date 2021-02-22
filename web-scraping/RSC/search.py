import os, sys, shutil
import json
import requests
from pprint import pprint
import joblib
import time
import re
from chemdataextractor2.scrape.pub.rsc import RscSearchScraper
from selenium import webdriver



query_text = "band gap"


def search(Page):
    '''
    search RSC metadata for band gap on a single page
    '''
    scrape = RscSearchScraper(driver=Driver).run(query_text, page=Page) # raw results
    results = scrape.serialize()  # convert to JSON style search results
    
    return results


def combine_metadata():
    metadata = []

    for Page in range(1,2600,1):
        results = joblib.load('metadata/rsc_page={}.sav'.format(Page))
        for result in results:
            metadata.append(result)
            
    joblib.dump(metadata, 'rsc_metadata.sav')
    print(len(metadata))

    return


def sort_metadata(path):
    
    path = 'rsc_metadata.sav'
    results = joblib.load(path)
    print('total number of articles: ', len(results))
    
    for result in results:
        for key in result.keys():
            if key not in key_list.keys():
                key_list[key] = 1
            else:
                key_list[key] += 1
    
    return key_list


if __name__ == "__main__":
    # requires a web browser driver (added to PATH), add Chrome driver only once to save time 
    Driver = webdriver.Chrome() 

    for Page in range(2500,2600,1):
        save_name = 'metadata/rsc_page={}.sav'.format(Page)
        results = search(Page)
        joblib.dump(results, save_name)
        print('page=', Page, 'num of articles=', len(results))
        # time.sleep(1)

    Driver.close()
    
    combine_metadata()
    pprint(sort_metadata('rsc_metadata.sav'))
    
