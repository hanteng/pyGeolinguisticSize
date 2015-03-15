# -*- coding: utf-8 -*-
from __future__ import unicode_literals
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。

from lxml.html import fromstring, tostring, parse
from io import StringIO, BytesIO
import pandas as pd

import os
os.chdir("..")
import ConfigParser
Config = ConfigParser.ConfigParser()
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
    with codecs.open(fn_operating, "r", "utf8") as f:
        output=f.read()
    tree = fromstring(fix_text(output))
except:
    import os
    from selenium import webdriver

    chromedriver = "C:/Python27/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    browser = webdriver.Chrome(chromedriver)
    browser.get(data_src)

    content = browser.page_source.encode(XML_encoding, 'ignore')
    desired_content_is_loaded = False;

    from datetime import datetime
    tstart = datetime.now()
    tdiff=datetime.now()-tstart

    while (tdiff.seconds<5):
        content = browser.page_source
        tdiff=datetime.now()-tstart
        print "{0}\t".format(tdiff.seconds),
              
    browser.quit()

    XML_src=content
    with codecs.open(fn_operating, "w", "utf8") as f:
        f.write(fix_text(XML_src.encode(XML_encoding)))
        
    tree = document_fromstring(XML_src)



## Parsing them into dataframe
import pandas as pd

mapping_x_path={\
                "l_code":'''tr[4]/td/b/a//text()''',\
                "timeperiod":'''td[1]/text()''',\
                "pgviews": '''td/span[2]//text()''',\
                }
#285 //*[@id="table1"]/tbody/tr[4]/td/b/a
#286 //*[@id="table1"]/tbody/tr[13]/td
#285 //*[@id="table1"]/tbody/tr[13]/td/span[2]
outcomes=[]

# Get "l_code" first
list_matched = tree.xpath('//*[@id="table1"]/tbody')#/tbody won't work with the downloaded xml
m=list_matched[0]
i="l_code"
content= m.xpath(mapping_x_path[i])
#len(content)=284
l_code=content

l_code[0]="ALL"

list_matched = tree.xpath('//*[@id="table1"]/tbody/tr[13]')
m=list_matched[0]
i="timeperiod"
content= m.xpath(mapping_x_path[i])
timeperiod=content[0].replace(u'\xa0',u' ')

def convertback(s):
    try:
        n,unit=s.split(u' ')
    except:
        try:
            s=float(s)
            return(s)
        except:
            #print s
            return None
    num=float(n.replace(",",""))
    if unit=="k":
       return num/(10**3)#num*10**3
    if unit=="M":
       return num#num*10**6

i="pgviews"
content= m.xpath(mapping_x_path[i])
#len(content)=285
pgviews=[convertback(x) for x in content]

r={"pgviews":pgviews,"l_code":l_code,"timeperiod":[timeperiod]*285}
df=pd.DataFrame(r)


df=df.set_index('l_code')
df.to_pickle(os.path.join(dir_outcome,fn_output))
