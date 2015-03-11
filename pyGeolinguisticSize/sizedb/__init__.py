# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pandas as pd
import os

__all__ = ["mapping", "langname", "territory", "size_gl", "size_l", "pgviews_wiki"]
__all__ = [str(u) for u in __all__]
_ROOT = os.path.abspath(os.path.dirname(__file__))


from os.path import basename, join, splitext

mapping  =pd.read_pickle(os.path.join(_ROOT,"mapping.pkl"))
size_gl  =pd.read_pickle(os.path.join(_ROOT,"size.pkl"))
territory=pd.read_pickle(os.path.join(_ROOT,"territory.pkl"))

size_gl=size_gl.set_index('c').sort(columns=['IPop'], ascending=False)

## Language names
langname=size_gl.reset_index()[['type','l_name']].drop_duplicates().set_index('type')['l_name']
#>>> langname['fr']
#'French'

list_indicators=['IPop','PPPGDP','LP']   
size_l=size_gl.groupby(['type']).sum()[list_indicators].sort(columns=['IPop'], ascending=False)
size_l_wiki=pd.read_pickle(os.path.join(_ROOT,"lang_wiki_size_mapped.pkl")).set_index("l_code").sort(columns=['IPop'], ascending=False)[[u'items']+list_indicators]
pgviews_wiki=pd.read_pickle(os.path.join(_ROOT,"pgviews_wiki.pkl")).set_index("l_code").sort(columns=['pgviews'], ascending=False)
