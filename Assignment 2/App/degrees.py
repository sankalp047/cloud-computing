import numpy as np
from datetime import datetime, timedelta

# Converts degree to radians
def degToRad(degree):
    return degree * np.pi/180

# Reference:  https://andrew.hedges.name/experiments/haversine/
def geoDifference(a_latitude_deg, a_longitude_deg, latitude_deg, longitude_deg): 
    radius_earth_miles = 3961
    radius_earth_kilometers = 6373

    a_latitude = degToRad(np.array(a_latitude_deg))
    a_longitude = degToRad(np.array(a_longitude_deg))
    latitude = degToRad(latitude_deg)
    longitude = degToRad(longitude_deg)

    d_latitude = a_latitude - latitude
    d_longitude = a_longitude - longitude

    A = (np.sin(d_latitude/2) ** 2) + np.cos(a_latitude) * np.cos(latitude) * (np.sin(d_longitude/2) ** 2)
    C = 2 * np.arctan((A**0.5), ((1-(A))**0.5))

    dist_miles = C * radius_earth_miles
    dist_kilometers = C * radius_earth_kilometers
    
    return dist_kilometers

def getCorrespondingTime(a_longitude_deg, a_gmt_time):
    gmt_time = np.array(a_gmt_time, dtype='datetime64')
    deltaTime_minutes = (np.array(a_longitude_deg)*4).astype('timedelta64[m]')
    correspondingTime = gmt_time + deltaTime_minutes
    return correspondingTime
