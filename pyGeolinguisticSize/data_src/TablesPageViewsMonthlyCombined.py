# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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
fn_output = Config.get("Filename",'wiki_pageviews')
data_src=Config.get("Source", 'wiki_pageviews')
fn_operating=os.path.join(dir_source,data_src.split('/')[-1])

## Webdriver API required for javascrpt-heavy web pages
from lxml.html import document_fromstring, fromstring, tostring, parse
from io import StringIO, BytesIO
import pandas as pd

XML_encoding="iso-8859-1"

from ftfy import fix_text
import codecs

try:
    with codecs.open(fn_operating, "r", XML_encoding) as f:
        output=f.read()
    tree = fromstring(fix_text(output))
except:
    import requests

    r = requests.get(data_src, stream=True)
    r.raw.decode_content = True

    if not( r.status_code == 200):
        logging.warning ("Downloading the data from {0} failed. Plese check Internet connections.".format(XML_src_url))
        exit()

    XML_src=r.content
    with codecs.open(fn_operating, "w", XML_encoding) as f:
        f.write(XML_src.decode(XML_encoding))
        
    tree = fromstring(XML_src)



## Parsing them into dataframe
import pandas as pd

mapping_x_path={\
                "l_code":'''tr/td[5]/a//text()''',\
                "timeperiod":'''td[1]/b//text()''',\
                "pgviews": '''tr/td[11]/text()''',\
                }
#285 //*[@id="table1"]/tbody/tr[4]/td/b/a
#286 //*[@id="table1"]/tbody/tr[13]/td
#285 //*[@id="table1"]/tbody/tr[13]/td/span[2]
outcomes=[]

# Get "l_code" first
list_matched = tree.xpath('//*[@id="table2"]/tbody')#/tbody won't work with the downloaded xml
m=list_matched[0]
i="l_code"
content= m.xpath(mapping_x_path[i])
#len(content)=244
l_code=content
l_code[0]="ALL"


i="pgviews"
content= m.xpath(mapping_x_path[i])
#len(content)=244
pgviews=[float(x.replace(',','')) for x in content]

list_matched = tree.xpath('''//*[@summary="Page header"]//tr[1]/td[1]/b/text()''')
m=list_matched[0]
i="timeperiod"
content= m
timeperiod=content.replace(u'\xa0',u' ')

r={"pgviews":pgviews,"l_code":l_code,"timeperiod":[timeperiod]*len(l_code)}
df=pd.DataFrame(r)


df=df.set_index('l_code')
file_output=os.path.join(dir_outcome,fn_output)
df.to_pickle(file_output)
file_output=file_output.replace(".pkl",".tsv")
df.to_csv(file_output, sep='\t', encoding="utf8", index=True)
