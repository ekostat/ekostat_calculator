#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import time
import datetime
import numpy as np

"""
========================================================================
========================================================================
========================================================================
"""
def is_sequence(arg):
    "Checks if an object is iterable (you can loop over it) and not a string"
#     print '='*30
#     print 'arg:'.ljust(20), arg
#     print 'type:'.ljust(20), type(arg)
#     print '-'*30
#     print "strip:".ljust(20), hasattr(arg, "strip")
#     print "__getitem__:".ljust(20), hasattr(arg, "__getitem__")
#     print "__iter__:".ljust(20), hasattr(arg, "__iter__")
    
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__iter__"))
            
#     return (not hasattr(arg, "strip") and
#             hasattr(arg, "__iter__") or 
#             (hasattr(arg, "__getitem__") and
#             not type(arg) == np.float64 and 
#             not type(arg) == np.float32 and 
#             not type(arg) == np.float16))
    
    
"""
========================================================================
========================================================================
========================================================================
"""
def get_current_datetime():
    return datetime.datetime.now()
    
"""
========================================================================
========================================================================
========================================================================
"""
def get_current_time_string(string_format='%Y-%m-%d'):
    """
    Method to get current time.
    """
    
    time_string = datetime.datetime.strftime(datetime.datetime.now(), 
                                                  string_format)

    
    return time_string

"""
========================================================================
========================================================================
========================================================================
"""
def get_month_name(month_nr, format='%b'):
    return datetime.date(2000, int(month_nr), 1).strftime(format)
    


"""
========================================================================
========================================================================
========================================================================
"""  
def get_float_list(unicode_list):

    try:
        value_list = []
        for val in unicode_list:
            if not val:
                value_list.append(np.nan)
            else:
                value_list.append(float(val))
        return value_list
    except:
        print(u'Could not create float-list.')

    
"""
========================================================================
========================================================================
========================================================================
"""  
def get_float_list_from_str(df=None, key='', ignore_qf=[]):
    """
    @Johannes
    Assumes list are of str type
    """
    if ignore_qf==[]:
        return [float(val) if val else np.nan for val in df.get(key)]
    else:
        out_list = []

        for val, qf in zip(df.get(key), df.get('Q_'+key)):
            if not val or qf in ignore_qf:
                val = np.nan
            else:
                val = float(val)
                
            out_list.append(val)
            
        return out_list
    
"""
========================================================================
========================================================================
========================================================================
"""  
def get_float_array(unicode_list):
    return np.array(get_float_list(unicode_list))

"""
========================================================================
========================================================================
========================================================================
"""
def get_sequel_display_string(value_list):
    """
    Returns a unicode string based on the values in value_string. 
    If values are in sequel they are put together with - otherwise separated with ,. 
    Values must be integers
    """
    print('value_list', value_list)
    try:
        value_list = map(int, value_list)
        value_list = sorted(value_list)
    except:
        print(u'Not able to map value_list')
    
    output_string = u''
    previous_value = value_list[0]
    temp_list = [previous_value]
    for value in value_list:
        if value <= previous_value+1:
            temp_list.append(value)
        else:
            # Check temp_values
            temp_list = sorted(set(temp_list))
            if len(temp_list) == 1:
                output_string = output_string + unicode(temp_list[0])
            else:
                output_string = output_string + u'%s-%s' % (temp_list[0], temp_list[-1])
            output_string += u', '
            temp_list = [value]
        previous_value = value
        
    if temp_list:
        # Check temp_values
        temp_list = sorted(set(temp_list))
        if len(temp_list) == 1:
            output_string = output_string + unicode(temp_list[0])
        else:
            output_string = output_string + u'%s-%s' % (temp_list[0], temp_list[-1])
    
    return output_string


"""
========================================================================
========================================================================
========================================================================
"""
def set_precision(value, nr_decimals=2, string=True):
    
    value = unicode(value)
    if u'.' in value:
        d = value.split(u'.')[-1]
        if len(d) > nr_decimals:
            value = unicode(round(float(value), nr_decimals))
    if nr_decimals == 0:
        value = value.split(u'.')[0]
    
    if not string:
        if u'.' in value:
            value = float(value)
        else:
            value = int(value)
        
    return value

"""
========================================================================
========================================================================
========================================================================
"""
def toYearFraction(date):
    """ 
    http://stackoverflow.com/questions/6451655/python-how-to-convert-datetime-dates-to-decimal-years
    """ 
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = datetime.datetime(year=year, month=1, day=1)
    startOfNextYear = datetime.datetime(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction



def insert_and_move_serno(list_to_insert=[], target_list=[], items_belong_to_same_list=False):
    
#     moves = dict((x,x) for x in target_list)
    moves = {}
    if not list_to_insert:
        return moves
#     if items_belong_to_same_list:
#         target_list = [item for item in target_list if item not in list_to_insert]
    
    list_to_insert = map(int, list_to_insert)
    target_list = map(int, target_list)
    
    nr_moves = len(list_to_insert)
    value_to_check = list_to_insert[0]
#     numbers_left = list_to_insert[:]
    

    while nr_moves > 0:
        if value_to_check in target_list:
            moves[str(value_to_check).rjust(4,'0')] = str(value_to_check + nr_moves).rjust(4,'0')
#             if numbers_left:
#                 numbers_left.pop(0)
        else:
            nr_moves -= 1
            
            
        value_to_check += 1
        
#     for n in numbers_left:
#         moves[n] = n
        
    return moves
    
#     for key in sorted(moves):
#         print key, ': ', moves[key] 





