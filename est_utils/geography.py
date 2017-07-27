#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import numpy as np

import est_utils

"""
========================================================================
========================================================================
========================================================================
"""
def decdeg_to_decmin(pos,string_type=False,decimals=False):
    # TODO, add if else for negative position (longitude west of 0 degrees)
    if est_utils.is_sequence(pos):
        output = []
        for p in pos:
            p = float(p)
            deg = np.floor(p)
            minut = p%deg*60.0
            if string_type:
                if decimals is not False:
                    output.append('%%2.%sf' % decimals % (deg*100.0 + minut))
                else:
                    output.append(unicode(deg*100.0 + minut))
            else:
                output.append(deg*100.0 + minut)
    else:
        pos = float(pos)
        deg = np.floor(pos)
        minut = pos%deg*60.0
        if string_type:
            if decimals is not False:
                output = ('%%2.%sf' % decimals % (deg*100.0 + minut))
            else:
                output = (unicode(deg*100.0 + minut))
        else:
            output = (deg*100.0 + minut)
          
    return output


"""
========================================================================
========================================================================
========================================================================
"""

def decmin_to_decdeg(pos, return_string=False):
#    print type(pos),pos
    try:
        if est_utils.is_sequence(pos):
            output = []
            for p in pos:
#                 print p, type(p)
                p = float(p)
                if p >= 0:
                    output.append(np.floor(p/100.) + (p%100)/60.)
                else:
                    output.append(np.ceil(p/100.) - (-p%100)/60.)
        else:
            pos = float(pos)
            if pos >= 0:
                output = np.floor(pos/100.) + (pos%100)/60.
            else:
                output = np.ceil(pos/100.) - (-pos%100)/60.
        
        if return_string:
            if est_utils.is_sequence(output):
#                 print 'if-if'
                return map(unicode, output)
            else:
#                 print 'if-else'
                return unicode(output)
        else:
#             print 'else'
            return output
    except:
        return pos




"""
========================================================================
========================================================================
========================================================================
"""
def latlon_distance(origin, destination):
    '''
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    from math import radians, cos, sin, asin, sqrt
    lat1, lon1 = origin
    lat2, lon2 = destination
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2.)**2 + cos(lat1) * cos(lat2) * sin(dlon/2.)**2
    c = 2 * asin(sqrt(a))
    # km = 6367 * c
    km = 6363 * c # Earth radius at around 57 degrees North
    return km 


"""
========================================================================
========================================================================
========================================================================
"""
def point_in_poly(x, y, poly):
    """
    # Determine if a point is inside a given polygon or not
    # Polygon is a list of (x,y) pairs. This function
    # returns True or False.  The algorithm is called
    # the "Ray Casting Method".
    http://geospatialpython.com/2011/01/point-in-polygon.html
    """

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

"""
========================================================================
========================================================================
========================================================================
"""
def point_in_polygon(point, point_list):
    """
    point in polygon
    @param point: point represented as a(x,y) tuple
    @param pointList: polygon represented as [(x1,y1),(x2,y2),…,(xn,yn),(x1,y1)]
    """
    assert len(point_list)>=3, 'Not enough points to form a polygon'
        
    x, y =float(point[0]),float(point[1])
    xp=[float(p[0]) for p in point_list]
    yp=[float(p[1]) for p in point_list]
        
    c=False
    i=0
    npol=len(point_list)
    j=npol-1
      
    while i<npol:
        if((((yp[i]<=y) and (y<yp[j])) or
            ((yp[j]<=y) and (y<yp[i]))) and
            (x < (xp[j]-xp[i])*(y-yp[i])/(yp[j]-yp[i])+xp[i])):
            c = not c
        j=i
        i+=1
    return c





"""
========================================================================
========================================================================
========================================================================
"""
def transform(in_proj = 'EPSG:3011',out_proj = 'EPSG:4326', lat=0.0, lon=0.0):
    """
    Transform coordinates from one spatial reference system to another.
    in_proj is your current reference system
    out_proj is the reference system you want to transform to, default is EPSG:4326 = WGS84
    (Another good is EPSG:4258 = ETRS89 (Europe), almost the same as WGS84 (in Europe) 
    and not always clear if coordinates are in WGS84 or ETRS89, but differs <1m.
    lat = latitude
    lon = longitude
    
    To find your EPSG check this website: http://spatialreference.org/ref/epsg/
    """
    import mpl_toolkits.basemap.pyproj as pyproj
    
    o_proj = pyproj.Proj("+init="+out_proj) 
    i_proj = pyproj.Proj("+init="+in_proj)
    if type(lat) == list:
        if len(lat) != len(lon):
            print(u'Length of Latitude differs from length of Longitude! When providing lists och coordinates they must have the same length')
            x, y = None, None
        else:
            x = []
            y = []
            for i in range(len(lat)):
                x_i, y_i = pyproj.transform(i_proj, o_proj, float(lon[i]), float(lat[i]))
                x.append(x_i)
                y.append(y_i)
    else:
        x, y = pyproj.transform(i_proj, o_proj, float(lon), float(lat))
    
    return y, x