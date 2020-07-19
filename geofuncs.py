#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 08:00:42 2020

@author: tom

functions for mapping maps (and deriving the df which make maps)

"""

import numpy as np

def haversine(lat1,lon1,lat2,lon2):
    '''use the haversine formula for the crow flies distance between two points
    # cribbed from https://www.movable-type.co.uk/scripts/latlong.html
    
    assumes inputs in decimal degrees latitude and longtitude
    '''

    R = 6371e3 #// radius of earth in metres
    
    try:
        start_lat = lat1 * np.pi/180 #tarting lat in radians  - phi
        end_lat = lat2 * np.pi/180 #end lat in radians
        delta_lat = (lat2-lat1) * np.pi/180 #
        delta_lon = (lon2-lon1) * np.pi/180 # - lambda
    
        a = (np.sin(delta_lat/2) * np.sin(delta_lat/2)) + \
            np.cos(start_lat) * np.cos(end_lat) * \
            np.sin(delta_lon/2) * np.sin(delta_lon/2)
            
        c = 2 * np.arctan2(np.sqrt(a),np.sqrt(1-a))
        
        d = R * c #in metres
        
    except:
        d = np.nan
        
    return d


'''
#for sanity testing the formula
lat1=41.88333333;lon1=    12.5 #rome
lat2=48.856613;lon2=2.352222 #paris
lat2=55.67611111;lon2=12.56833333 #copenhagen

haversine(lat1,lon1,lat2,lon2)/1000
'''

def haversine_intermediate(lat1,lon1,lat2,lon2,f):
    '''
    thanks again https://www.movable-type.co.uk/scripts/latlong.html
    find points which are some fraction f between origin and destination
    '''
    R = 6371e3 #// radius of earth in metres
    d = haversine(lat1,lon1,lat2,lon2)
    
    delta=d/R
    
    
    a = np.sin((1-f)*delta) / np.sin(delta)
    
    b = np.sin(f*delta) / np.sin(delta)
    
    start_lat = lat1 * np.pi/180 #tarting lat in radians  - phi
    end_lat = lat2 * np.pi/180 #end lat in radians
    
    start_lon = lon1 * np.pi/180
    end_lon = lon2 * np.pi/180
    
    x = a * np.cos(start_lat) * np.cos(start_lon) + b * np.cos(end_lat) * np.cos(end_lon)
    
    y = a * np.cos(start_lat) * np.sin(start_lon) + b * np.cos(end_lat) * np.sin(end_lon)
    
    z = a * np.sin(start_lat) + b * np.sin(end_lat)
    
    int_lat = (np.arctan2(z, np.sqrt(x**2+y**2)) ) / (np.pi/180)
    
    int_lon = np.arctan2(y,x) / (np.pi/180)
        
    return int_lat,int_lon

def monthdays(month_n):
    '''calculate days to add because of month, since 22 april 2017'''
    month_length=[31,28,31,31,30,30,31,31,30,31,30,31]
    i=0;day_count=0
    while month_n!=(i+1):
        day_count+=month_length[i]
        i+=1
    return day_count
        

def reignday(year,month_n,day):
    '''
    Papacy began	22 April 1073 - the 112th day of the year
    Papacy ended	25 May 1085- #4414 day reign
    nb this ignores the existence of leap days (Feb 23rd in Julian calendar)
    '''    
    try: 
        return day + monthdays(month_n) + (year-1073)*365 -  112
    except:
        return np.nan
    
def calctravel(origin, destination,speed,day,daysent):
    lat1 = origin[0]
    lon1 = origin[1]
    lat2 = destination[0]
    lon2 = destination[1]
    speed = speed *1000 #m/day
    
    distance = haversine(lat1,lon1,lat2,lon2)
    
    days=day-daysent
    
    #default is to return no position    
    show_lat=np.nan;show_lon=np.nan;f=0
    
    #change default if day is equal to day of sending, or later
    if days>-1:
        f = (days * speed) / distance
        last_f = ((days -1) * speed) / distance
        if (f>1) & (last_f>1): #if this day and the last are post-arrival
            show_lat=np.nan;show_lon=np.nan;
        else:
            show_lat,show_lon = haversine_intermediate(lat1,lon1,lat2,lon2,f)
            
    return show_lat,show_lon,f
