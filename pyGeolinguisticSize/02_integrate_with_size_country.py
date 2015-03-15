# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。

import pyCountrySize

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("config.ini")

dir_source = Config.get("Directory", 'source')
dir_outcome = Config.get("Directory",'outcome')
fn_suffix = Config.get("Filename",'suffix')
fn_output = Config.get("Filename",'output')

import os.path, glob

import numpy as np
import pandas as pd

list_df={"t":'df_territory_basic.pkl',\
         "tl":'df_territory_lang.pkl',\
         "m":'df_codeMappings.pkl',\
         }
df=dict()

for i in list_df.keys():
    df[i]=pd.io.pickle.read_pickle(os.path.join(dir_source,list_df[i]))
    print "df[\'{0}\'] has the following columns:".format(i)
    print list (df[i].columns.values)
 

d=df['tl'].copy()
d['ISO']=[df['m']['alpha3'][x] for x in df['tl']['c_code'].values]

##>>> pyCountrySize.sizec.items
##Index([u'IH', u'IPop', u'IPv4', u'LP', u'PPPGDP'], dtype='object')

## pre-processing
d['populationPercent']=[float(x)/100.0 for x in d['populationPercent']]
print "There are {0} territory-language pairs".format(len(d)) #1261
d=d.set_index(['type','c_code'])
#>>> d.columns
#Index([u'c_code', u'l_name', u'officialStatus', u'populationPercent', u'references', u'type', u'writingPercent', u'geo', u'ISO'], dtype='object')

dd=dict()
list_size_indicators=list(pyCountrySize.sizep.items)
#>>>len(d)
#1261
#>>> len(d.join(pyCountrySize.sizep[indicator][range(2000,2015+1)], how="left", on=['ISO']))
#1261

#indicator='IPop'
for indicator in list_size_indicators:
    dd[indicator]=d.join(pyCountrySize.sizep[indicator][range(2000,2015+1)], how="left", on=['ISO'])
    a=np.array(dd[indicator][range(2000,2015+1)])
    b=np.array(dd[indicator]['populationPercent'])
    c=a.transpose()*b
    dd[indicator][range(2000,2015+1)]=c.transpose()
tl_panel=pd.Panel(dd)

tl_panel.to_pickle(os.path.join(dir_outcome,fn_output))

## Check Values
#w=tl_panel['IPop']
#>>> w.loc[(w.index.get_level_values('type') =='zh_Hans') & (w.index.get_level_values('c_code') =='CN')][2013]
#type     c_code
#zh_Hans  CN        560.9053


