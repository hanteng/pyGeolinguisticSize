# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。

import pyCountrySize
import logging

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

## setting up to run from the script directory itself
import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

Config = configparser.ConfigParser()  
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
    df[i]=pd.io.pickle.read_pickle(os.path.join(dir_outcome,list_df[i]))
    logging.warning ( "df[\'{0}\'] has the following columns:".format(i)  )
    logging.warning ( "{}".format(list (df[i].columns.values) ))
 

d=df['tl'].copy()
d['ISO']=[df['m']['alpha3'][x] for x in df['tl']['c_code'].values]

##>>> pyCountrySize.sizec.items
##Index([u'IH', u'IPop', u'IPv4', u'LP', u'PPPGDP'], dtype='object')

## pre-processing
d['populationPercent']=[float(x)/100.0 for x in d['populationPercent']]
print ("There are {0} territory-language pairs".format(len(d))) #1261
d=d.set_index(['type','c_code'])

df["t"]["c_name"]=df["t"]['comments']

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
    dd[indicator]=d.join(pyCountrySize.sizep[indicator][list(range(2000,2013+1))], how="left", on=['ISO'])
    a=np.array(dd[indicator][list(range(2000,2013+1))])
    b=np.array(dd[indicator]['populationPercent'])
    c=a.transpose()*b
    dd[indicator][list(range(2000,2013+1))]=c.transpose()

    # adding indicators to d
    label = indicator + "_geo"
    pyCountryObject = eval ("pyCountrySize." + indicator)
    d[label] = [pyCountryObject.get(x, None) for x in d['ISO'].values]
    d[indicator] = d[label] * d['populationPercent']
    
tl_panel=pd.Panel(dd)

tl_panel.to_pickle(os.path.join(dir_outcome,fn_output))

## Check Values
#w=tl_panel['IPop']
#>>> w.loc[(w.index.get_level_values('type') =='zh_Hans') & (w.index.get_level_values('c_code') =='CN')][2013]
#type     c_code
#zh_Hans  CN        560.9053

# Generate size_geolinguistic.tsv
d=d.reset_index()
d['tag']=d.type + "-" + d.c_code
## Geo/Country names
##>>> df['t']['c_name']['TW']
##'Taiwan'
d['geo_name']=[df['t']['c_name'][x] for x in d['geo']]

list_indicators=['LP','IPop','PPPGDP', 'IPv4']
list_CLDRmeta=['tag','type','l_name','ISO','geo','geo_name','officialStatus','references']

output_selected=d[list_CLDRmeta+list_indicators]

#grouped = d.groupby(['type', 'geo'])
#summary_geoling=d.groupby(['type', 'geo']).sum()
#summary_geoling.sort(['PPPGDP', 'LP'], ascending=[0, 0])

#output sort by type/lang and geo
simplified = output_selected.sort(['type','geo']).set_index(['tag'])
outputfile = "size_geolinguistic.tsv"
simplified.to_csv ( os.path.join(dir_outcome, outputfile), sep="\t", float_format="%4.4f", encoding = "utf8")
simplified.to_pickle ( os.path.join(dir_outcome, outputfile.replace(".tsv",".pkl") )   )


