#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 09:37:59 2020

@author: tom
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

#test which machine we are on and set working directory
if 'tom' in socket.gethostname():
    os.chdir('/home/tom/t.stafford@sheffield.ac.uk/A_UNIVERSITY/toys/MappingPapalLetters')
else:
    print("I don't know where I am! ")
    print("Maybe the script will run anyway...")



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
year = []; month =[];cles = [];secs = []

for index, row in df.iterrows():        
    
    try:
        
        latvals=literal_eval(row['lat'])
        lonvals=literal_eval(row['lon'])
        namvals=row['place'].split(',')

        for lat,lon,nam in zip(latvals,lonvals,namvals):
            lats.append(lat)
            year.append(row['year'])
            month.append(row['month'])
            cles.append(row['clerical'])
            secs.append(row['secular'])
            lons.append(lon)
            nams.append(nam.strip())
            
    except:
        print(row['place'])


df2 = pd.DataFrame({'year': pd.Series(year),
                    'month': pd.Series(month),
                    'place': pd.Series(nams),
                    'lat': pd.Series(lats),
                    'lon': pd.Series(lons),
                    'clerical': pd.Series(cles),
                    'secular': pd.Series(secs)
                    })

#https://gis.stackexchange.com/questions/147156/making-shapefile-from-pandas-dataframe
# combine lat and lon column to a shapely Point() object
df2['geometry'] = df2.apply(lambda x: Point((float(x.lon), float(x.lat))), axis=1)

df2['month']=df2['month'].apply(lambda x: str(x).split('/')[0].strip())

d = {'month': ['December','January','February','March','April','May','June','July','August','September','October','November'], 'season': ['winter', 'winter','winter','spring','spring','spring','summer','summer','summer','autumn','autumn','autumn']}
seasons=pd.DataFrame(data=d)

df2=df2.merge(seasons, how='left')

df2 = gpd.GeoDataFrame(df2, geometry='geometry')

#https://geopandas.org/mapping.html#mapping-tools
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))


def heatmap(d, bins=(100,100), smoothing=1.3, cmap='jet'):
    def getx(pt):
        return pt.coords[0][0]

    def gety(pt):
        return pt.coords[0][1]

    x = list(d.geometry.apply(getx))
    y = list(d.geometry.apply(gety))
    heatmap, xedges, yedges = np.histogram2d(y, x, bins=bins)
    extent = [yedges[0], yedges[-1], xedges[-1], xedges[0]]

    logheatmap = np.log(heatmap)
    logheatmap[np.isneginf(logheatmap)] = 0
    logheatmap = ndimage.filters.gaussian_filter(logheatmap, smoothing, mode='nearest')
    
    plt.imshow(logheatmap, cmap=cmap, extent=extent)
    plt.colorbar()
    plt.gca().invert_yaxis()
    plt.show()
    
    
    
    
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






fig, ax = plt.subplots()


# set aspect to equal. This is done automatically
# when using *geopandas* plot on it's own, but not when
# working with pyplot directly.
ax.set_aspect('equal')

world.plot(ax=ax, color=None, edgecolor=None)
df2[df2['secular']]['geometry'].plot(ax=ax, marker='o', color='lightblue', markersize=25,label='secular')
df2[df2['clerical']]['geometry'].plot(ax=ax, marker='+', color='yellow', markersize=25,label='clerical')


plt.xlim([-10,35])
plt.ylim([35,60])
plt.legend(loc=0,title='Recipient')
plt.title('Correspondence of Pope Gregory VII: ' + str(len(df2)) + ' letters, ' + str(df['year'].min()) + ' to ' + str(df['year'].max()))
plt.annotate('@tomstafford, @Pseudo_Isidore & @geolitchy',fontsize=4,xy=(23,36),bbox=dict(boxstyle='round,pad=0.5', fc='lightgray', alpha=0.8,lw=0))

plt.savefig('plots/map_all.png',dpi=320,bbox_inches='tight')

for year in np.sort(df2['year'].unique()):

    fig, ax = plt.subplots()
    
    # set aspect to equal. This is done automatically
    # when using *geopandas* plot on it's own, but not when
    # working with pyplot directly.
    ax.set_aspect('equal')
    
    world.plot(ax=ax, color=None, edgecolor='black')
    df2[df2['year']==year]['geometry'].plot(ax=ax, marker='o', color='black', markersize=25)
      
    plt.xlim([-10,35])
    plt.ylim([35,60])

    plt.title('Correspondence of Pope Gregory VII')
    plt.annotate('@tomstafford, @Pseudo_Isidore & @geolitchy',fontsize=4,xy=(23,36),bbox=dict(boxstyle='round,pad=0.5', fc='lightgray', alpha=0.8,lw=0))
    plt.annotate(str(year),fontsize=24,xy=(-8,56),bbox=dict(boxstyle='round,pad=0.05', fc='white', alpha=0.8,lw=0))
    plt.savefig('plots/yearmap/map'+str(year)+'.png',dpi=320,bbox_inches='tight')




os.system('convert -delay 60 plots/yearmap/*.png plots/yearmap.gif')


'''
----------------------------> RASTER
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

ax.set_axis_off()
plt.savefig('plots/map1_relief.png',dpi=320,bbox_inches='tight')



for year in np.sort(df2['year'].unique()):

    fig, ax = plt.subplots()
    
    # set aspect to equal. This is done automatically
    # when using *geopandas* plot on it's own, but not when
    # working with pyplot directly.
    ax.set_aspect('equal')
    
    ax.imshow(pix[imbounds[3]:imbounds[2],imbounds[0]:imbounds[1]], extent=euro_bounds,cmap='gray')
    df2[df2['year']==year]['geometry'].plot(ax=ax, marker='o', color='black', markersize=25)
      
    plt.xlim([euro_bounds[0],euro_bounds[1]])
    plt.ylim([euro_bounds[2],euro_bounds[3]])
    ax.set_axis_off()

    plt.title('Correspondence of Pope Gregory VII')
    plt.annotate('@tomstafford, @Pseudo_Isidore & @geolitchy',fontsize=4,xy=(28,36),bbox=dict(boxstyle='round,pad=0.5', fc='lightgray', alpha=0.8,lw=0))
    plt.annotate(str(year),fontsize=24,xy=(-8,61),bbox=dict(boxstyle='round,pad=0.05', fc='white', alpha=0.8,lw=0))
    plt.savefig('plots/yearmap/map'+str(year)+'.png',dpi=320,bbox_inches='tight')




os.system('convert -delay 60 plots/yearmap/*.png yearmap.gif')


'''
----------------------------> HEATMAP
'''

for year in np.sort(df2['year'].unique()):
    

    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    plt.xlim([-10,35])
    plt.ylim([35,60])
    plt.title(str(year))
    heatmap(df2[df2['year']==year]['geometry'], bins=50, smoothing=1.5)    
    plt.savefig('plots/heatmap'+str(year)+'.png',dpi=320,bbox_inches='tight')

'''
# 2. Convert plot to a web map:
mplleaflet.show(fig=f,crs=source.crs)

mplleaflet.display(fig=f,crs=source.crs)
mplleaflet.display(fig=f)



pts = gpd.GeoDataFrame.from_file('mapfiles/points_demo.shp')
'''
