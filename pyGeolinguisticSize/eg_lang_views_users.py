# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
import pandas as pd
import pyGeolinguisticSize

## Target l_codes
#interpolation
panel_x=pyGeolinguisticSize.size_l_wiki.loc[:,:,:].apply(pd.Series.interpolate, axis=1)

x_order=[u'IPop', u'LP',u'PPPGDP']#, u'IPv4', 'IH' ]
df_x=panel_x.loc[x_order,:,2013]
df_y=pyGeolinguisticSize.wiki_pageviews[['pgviews']]

print "difference:",len(set(df_y.index).difference(set(df_x.index)))
print "intersection:",len(set(df_y.index).intersection(set(df_x.index)))

## Considered languages list based on intersection
l_code_target=list(set(df_y.index).intersection(set(df_x.index)))

## All possible independent variables
x_possible = x_order
y_possible=['pgviews'] #'pgedits','mobile'  in the future

#df_draw

## Observartion from Wikipedia, limiting to the intersection of laugage codes
observed=df_y.loc[l_code_target]
o=df_x.loc[l_code_target]

## Constructing an integrated dataframe df_all
df_=df_y.join(df_x).dropna(axis=0, thresh=2).reset_index()##
d=pd.melt(df_, id_vars=['l_code','pgviews'], var_name="x_attr" ,value_name="x")
d=pd.melt(d, value_vars=['pgviews'],id_vars=['l_code','x_attr', 'x'], var_name="y_attr" ,value_name="y")
print len(d) 
df_all=d
df_all['y']=df_all['y'].astype(object)#formatting output

df_all['l_code']=[str(x) for x in df_all['l_code']]  #Unknown bug here in l_code, lxml related  AssertionError: invalid Element proxy at 185990984
df_all=df_all[df_all.x>0]                            #Remove x values= zero

# Customizing figures
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams["axes.labelsize"] = 16.0
mpl.rcParams["axes.grid"] = True

mpl.rcParams["font.size"] = 15.0#

font_size_geom_text = 15.0

mpl.rcParams["axes.edgecolor"] = "black" 
mpl.rcParams["axes.labelcolor"] = "black"
mpl.rcParams["grid.color"] = "grey" # or  whatever you want

mpl.rcParams["figure.subplot.wspace"] = 0.03
mpl.rcParams["figure.figsize"] = [6,6.5]
mpl.rcParams["figure.subplot.left"] = 0.18
mpl.rcParams["figure.subplot.bottom"] = 0.168
mpl.rcParams["figure.subplot.right"] = 0.95
mpl.rcParams["figure.subplot.top"] = 0.98

import matplotlib.pyplot as plt


## plotting
from ggplot import *
from scipy import stats

import string
allTheLetters = string.lowercase
counting=0

import math
import statsmodels.api as sm
def sm_lm(x,y):
    X = sm.add_constant(x)
    model = sm.OLS(y,X)
    results = model.fit()
    return results.predict()



timeperiod=pyGeolinguisticSize.wiki_pageviews['timeperiod'][0]
for i,x_name in enumerate(x_possible):      #x_name='PPPGDP'
    for j,y_name in enumerate(y_possible):  #y_name='pgviews'

        df_draw=df_all[(df_all.x_attr==x_name) &(df_all.y_attr==y_name)].copy()

        df_size_dx=pd.algos.kth_smallest(df_draw['x'].values.astype(float), len(df_draw['x'].values) - 1)  #1 all   3 minus the biggest 2
        #df_draw['x'].quantile(q=.88)#max()*.5#.quantile(q=.88)
        df_size_dy=pd.algos.kth_smallest(df_draw['y'].values.astype(float), len(df_draw['x'].values) - 1)  #1 all   3 minus the biggest 2 
        #df_draw['y'].quantile(q=.88)#max()*.5#.quantile(q=.88)

        #slope of the expected value line, using the first value
        #slope_=d_perc[y_name][dict_size_rv[x_name]][df_draw['ISO'].values[0]]/df_size[x_name][df_draw['ISO'].values[0]]

        df_draw=df_draw.set_index('l_code')
        p_d = ggplot(aes(x='x', y='y', label=list(df_draw.index)), data=df_draw)
        ##Detail plotting: xlim setting            ylim(0,df_size_dy)+\

        
#           geom_abline(intercept=0, slope=slope_, color='red', linetype='dotted')+\
        p=p_d+geom_point()+\
            geom_text(aes(hjust = 0, vjust = 0, size=font_size_geom_text, color='darkblue'))+\
            geom_smooth(aes(x='x', y='y'), method='lm', se=False, color='grey')+\
            ylim(0,df_size_dy*1.05)+\
            xlim(0,df_size_dx*1.08)+\
            labs(x = x_name.replace("_"," ")+"\n("+allTheLetters[counting]+")", \
            y = y_name.replace("_"," ").capitalize() + ":" + timeperiod + "(Millions)")+\
            theme_matplotlib()+ theme(axis_text_x  = element_text(size=font_size_geom_text*0.8, angle = 30, hjust = 1))
            #theme_bw()+ theme(axis_text_x  = element_text(size=font_size_geom_text*0.8, angle = 30, hjust = 1))
            #labs(x = "Size Indicators: \n"+x_name.replace("_"," "), y = "Cyber Incidents: "+y_name.replace("_"," ")) +\

        counting=counting+1
        
        df_draw['y_est']=sm_lm(df_draw.x.values, df_draw.y.values)
        df_draw['y_deviation']=(df_draw.y-df_draw.y_est)
        df_draw['y_deviation_perc']=(df_draw.y-df_draw.y_est)/df_draw.y_est

        dfo=dict()

        dfo[1]=df_draw.sort(['y',], ascending=[0,])[['y', 'y_est','y_deviation_perc']]
        dfo[2]=df_draw.sort(['y_deviation',], ascending=[0,])[['y', 'y_est','y_deviation']]
        dfo[3]=df_draw.sort(['y_deviation_perc',], ascending=[0,])[['y', 'y_est','y_deviation_perc']]
        dfo[1]['ranking']=[x+1 for x in range(len(dfo[1]))]
        dfo[2]['ranking']=[x+1 for x in range(len(dfo[2]))]
        dfo[3]['ranking']=[x+1 for x in range(len(dfo[3]))]


        for i,ll in enumerate(['y','y_deviation','y_deviation_perc']):
            dfo[i+1][ll] = dfo[i+1][ll].map(lambda x: '%0.3f' % x)

        fn="Dt_{0}_{1}_before.tsv".format(y_name,x_name)
        dfo[1].to_csv(fn, sep='\t', float_format='%.3f',index_label="l_code")
        fn="Dt_{0}_{1}_after_absolute.tsv".format(y_name,x_name)
        dfo[2].to_csv(fn, sep='\t', float_format='%.3f',index_label="l_code")
        fn="Dt_{0}_{1}_after.tsv".format(y_name,x_name)
        dfo[3].to_csv(fn, sep='\t', float_format='%.3f',index_label="l_code")
        
        fn="Dt_{0}_{1}.png".format(y_name,x_name)
        print "debug::", allTheLetters[counting-1], ", filename:",fn #dict_size_rv[x_name]

        ggsave(p, fn)#dict_size_rv[x_name]

         
