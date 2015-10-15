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

##>>> pyCountrySize.LP['TWN']
##23.374000000000002
##>>> pyCountrySize.IPop['TWN']
##18.699999999999999

d['LP_c']=[pyCountrySize.LP.get(x,None) for x in d['ISO'].values]
d['IPop_c']=[pyCountrySize.IPop.get(x,None)  for x in d['ISO'].values]
d['PPPGDP_c']=[pyCountrySize.PPPGDP.get(x,None)  for x in d['ISO'].values]

## pre-processing
d['populationPercent']=[float(x)/100.0 for x in d['populationPercent']]

d['LP']=d['LP_c']*d['populationPercent']
d['IPop']=d['IPop_c']*d['populationPercent']
d['PPPGDP']=d['PPPGDP_c']*d['populationPercent']

d['c']=d.type+"-"+d.c_code

df["t"]["c_name"]=df["t"]['comments']


d.to_csv("territory_language.tsv", sep="\t", float_format='%4.4f', encoding='utf8',  index_label=False, index=False)
d.to_pickle('size.pkl')

## Language names
dict_langname=dict(zip(list(d[['type','l_name']].set_index('type').index.values), list(d[['type','l_name']].set_index('type').l_name.values)))


##
d.query('(type == "zh_Hant")')['PPPGDP']

#pivot_table(d, values='PPPGDP', index=['type'], columns=['c_code'], aggfunc=np.sum)

list_indicators=['LP','IPop','PPPGDP']

grouped = d.groupby(['type', 'geo'])


summary_geoling=d.groupby(['type', 'geo']).sum()

summary_ling=d.groupby(['type']).sum()[ list_indicators]

summary_geoling.sort(['PPPGDP', 'LP'], ascending=[0, 0])
summary_ling.sort(['PPPGDP', 'LP'], ascending=[0, 0])

print (summary_ling.IPop['zh_Hans']+summary_ling.IPop['zh_Hant']-summary_ling.IPop['en'])

dfw=summary_geoling.IPop[["en","zh_Hans","zh_Hant"]].copy()
dfw.sort(ascending=False)
dfw=dfw.reset_index()
dfw=dfw.fillna(0)
dfw["c_name"]=[df["t"].c_name[x] for x in dfw['geo']]
dfw["g_sum"]=dfw.groupby(["type"]).transform(sum)
dfw.columns=['Language',"Country", "Internet Population", "Country Name", "IPop"]
#Index([u'type', u'geo', u'IPop', u'c_name', u'g_sum'], dtype='object')
dfw[['Language',"Country", "Country Name", "Internet Population", "IPop"]].sort(["IPop","Internet Population"],ascending=False).to_csv("output_en_zh_IPop.tsv", sep="\t", float_format='%4.2f')


dfw=summary_geoling.PPPGDP[["en","zh_Hans","zh_Hant"]].copy()
dfw.sort(ascending=False)
dfw=dfw.reset_index()
dfw=dfw.fillna(0)
dfw["c_name"]=[df["t"].c_name[x] for x in dfw['geo']]
dfw["g_sum"]=dfw.groupby(["type"]).transform(sum)
dfw.columns=['Language',"Country", "Economy Size PPPGDP", "Country Name", "PPPGDP"]
#Index([u'type', u'geo', u'IPop', u'c_name', u'g_sum'], dtype='object')
dfw=dfw[['Language',"Country", "Country Name", "Economy Size PPPGDP"]].sort(["Economy Size PPPGDP",'Language',"Country"],ascending=[False, True, True])
dfw.reset_index()
dfw.index=index=[1+x for x in dfw.index]
dfw.to_csv("output_en_zh_PPPGDP.tsv", sep="\t", float_format='%4.2f')



top20_lang_IPop=summary_ling.sort(['IPop', 'PPPGDP'], ascending=[0, 0])[0:20]
top20_lang_IPop["Language"]=[dict_langname[x] for x in top20_lang_IPop.index]
top20_lang_IPop.columns=["Population", "Internet Population", "Economy PPPGDP", "Language Name"]
top20_lang_IPop[["Language Name","Internet Population", "Economy PPPGDP", "Population"]].sort(["Internet Population", "Economy PPPGDP"],ascending=False).to_csv("top20_lang_IPop.tsv", sep=",", float_format='%4.2f')
top20_lang_IPop[["Language Name","Economy PPPGDP", "Population", "Internet Population"]].sort(["Economy PPPGDP", "Population"],ascending=False).to_csv("top20_lang_PPPGDP.tsv", sep=",", float_format='%4.2f')
top20_lang_IPop[["Language Name","Population","Internet Population","Economy PPPGDP"]].sort(["Population","Internet Population"],ascending=False).to_csv("top20_lang_LP.tsv", sep=",", float_format='%4.2f')


Ipop2013=summary_geoling["IPop"].copy()
Ipop2013.sort(ascending=False)

Ipop2013drop=Ipop2013.dropna()
Ipop2013drop.groupby(level=0).transform(sum)
Ipop2013drop['a_bsum'] = Ipop2013drop.groupby(level=0).transform(sum)



exit()

## Adding index points to the dataframe    'ISO', 'Subject'
df.set_index(['ISO'], inplace=True)

from os.path import basename, join, splitext
df.to_pickle(join('', splitext(basename(file_name))[0] + "." + filename_suffix))
