# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
from lxml.html import fromstring, tostring, parse
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
fn_output = Config.get("Filename",'wiki_sitemap')
data_src=Config.get("Source", 'wiki_sitemap')

XML_encoding="iso-8859-1"

fn_operating=os.path.join(dir_source,data_src.split('/')[-1])

try:
    tree = parse(fn_operating)
except:
    XML_src_url=data_src #u'http://stats.wikimedia.org/EN/Sitemap.htm'

    import requests
    r = requests.get(XML_src_url, stream=True)
    r.raw.decode_content = True

    if not( r.status_code == 200):
        logging.warning ("Downloading the data from {0} failed. Plese check Internet connections.".format(XML_src_url))
        exit()

    ##Requests will automatically decode content from the server [as r.text]. ... You can also access the response body as bytes [as r.content].
    XML_src=r.content# r.raw.read()#r.raw#r.text
    #XML_encoding=r.encoding  #'ISO-8859-1'

    import codecs
    with codecs.open(fn_operating, "w", XML_encoding) as file:
        file.write(XML_src.decode(XML_encoding))
        
    tree = fromstring(XML_src)

mapping_x_path={\
                "l_code":'''td[5]/a//text()''',\
                "l_name":'''td[6]/a/text()''',\
                "l_url": '''td[5]/a/@href''',\
                "speakers": '''td[9]//text()''',\
                "editors_per_speaker": '''td[10]//text()''',\
                "usage_views_per_hour": '''td[11]//text()''',\
                "content_articles": '''td[12]//text()''',\
                }

outcomes=[]
list_matched = tree.xpath('//*[@id="table2"]/tbody/tr')
#    print "{0} parsed for {1}".format(len(list_matched), i)
for j,m in enumerate(list_matched):
    r=dict()
    for i in mapping_x_path.keys():
        try:
            content=m.xpath(mapping_x_path[i])[0] 
        except:
            content=u""
        r[i]=content.strip()
    if r['l_code']!="":
        outcomes.append(r)
df=pd.DataFrame(outcomes)


def kMrev(s):
    try:
        n,unit=s.split(u'\xa0')
    except:
        try:
            s=float(s)
            return(s)
        except:
            #print s
            return None
    if unit=="k":
        return float(n)*10**3
    if unit=="M":
        return float(n)*10**6
    
df['speakers']=[kMrev(x) for x in df['speakers']]
df['editors_per_speaker']=[kMrev(x) for x in df['editors_per_speaker']]

import locale
locale.setlocale(locale.LC_NUMERIC, '')
df['usage_views_per_hour']=df[['usage_views_per_hour']].applymap(locale.atof)

import re

df['content_articles']=[re.sub("\D", "", x) for x in df['content_articles'] ]

df=df.set_index('l_code')
file_output=os.path.join(dir_outcome,fn_output)
df.to_pickle(file_output)
file_output=file_output.replace(".pkl",".tsv")
df.to_csv(file_output, sep='\t', encoding="utf8", index=True)
