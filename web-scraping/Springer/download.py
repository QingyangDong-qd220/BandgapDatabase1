import os
import sys
import json
import requests
import urllib.request
from pprint import pprint
import joblib
import time
import re
from bs4 import BeautifulSoup
import unicodedata


def scrap_spr_tdm(starting_number, year, num_articles, dump):

    '''
    search article using TDM API of Springer
    output: response in JATS format (".sav", contains full text)
    '''
    
    tdm_api_key = ''
    tdm_url = 'https://articles-api.springer.com/xmldata/jats'
    # year = 2020
    empty = '%22band%20gap%22%20AND%20year:{}'.format(year)
    # starting_number = 1
    # num_articles = 3
    spr_url = '{}?q={}&excludeElements=Bibliography&api_key={}&s={}&p={}'.format(tdm_url, empty, tdm_api_key, starting_number, num_articles)

    response = requests.get(spr_url)

    file_name = 's={}_year={}'.format(starting_number, year)

    if response:
        # print('search success')
        print('start from number:', starting_number)
        # pprint(response.text)
        if dump == True:
            joblib.dump(response, '{}/{}.sav'.format(res_folder, file_name))
    else:
        print('search error', response)
        sys.exit()

    return response


def find(raw_text, target):

    index = []
    patterns_fig = [r'(<fig>|<fig\sid="[\w\d]+">)', r'</fig>']
    patterns_tb = [r'(<table\-wrap>|<table\-wrap\sid="[\w\d]+">)', r'</table\-wrap>']
    pattern_article = [r'<article\s', r'</article>']
    pattern_doi = [r'<article\-id\spub\-id\-type="doi">', r'</article\-id>']
    
    if target == 'fig':
        patterns = patterns_fig
    elif target == 'tb':
        patterns = patterns_tb
    elif target == 'article':
        patterns = pattern_article
    elif target == 'doi':
        patterns = pattern_doi

    matches = re.finditer(patterns[0], raw_text)

    for match in matches:
        # print(match)
        end = re.search(patterns[1], raw_text[match.start(0):]).end(0)
        index.append([match.start(0), end + match.start(0)])
    
    return index


def replace(raw_text, index):

    texts = []
    a = 0
    for i in index:
        a += (i[1] - i[0])
        texts.append(raw_text[i[0]:i[1]])

    for i in texts:
        raw_text = raw_text.replace(i, ' ')
        
        
    # print('length of all removed text:', a)

    return raw_text


def remove_section(raw_text):

    '''
    remove some redundant words from raw_text
    add period to captions
    '''

    patterns = [r'<sec[\w\d\s\-":=]*><title>Funding</title>.+</sec>', r'<ack><title>Acknowledgements</title>.+</ack>',
        r'<table\-wrap[\w\d\s\-":=]*>.+</table\-wrap>', r'<fig[\w\d\s\-":=]*><label[\w\d\s\-":=]*>[\w\s\d]+</label>', 
        r'<title>[\w\d\s]+</title>', r'<institution>[^<>/=]+</institution>', 
        r'<award\-id[\w\d\s\-":=]*>[^<>/=]+</award\-id>', r'<meta\-value[\w\d\s\-":=]*>[^<>=]+</meta\-value>', 
        r'<surname[\w\d\s\-":=]*>[^<>/"=]+</surname>', r'<given\-names[\w\d\s\-":=]*>[^<>/"=]+</given\-names>', 
        r'<meta\-name[\w\d\s\-":=]*>[^<>/=]+</meta\-name>', r'<institution\-id[\w\d\s\-":=]*>[^<>"]+</institution\-id>', 
        r'<notes[\w\d\s\-":=]*>.+</notes>', r'<kwd>[^<>/=]*</kwd>', r'<label>[^<>/]*</label>',
        r'<journal\-id\sjournal\-id\-type="[\w\s]*"[^<>]*</journal\-id>', r'<journal\-title>[^<>/]*</journal\-title>',
        r'<abbrev\-journal\-title[\w\d\s\-":=]*>[^<>/=]*</abbrev\-journal\-title>', r'<issn[\w\d\s\-":=]*>[^<>/=]*</issn>',
        r'<publisher\-name>[^<>]*</publisher\-name>', r'<subject>[^<>]*</subject>',
        r'<article\-id[\w\d\s\-":=]*>[^<>]*</article\-id>', r'<publisher\-loc>[^<>]*</publisher\-loc>', 
        r'<copyright\-statement>[^<>]*</copyright\-statement>', r'<copyright\-year>[^<>]*</copyright\-year>', 
        r'<kwd\-group[\w\d\s\-":=]*>.*</kwd\-group>']
    
    for pattern in patterns:
        matches = re.findall(pattern, raw_text)
        # print(matches, '\n')
        for match in matches:
            raw_text = raw_text.replace(match, ' ')
            
    caption_pattern = r'</caption>'
    matches = re.findall(caption_pattern, raw_text)
    for match in matches:
            raw_text = raw_text.replace(match, '. ')
            
    # print(raw_text)
    
    return raw_text

    
