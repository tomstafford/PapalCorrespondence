#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 09:37:59 2020

@author: tom

Finished July 2020 - first tranche of requests from GL and CW

"""
import os #file and folder functions
import socket #to get host machine identity
import pandas as pd #dataframes
import numpy as np #number functions
import geopandas as gpd
import matplotlib.pyplot as plt
import mplleaflet
from shapely.geometry import Point
from ast import literal_eval
from scipy import ndimage

#bespoke functions
from geofuncs import haversine,haversine_intermediate,monthdays,reignday,calctravel

#test which machine we are on and set working directory
if 'tom' in socket.gethostname():
    os.chdir('/home/tom/t.stafford@sheffield.ac.uk/A_UNIVERSITY/toys/MappingPapalLetters')
else:
    print("I don't know where I am! ")
    print("Maybe the script will run anyway...")

MAKEDF = True
MAKEFRAMES = True

speed = 40 # km per day
delay = 5 #10s of a second per fram


if MAKEDF:


    #import data, downloaded from google sheets (and at some point run through geolocation)
    df = pd.read_csv('data/gregory_vii.csv')
    
    # split so coded for positively addressed to this audience (not exclusively addressed)
    df['clerical']=df['clerical/secular'].str.contains('c')==True
    df['secular']=df['clerical/secular'].str.contains('s')==True
    
    #round up 'half' years
    df['year'] = df['year'].apply(lambda x :x.replace('2/3','3'))
    df['year'] = df['year'].apply(lambda x :x.replace('1/2','2'))
    df['year'] = df['year'].astype(int)
    
    #now make df for plotting
    
    lats = []; lons = [];nams = []
    year = []; month =[]; day = []
    cles = [];secs = []
    pope_lats = []; pope_lons = []
    
    for index, row in df.iterrows():        
        
        try:
            
            latvals=literal_eval(row['lat'])
            lonvals=literal_eval(row['lon'])
            namvals=row['place'].split(',')
    
            for lat,lon,nam in zip(latvals,lonvals,namvals):
                lats.append(lat)
                year.append(row['year'])
                month.append(row['month'])
                day.append(row['day'])
                cles.append(row['clerical'])
                secs.append(row['secular'])
                lons.append(lon)
                nams.append(nam.strip())
                pope_lats.append(row['pope_lat'])
                pope_lons.append(row['pope_lon'])
        except:
            print(row['place'])
    
    
    df2 = pd.DataFrame({'year': pd.Series(year),
                        'month': pd.Series(month),
                        'day': pd.Series(day),
                        'place': pd.Series(nams),
                        'lat': pd.Series(lats),
                        'lon': pd.Series(lons),
                        'clerical': pd.Series(cles),
                        'secular': pd.Series(secs),
                        'pope_lat': pd.Series(pope_lats),
                        'pope_lon': pd.Series(pope_lons)
                        })
    
    #https://gis.stackexchange.com/questions/147156/making-shapefile-from-pandas-dataframe
    # combine lat and lon column to a shapely Point() object
    df2['geometry'] = df2.apply(lambda x: Point((float(x.lon), float(x.lat))), axis=1)
    
    df2['month']=df2['month'].apply(lambda x: str(x).split('/')[0].strip())
    
    d = {'month': ['December','January','February','March','April','May','June','July','August','September','October','November'], 'season': ['winter', 'winter','winter','spring','spring','spring','summer','summer','summer','autumn','autumn','autumn']}
    seasons=pd.DataFrame(data=d)
    
    df2=df2.merge(seasons, how='left')
    
    df2['month_n']=pd.to_datetime(df2.month,format='%B',errors='coerce').dt.month
    
    df2 = gpd.GeoDataFrame(df2, geometry='geometry')
        
    df2['distance']=df2.apply(lambda x: haversine(x['lat'],
                                  x['lon'],
                                  x['pope_lat'],
                                  x['pope_lon'])/1000,axis=1) #in km
    
 
    
    df2['reigndaysent']=df2.apply(lambda x: reignday(x['year'],x['month_n'],x['day']),axis=1)

    df3=pd.DataFrame(columns=['letter','day','show_lat','show_lon','f'])
    
    
    for index, row in df2.iterrows():
        for day in range(4414):
            #calc lat and lon depending on whether letter has been sent, speed, etc
            daysent=row['reigndaysent']
            origin=(row['pope_lat'],row['pope_lon'])
            destination=(row['lat'],row['lon'])
            show_lat,show_lon,f=calctravel(origin, destination,speed,day,daysent)
            df3=df3.append({'letter':index, 'day':day, 'show_lat':show_lat, 'show_lon':show_lon, 'f':f},ignore_index=True)

    df2.to_csv('processed_data/letterdf.csv')                
    df3.to_csv('processed_data/animdf.csv')

else:
    
    df2=pd.read_csv('processed_data/letterdf.csv')
    df3=pd.read_csv('processed_data/animdf.csv')
         



    
    
'''
---------------------------------------------> MAKING MAPS
'''




#https://geopandas.org/mapping.html#mapping-tools
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))


  
    
BORDERS=True

if BORDERS:
    bordercolour='black'
    filename='map1_borders.png'
else:
    bordercolour='grey'
    filename='map1_noborders.png'

bordercolour='black'

fig, ax = plt.subplots()
ax.set_aspect('equal')
world.plot(ax=ax, cmap=None,color='grey', edgecolor=bordercolour)
df2['geometry'].plot(ax=ax, marker='o', color='black', markersize=25,label='secular')
plt.xlim([-10,35])
plt.ylim([35,60])
plt.title('Correspondence of Pope Gregory VII: ' + str(len(df2)) + ' letters, ' + str(df['year'].min()) + ' to ' + str(df['year'].max()))
plt.annotate('@tomstafford, @Pseudo_Isidore & @geolitchy',fontsize=4,xy=(23,36),bbox=dict(boxstyle='round,pad=0.5', fc='lightgray', alpha=0.8,lw=0))

plt.savefig('plots/'+filename,dpi=320,bbox_inches='tight')




'''
----------------------------> RELIEF + SEASONS
'''
#data
#https://www.naturalearthdata.com/downloads/10m-raster-data/10m-gray-earth/

#how to
#http://darribas.org/gds15/content/labs/lab_03.html

import rasterio
import numpy as np


euro_bounds=(-10,43,35,65)

# Reading in data
source = rasterio.open('mapfiles/GRAY_LR_SR_W/GRAY_LR_SR_W.tif', 'r')
pix = np.squeeze(np.dstack((source.read())))

pix.shape # (8100, 16200)

bounds = (source.bounds.left, source.bounds.right, \
          source.bounds.bottom, source.bounds.top)
# (-180.0, 179.99999999996396, -89.99999999998198, 90.0)

ratio_leftright=16200/360.0
ratio_updown=8100/180.0

imbounds=[(16200/2)-10*ratio_leftright, (16200/2)+43*ratio_leftright, (90-35)*ratio_updown,(90-65)*ratio_updown]

imbounds=tuple(int(i) for i in imbounds)

#imbounds=(8100,16200,0,4050)

#f = plt.figure(figsize=(12, 12))
f = plt.figure()
ax = f.add_subplot(1, 1, 1)
ax.set_aspect('equal')

ax.imshow(pix[imbounds[3]:imbounds[2],imbounds[0]:imbounds[1]], extent=euro_bounds,cmap='gray')

for seasonname,seasoncolour in zip(['winter','spring','summer','autumn'],['blue','yellow','red','sienna']):
    df2[df2['season']==seasonname]['geometry'].plot(ax=ax, marker='+', color=seasoncolour, markersize=15,label=seasonname)

ax.legend(loc=0)
ax.set_axis_off()
plt.savefig('plots/map1_relief.png',dpi=320,bbox_inches='tight')

df2.groupby('season')['year'].count() #for interest
      
plt.clf()
for year in np.sort(df2['year'].unique()):
    try:
        df2[df2['year']==year].groupby('month_n')['place'].count().plot(label=str(year))
    except:
        print("not for " + str(year))
    
plt.xlabel('Month number')
plt.ylabel('Number of letters')
plt.title('Different lines for different years')
plt.savefig('plots/letters_per_month.png',bbox_inches='tight')


plt.clf()
(df2.groupby('month_n')['distance'].sum()/df2.groupby('month_n')['place'].count()).plot.bar(rot=35)
plt.xlabel('Month')
plt.ylabel('Average crow-flies distance of letter (km)')
plt.savefig('plots/map1_avdistance.png',bbox_inches='tight')


'''
----------------------------> FLYING LETTERS
'''
    
    
if MAKEFRAMES:
#base map

    for day in range(0,4414):
        plt.close('all')
        f = plt.figure()
        ax = f.add_subplot(1, 1, 1)
        ax.set_aspect('equal')
        
        ax.imshow(pix[imbounds[3]:imbounds[2],imbounds[0]:imbounds[1]], extent=euro_bounds,cmap='gray')
    
        lats=df3[df3['day']==day][['show_lat','show_lon']].dropna()['show_lat'].values
        lons=df3[df3['day']==day][['show_lat','show_lon']].dropna()['show_lon'].values
    
        ax.plot(lons,lats,'o',ms=4,color='red')
        plt.title('Correspondence of Pope Gregory VII')
        plt.annotate('@tomstafford, @Pseudo_Isidore & @geolitchy',fontsize=4,xy=(28,36),bbox=dict(boxstyle='round,pad=0.5', fc='lightgray', alpha=0.8,lw=0))
        plt.annotate('Day ' + str(day).zfill(4),fontsize=14,xy=(-8,61),bbox=dict(boxstyle='round,pad=0.05', fc='white', alpha=0.8,lw=0))
        plt.savefig('postal/day_'+str(day).zfill(5))



#os.system('ffmpeg -framerate 24 -pattern_type glob -i 'postal/*.png' plots/video.mp4')