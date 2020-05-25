#Assumes python3
#You need to load the conda environment in the terminal,

#>conda env create --name mapping --file mapping.yml
#>conda activate mapping

import socket #to get host machine identity
import pandas as pd #dataframes
import os #file and folder functions
import numpy as np #number function
import datetime #date functions
import matplotlib.pyplot as plt #plotting function
import cartopy.crs as ccrs
import cartopy
import cartopy.feature as cfeature

df=pd.read_csv('data/gregory_vii_book1.csv') # this is the form we expect to get the data
df.head()


df_places=pd.read_csv('data/places.csv')
df_locs=df.merge(df_places,how='left')

df_locs=df_locs.merge(df_places,how='left',left_on='Location of pope',right_on='place',suffixes=('','_pope'))
df_locs.drop(columns=['place_pope'],inplace=True)
df_locs.head()

#Cribbing from
#https://uoftcoders.github.io/studyGroup/lessons/python/cartography/lesson/
#and
#https://matthewkudija.com/blog/2018/04/21/travel-map-cartopy/

def new_base(df):
    #Long/Lat boundaries of Europe!
    top=60
    bottom=35
    left=-10
    right=35
    
    #Map projection
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # [lon_min, lon_max, lat_min, lat_max]
    ax.set_extent([left,right,bottom,top], crs=ccrs.PlateCarree())
    
    # add and color high-resolution land
    OCEAN_highres = cfeature.NaturalEarthFeature('physical', 'ocean', '50m',
                                                edgecolor='#B1B2B',
                                                facecolor='white',
                                                linewidth=.1
                                               )
    
    
    
    LAND_highres = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                                 facecolor='green',
                                                 linewidth=.1
                                             )    

    #This works, sort of, but doesn't add much at this scale
    RIVERS_highres = cfeature.NaturalEarthFeature('physical', 'rivers_lake_centerlines', '50m',
                                                  linewidth=0.1)
    

    ax.add_feature(OCEAN_highres, zorder=0, 
                   edgecolor='#B1B2B4', facecolor='#7f7f7f')
    

    ax.add_feature(LAND_highres,zorder=0,facecolor='white')
                       
    ax.add_feature(RIVERS_highres,facecolor='None',edgecolor='lightblue')
    


# -----------------> SET UP MAP

plt.clf()
new_base(df_locs)

# Location of Rome
rome_lati=41.9028
rome_long=12.4964

# Map parameters
marksize=16
popemarksize=3
popealpha=0.75

# -----------------> PUT ON LETTER DATA ON MAP

#Loop through dataset of letters
for index, row in df_locs.iterrows():
    colorcode='grey' #default
    if row['clerical/secular']=='s':
        colorcode='red'
    if row['clerical/secular']=='c':
        colorcode='blue'
        
    x=row['longitude'];y=row['latitude']
    pope_long=row['longitude_pope'];pope_lati=row['latitude_pope']
    plt.plot([pope_long,x],[pope_lati,y],lw=0.25,alpha=0.25,color='black')        
    plt.plot(x,y,'.',alpha=0.25,ms=marksize,color=colorcode)
    plt.plot(pope_long,pope_lati,'.',ms=popemarksize,alpha=popealpha,color='black',marker='^')        
    plt.plot(pope_long,pope_lati,'.',ms=popemarksize-1,alpha=popealpha,color='yellow',marker='^')        
        
    #plt.title(annotext)
    #plt.ylim([46,56])
    #plt.xlim([-4,2])
    


# -----------------> LEGEND AND ANNOTATIONS

plt.title('Papal Correspondence of Gregory VII, book 1')

from matplotlib.patches import Patch

legend_elements = [Patch(facecolor='red', alpha=0.25, label='secular'),
                   Patch(facecolor='blue', alpha=0.25, label='clerical')]

plt.legend(handles=legend_elements, title="Recipient type",loc='upper right')

#show the pope    
popemark_long=27.5;popemark_lat=52

plt.plot(popemark_long,popemark_lat,'.',alpha=1,ms=6,color='black',marker='^')        
plt.plot(popemark_long,popemark_lat,'.',alpha=1,ms=5,color='yellow',marker='^')        
plt.annotate('Pope',fontsize=8,xy=(popemark_long+1.5,popemark_lat-0.4))

plt.annotate('@tomstafford & @Pseudo_Isidore',fontsize=8,xy=(-9,36),bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.8))

plt.savefig('map_book1.png',dpi=320,bbox_inches='tight')

df_locs['recipient'].value_counts()


df_locs['place'].value_counts().head(15)


plt.clf()
new_base(df_locs)

plt.title('Average location of all correspondence')
plt.annotate('@tomstafford & @Pseudo_Isidore',fontsize=8,xy=(-9,36),bbox=dict(boxstyle='round,pad=0.5', fc='gray', alpha=0.8))

center_lat=df_locs['latitude'].mean() #46.10233625
center_long=df_locs['longitude'].mean() #8.2351825

plt.plot(center_long,center_lat,ms=12,color='black',marker='*')
plt.annotate('Domodossola, Italy',fontsize=8,xy=(center_long+0.5,center_lat+0.5))

plt.savefig('map_book1_center.png',dpi=320,bbox_inches='tight')



#Other possible analyses

# repeat recipients
# distance each letter went (and divided by secular clerical)
# timing of letters across the year