def slice_paragraph(raw_text):
    
    '''
    cut a whole piece of xml article into paragraphs
    '''
    
    paragraphs = []
    
    p = []
    pattern = [r'(<p>|<p\sid="[\w\d]+">)', r'</p>']
    starts = re.finditer(pattern[0], raw_text)

    for i in starts:
        end = re.search(pattern[1], raw_text[i.end(0):]).end(0)
        paragraphs.append(raw_text[i.start(0):i.end(0)+end])
        

    return paragraphs

    
def clean_jats(raw_text):
    
    '''
    clean up jats xml text from Springer response
    '''
    
    clean_text = BeautifulSoup(raw_text, "lxml").text
    text = unicodedata.normalize("NFKD", clean_text)
    new1 = re.sub(r'\\usepackage\{.*\}', '', text)
    new2 = re.sub(r'\\setlength\{\\\w+\}\{[\-\d\w]*\}', '', new1)
    new3 = re.sub(r'\\documentclass\[[\w\d]*\]\{\w+\}', '', new2)
    new4 = re.sub(r'\\begin\{document\}.+\\end\{document\}', '', new3)
    new5 = re.sub(r'\S{30,200}', '', new4)
    new6 = re.sub(r'\s{2,300}', ' ', new5)
    new7 = re.sub(r'\n', ' ', new6)
    new8 = re.sub(r'\[[\d\–,\s]+\]', '', new7) # – is not a minus sign
    
    return new8


def response_2_txt(response):
    
    '''
    convert Springer response to article in txt
    '''
    
    paper_folder = 'articles'
    text = response.text
    
    index = find(text, 'article')
    articles = []
    for i in index:
        articles.append(text[i[0]:i[1]])
        
    for raw_text in articles:
        match = BeautifulSoup(raw_text, 'xml').find_all('article-id', {"pub-id-type" : "doi"})
        doi = match[0].text
        journal = get_journal(raw_text)[0]
        
        # remove tables
        for i in ['tb', 'fig']:
            raw_text = replace(raw_text, find(raw_text, i))
            # print('length of new xml:', len(raw_text))
        
        # raw_text = remove_section(raw_text)
        # print(raw_text)
        raw_paragraphs = slice_paragraph(raw_text)
        
        
        paragraphs = []
        for raw_paragraph in raw_paragraphs:
            paragraphs.append(clean_jats(raw_paragraph))
            
        with open('{}/{}.txt'.format(paper_folder, doi.replace('/', '_')), 'w+', encoding='utf-8') as f: 
            f.write(journal + '\n\n')
            for paragraph in paragraphs:
                # print(i, '\n', paragraph, '\n')
                f.write(paragraph + '\n\n')
    print('write success')
        
    return


    
    
def get_total(response):
    
    '''
    slice out the total number of matches from jats xml response from the TDM API of Springer
    input: response from Springer in JATS XML format
    output: int number
    '''
    
    soup = BeautifulSoup(response.text, 'lxml')
    matches = int(soup.find_all('total')[0].text)
    
    return matches
    
    
def get_journal(text):
    
    '''
    slice out the journal name from jats xml response from the TDM API of Springer
    input: response from Springer in JATS XML format
    output: list of strings of journal name
    '''
    
    # text = response.text
     
    start = []
    pattern_start = r'<journal\-title>'
    matches_start = re.finditer(pattern_start, text)
    for match in matches_start:
        start.append(match.end(0))
    # print(start)

    end = []
    pattern_end = r'</journal\-title>'
    matches_end = re.finditer(pattern_end, text)
    for match in matches_end:
        end.append(match.start(0))
    # print(end)
        
    journal_name = []
    for i in range(len(start)):
        journal_name.append(text[start[i]:end[i]])
    
    return journal_name

     
def scrap_spr_meta(doi):

    '''
    search article using TDM API of Springer
    output: response in JATS format (contains full text), and html file of article (wrong encoding!)
    '''

    meta_api_key = 'e8f388b08874cace533df4e894818679'
    meta_url = 'http://api.springernature.com/meta/v2/json'
    spr_url = '{}?q=doi:{}&api_key={}'.format(meta_url, doi, meta_api_key)

    response = requests.get(spr_url)



    if response:
        print('search success')
        metadata = eval(response.text)
    else:
        pprint('search error', response)
        sys.exit()

    return metadata




if __name__ == "__main__":

    starting_number = 1
    num_articles = 50
    year = 2020
    res_folder = 'response'
    paper_folder = 'articles'

    
    response = scrap_spr_tdm(starting_number, year, 1, False)
    matches = get_total(response)
    print('total num of matches =', matches)
    
    
    print('year: ', year)
    for i in range(1, matches, num_articles):
        starting_number = i
        response = scrap_spr_tdm(starting_number, year, num_articles, True)
        # response_2_txt(response)

    


    
    # response = joblib.load('{}/s={}_year={}.sav'.format('test', starting_number, year))

    # print('doi =', get_doi(response.text)[0])

    # response_2_txt(response, '{}/s={}_year={}.txt'.format(paper_folder, starting_number, year))

    # write xml file
    # with open('xml/s={}_year={}.xml'.format(starting_number, year), 'w', encoding='utf-8') as f:
        # f.write(response.text)

    # search meatadata API
    # meta = scrap_spr_meta(doi)
    # joblib.dump(meta, 'files/meta.sav')
    






