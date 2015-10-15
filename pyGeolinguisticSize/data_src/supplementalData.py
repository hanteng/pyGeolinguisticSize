# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。

# Using the latest CLDR 28
# http://www.unicode.org/cldr/charts/28/
# http://www.unicode.org/cldr/charts/28/supplemental/index.html

from lxml.html import fromstring, tostring, etree
from io import StringIO, BytesIO
import pandas as pd

import logging

import os
os.chdir("..")

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

Config = configparser.ConfigParser()
Config.read("config.ini")

dir_source = Config.get("Directory", 'source')
dir_outcome = Config.get("Directory",'outcome')
fn_suffix = Config.get("Filename",'suffix')
fn_output = [x.strip() for x in Config.get("Filename",'CLDR_suppl').split(",")]
data_src=Config.get("Source", 'CLDR_suppl')

fn_operating=os.path.join(dir_source,data_src.split('/')[-1])

try:
    tree=etree.parse(fn_operating)
except:
    XML_src_url=data_src

    import requests
    r = requests.get(XML_src_url, stream=True)
    r.raw.decode_content = True

    if not( r.status_code == 200):
        logging.warning ("Downloading the data from {0} failed. Plese check Internet connections.".format(XML_src_url))
        exit()

    ##Requests will automatically decode content from the server [as r.text]. ... You can also access the response body as bytes [as r.content].
    XML_src=r.content# r.raw.read()#r.raw#r.text
    XML_encoding=r.encoding  #'ISO-8859-1'

    import codecs
    with codecs.open(fn_operating, "w", XML_encoding) as file:
        file.write(XML_src.decode(XML_encoding))

    tree = etree.XML(XML_src)

import numpy as np

def parse_generic(_xpath, _com):
    list_matched = tree.xpath(_xpath)
    list_processed=[]
    for i,t in enumerate(list_matched):
        data_dict=dict(zip(t.keys(),t.values()))
        if _com=="getnext":
            data_dict['comments']=t.getnext().text.strip()
        else:
            if _com=="getchildren":
                data_dict['comments']=t.getchildren()[0].text.strip()
        #debug
        if i==0:
            logging.warning("Debug: {}".format(data_dict))
        list_processed.append(data_dict)
    df__=pd.DataFrame(list_processed)
    return df__


## Multiple outputs
#>>> fn_output
#['df_territory_basic.pkl', 'df_territory_lang.pkl', 'df_codeMappings.pkl']
#>>> funcs=[x.split(".")[0].split("df_")[1] for x in fn_output]
#['territory_basic', 'territory_lang', 'codeMappings']


def slice_this(x):
    ## To get data:  c_name gdp literacyPercent population
    if x=="territory_basic":
        list_matched = parse_generic('//territoryInfo/territory',"getchildren" ).set_index('type')
        logging.warning ("{0} //territoryInfo/territory parsed".format(len(list_matched)))
        #print list_matched['comments']['AX']
        #print list_matched['comments']['TW']
        #print list_matched
        
        df=pd.DataFrame(list_matched)
        return df


    ## To get data: languagePopulation
    if x=="territory_lang":
        list_matched = tree.xpath('//territoryInfo/territory/languagePopulation')
        logging.warning ("{0} territory//languagePopulation parsed".format(len(list_matched)))

        list_territory=[]
        for t in list_matched:
            data_dict=dict(zip(t.keys(),t.values()))
            if t.getnext()!=[]:
                data_dict['l_name']=t.getnext().text
            data_dict['c_code']=t.getparent().values()[0]
            list_territory.append(data_dict)
            
        df=pd.DataFrame(list_territory)
        df['geo']=df['c_code']
        df.index.names = ['serial']
        #df=df.set_index(['geo',"type"])
        #df.to_pickle('df_territory_lang.pkl')
        return df

        #df_=df.copy()

    
    ## To get data: codeMappings
    if x=="codeMappings":
        list_matched = tree.xpath('//codeMappings/territoryCodes')
        logging.warning ("{0} //codeMappings/territoryCodes parsed".format(len(list_matched)))

        list_territory=[]
        for t in list_matched:
            data_dict=dict(zip(t.keys(),t.values()))
            list_territory.append(data_dict)
            
        df=pd.DataFrame(list_territory)
        df=df.set_index("type")
        #df.to_pickle('df_codeMappings.pkl')
        return df


## Multiple outputs Execution
funcs=[x.split(".")[0].split("df_")[1] for x in fn_output]

for i,func in enumerate(funcs):
    logging.warning ( "-->{2}: Processing for {0} using {1}".format(fn_output[i], func, i))
    df=slice_this(func)
    file_output=os.path.join(dir_outcome,fn_output[i])
    df.to_pickle(file_output)
    file_output=file_output.replace(".pkl",".tsv")
    df.to_csv(file_output, sep='\t', encoding="utf8", index=True)
    print("\n")
