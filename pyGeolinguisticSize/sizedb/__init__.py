# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd
import os

__all__ = ["wiki_sitemap", "wiki_pageviews",\
           "mapping", "langname", "territory", "territory_lang", \
           "size_gl", "size_gl_IPop", "size_l", "size_l_wiki", \
           "simplified"]
__all__ = [str(u) for u in __all__]
_ROOT = os.path.abspath(os.path.dirname(__file__))


from os.path import basename, join, splitext

wiki_sitemap  = pd.read_pickle(os.path.join(_ROOT,"Sitemap.pkl"))
mapping       = pd.read_pickle(os.path.join(_ROOT,"df_codeMappings.pkl"))   #Legacy:mapping.pkl
territory     = pd.read_pickle(os.path.join(_ROOT,"df_territory_basic.pkl"))#Legacy:territory.pkl
territory_lang= pd.read_pickle(os.path.join(_ROOT,"df_territory_lang.pkl"))

# wiki_sitemap df=df.set_index('l_code')   INDEX: Wiki style language codes 
# mapping      df=df.set_index("type")     INDEX: CLDR two-digit ISO country codes
# territory    df=df.set_index("type")     INDEX: CLDR two-digit ISO country codes
# territory_lang  INDEX: serial number, with
####c_code (2 digit country code)
####geo (2 digit country code)
####type (CLDR language code)
# for futher integrations


size_gl       = pd.read_pickle(os.path.join(_ROOT,"_tl_size.pkl"))
##>>> size_gl
##<class 'pandas.core.panel.Panel'>
##Dimensions: 5 (items) x 1261 (major_axis) x 23 (minor_axis)
##Items axis: IH to PPPGDP
##Major_axis axis: (en, AC) to (tn, ZW)
##Minor_axis axis: l_name to 2015


## Slice out IPop for use
size_gl_IPop=size_gl['IPop'].sort(columns=[2013], ascending=False)
#test=size_gl_IPop[2010].copy(deep=True)
#test.sort(ascending=False)

## Language names
langname=size_gl['IPop'].reset_index()[['type','l_name']].drop_duplicates().set_index('type')['l_name']
#>>> langname['fr']
#'French'

## Aggregation results based on languages  _l_size.pkl

try:
    size_l.pd.read_pickle(os.path.join(_ROOT,"_l_size.pkl"))

except:
    list_indicators=size_gl.items   #Legacy: ['IPop','PPPGDP','LP']   
    #indicator='IPop'
    sizel=dict()
    for indicator in list_indicators:
        dfo=size_gl[indicator].reset_index()
        osize_l=dfo[["type"]+list (range(2000,2013+1))].groupby(['type']).sum()
        osize_l["l_name"]=[langname[x] for x in osize_l.index]
        #osize_l.drop(['c_code','populationPercent'], axis=1, inplace=True)
        
        osize_lg=dfo[["type"]+["geo"]].groupby(['type']).sum()
        osize_l["geo"]=[[x[i:i+2] for i in range(0, len(x), 2)] for x in osize_lg.geo]
        #exit()        
        sizel[indicator]=osize_l
        #size_l=size_gl[indicator].groupby(['type']).sum()[list_indicators].sort(columns=['IPop'], ascending=False)

    size_l=pd.Panel(sizel)
    size_l.to_pickle(os.path.join(_ROOT,"_l_size.pkl"))


## Aggregation results based on languages in Wikipedia
size_l_wiki=pd.read_pickle(os.path.join(_ROOT,"wiki_lang_panel_aggregated.pkl"))

## Simplified results
simplified=pd.read_pickle(os.path.join(_ROOT,"size_geolinguistic.pkl"))


'''
>>> size_l_wiki.loc[:,:,2013].head()
        IH        IPop IPv4         LP    PPPGDP
index                                           
zh     NaN     594.441  NaN   1271.592  16487.45
iu     NaN  0.02530088  NaN  0.0294882  1.275464
mn     NaN    0.951459  NaN   5.364831  49.92671
als    NaN    1.307198  NaN   1.539666  74.89924
az     NaN    11.54916  NaN   28.38094  469.3428

>>> size_l_wiki.loc['IPop',:,:].head()[['geo']+list(range(2000,2013+1))]
                                                     geo        2000  \
index                                                                  
zh     [AU, BN, GB, GF, HK, ID, MO, MY, PA, PF, PH, S...    31.23139   
iu                                              [CA, CA]  0.01320641   
mn                                      [MN, RU, MN, RU]  0.05592889   
als                                         [CH, FR, LI]   0.4815436   
az                              [IR, AZ, RU, AM, AZ, TR]   0.1754967   

             2001        2002          2003         2004          2005  \
index                                                                    
zh       44.19375    70.60649       91.6723     106.4931      123.2236   
iu     0.01566192  0.01619877    0.01704233   0.01767301     0.0193844   
mn     0.07469757  0.09346433  0.0003592577  0.000554754  0.0006541379   
als     0.6179152   0.6985425     0.7690295    0.8146932     0.8615768   
az      0.2835659    1.195153      1.192338     1.318835      2.118526   

               2006        2007        2008        2009        2010  \
index                                                                 
zh         149.3169    216.5657    297.1577    375.4637    443.4091   
iu       0.01978284  0.02019758  0.02138945  0.02265106  0.02290602   
mn     0.0007721172   0.4388074   0.4858311   0.5053024    0.524522   
als        0.939457    1.067281    1.121284    1.158199    1.225288   
az         2.614118    3.047691    3.473452    4.588354    6.988492   

             2011        2012        2013  
index                                      
zh       494.5442    547.4921     594.441  
iu     0.02391605  0.02419423  0.02530088  
mn      0.6498466   0.8690564    0.951459  
als      1.251201    1.283024    1.307198  
az       8.593783    10.30142    11.54916
'''


wiki_pageviews=pd.read_pickle(os.path.join(_ROOT,"TablesPageViewsMonthlyCombined.pkl"))
##>>> pgviews_wiki.head()
##        pgviews timeperiod
##l_code                    
##ALL       19629   Feb 2015
##en         9327   Feb 2015
##ja         1444   Feb 2015
##es         1357   Feb 2015
##ru         1275   Feb 2015




