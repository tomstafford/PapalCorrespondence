#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 07:17:17 2020

Messy notes on how to do this geocoding for when the time comes

@author: tom
"""
# This might help when the time comes https://www.wikidata.org/wiki/Wikidata:Tools/For_programmers

# https://towardsdatascience.com/where-do-mayors-come-from-querying-wikidata-with-python-and-sparql-91f3c0af22e2

#Note that you can test and play with each query at https://query.wikidata.org/.

import pandas as pd
from collections import OrderedDict


import requests

url = 'https://query.wikidata.org/sparql'
query = """
SELECT 
  ?countryLabel ?population ?area ?medianIncome ?age
WHERE {
  ?country wdt:P463 wd:Q458.
  OPTIONAL { ?country wdt:P1082 ?population }
  OPTIONAL { ?country wdt:P2046 ?area }
  OPTIONAL { ?country wdt:P3529 ?medianIncome }
  OPTIONAL { ?country wdt:P571 ?inception. 
    BIND(year(now()) - year(?inception) AS ?age)
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

query = """
SELECT DISTINCT ?settlement ?name ?coor

WHERE

{

  

   ?subclass_settlement wdt:P279+ wd:Q486972 .

   ?settlement wdt:P31 ?subclass_settlement ;

               wdt:P625 ?coor ;

                rdfs:label ?name .

   FILTER regex(?name, "Antwerp", "i")


}
"""

r = requests.get(url, params = {'format': 'json', 'query': query})
data = r.json()




countries = []
for item in data['results']['bindings']:
    countries.append(OrderedDict({
        'country': item['countryLabel']['value'],
        'population': item['population']['value'],
        'area': item['area']['value'] 
            if 'area' in item else None,
        'medianIncome': item['medianIncome']['value'] 
            if 'medianIncome' in item else None,
        'age': item['age']['value'] 
            if 'age' in item else None}))
    
df = pd.DataFrame(countries)
df.set_index('country', inplace=True)
df = df.astype({'population': float, 'area': float, 'medianIncome': float, 'age': float})
df.head()



