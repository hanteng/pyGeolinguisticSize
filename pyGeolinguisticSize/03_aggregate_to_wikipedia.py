# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
import pyCountrySize
import pandas as pd
import os

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("config.ini")

dir_source = Config.get("Directory", 'source')
dir_outcome = Config.get("Directory",'outcome')
fn_suffix = Config.get("Filename",'suffix')
fn_input = [x.strip() for x in Config.get("Filename",'aggr_wiki_input').split(",")]
fn_output = Config.get("Filename",'aggr_wiki_output')

#fn_output = Config.get("Filename",'output')#lang_wiki_size_mapped.pkl
l_wiki     =pd.read_pickle(os.path.join(dir_outcome,fn_input[0]))
l_cldr  =pd.read_pickle(os.path.join(dir_outcome,fn_input[1]))
set_wikipedia=set(list(l_wiki.index))  #Index([u'simple', u'en', u'zh', u'hi',....
set_unicode=set(list(l_cldr['IPop'].index))  #Index([u'aa', u'ab', u'abr', u'ace',....
print "Length, i.e. # of languages (unicode, wikipedia),",len(set_unicode), len(set_wikipedia)
# Length, i.e. # of languages (unicode, wikipedia), 647 235

# Check an indicator:  Internet Population and Language Population
print l_cldr['IPop'][2013]['zh_Hans']
# 564.215053496
print l_cldr['LP'][2013]['zh_Hans']
# 1229.242578


## Check if the intersection contains exactly the same languages
df =l_wiki
dfl=l_cldr['IPop']

_intersection=set_wikipedia.intersection(set_unicode)
_left=pd.DataFrame(df[u'l_name'][list(_intersection)].drop_duplicates())
#len(_left) 180
_right=pd.DataFrame(dfl[u'l_name'][list(_intersection)].drop_duplicates())
#len(_right) 180
_right.columns=[u"l_name_left"]
_right.index.name='l_code'
table_compare= _left.reset_index().merge(_right.reset_index())
table_compare['exact']=(table_compare['l_name']==table_compare['l_name_left'])
table_compare.to_csv('table_compare_wiki_cldr.tsv', sep="\t", encoding="utf8")
print len(table_compare),len(_left), len(_right), len(_intersection)




## Check if difference matters
_diff=set_wikipedia.difference(set_unicode)
print "Difference", len(_diff)

_left=pd.DataFrame(df[u'l_name'].drop_duplicates())
_right=pd.DataFrame(dfl[u'l_name'].drop_duplicates())

dfdiff=pd.DataFrame(_left['l_name'][_diff]).reset_index()
dfdiff['Note']=[_right['l_name'].get(x, None) for x in dfdiff['l_code']]

dfdiff.to_csv('Diff_to_be_noted.tsv', sep="\t", encoding="utf8")
dfdiffn=pd.read_csv("Diff_noted_manually.tsv", sep="\t", index_col=False)

df_yes_mapping=pd.DataFrame([[dfdiffn.l_code[i],x] for i,x in enumerate(dfdiffn.Note) if "Yes" in x])
df_yes_mapping.columns=['l_code','Note']

df_yes_mapping['items']=[x.replace(" ","").split(":")[1].split("+") for x in df_yes_mapping['Note']]


## Constructing mapping tables
table_compare['items']=[x.split("+") for x in table_compare['l_code']]
df_mapping=pd.concat([df_yes_mapping[['l_code','items']],table_compare[['l_code','items']]])
df_mapping=df_mapping.reset_index()
df_mapping=df_mapping.set_index(['l_code'])

list_size_indicators=list(l_cldr.items)


df_=dict()
#indicator='IPop'
for indicator in list_size_indicators:
    outcome=[]
    for l in list(df_mapping.index):
        series_l=l_cldr[indicator].loc[df_mapping.loc[l]['items']].sum()
        outcome.append(series_l)
    df_con=pd.DataFrame(outcome)
    df_con['index']=df_mapping.index
    df_con=df_con.set_index('index')
    df_[indicator]=df_con


wiki_l_panel=pd.Panel(df_)
wiki_l_panel.to_pickle(os.path.join(dir_outcome,fn_output))



df_mapping[indicator]=outcome



#picked="PPPGDP"#"LP"#"IPop"
for picked in ["PPPGDP","LP","IPop"]:
    outcome=[]
    for l in list(df_mapping.index):
        _sum=0
        for i in df_mapping.loc[l]['items']:
            _sum=_sum+lang[picked].get(i,0)
        outcome.append(_sum)
    df_mapping[picked]=outcome

#df_mapping.to_csv('lang_wiki_size_mapped.tsv', sep="\t", encoding="utf8")
df_mapping.to_pickle('lang_wiki_size_mapped.pkl')


exit()

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
#>>> wiki_l_panel['IPop'][2013]['zh']
#594.4409814824418


