# -*- coding: utf-8 -*-
"""
Helper functions

@author: jokebill
"""
import datetime
import re
from time import sleep
from enum import IntEnum

Weekdays = IntEnum('Weekdays', 'mon tue wed thu fri sat sun', start=0)

class PageError(Exception):
    '''Error class for any problems when working on a webpage.
    '''
    def __init__(self, message):
        self.message = message

class TimeError(Exception):
    '''Error class for any problems when working on a webpage.
    '''
    def __init__(self, message):
        self.message = message
        
def Now():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')     


class Timer(object):
    def __init__(self, exp=None, logging=True):
        if exp:
            try:
                self.delta = datetime.timedelta(seconds=int(exp))
            except TypeError:
                self.delta = exp
        else:
            self.delta = None
        self.logging = logging
        if isinstance(self.delta, datetime.timedelta):
            print(Now(), f"Timer enabled for duration ", self.delta)
            self.start_time = datetime.datetime.now()
            self.end_time = self.start_time + self.delta
        else:
            print(Now(), 'Timer disabled.')
            
    
    def Wait(self):
        if not self.delta:
            return
        dt = (self.end_time - datetime.datetime.now()).total_seconds()
        if dt > 0:
            if self.logging:
                print(f'Sleeping {dt!s} seconds')
            sleep(dt)
        self.start_time = datetime.datetime.now()
        self.end_time = self.start_time + self.delta
        
   
      
def SBreak():
    sleep(0.2)
    
def MBreak():
    sleep(2)

def LBreak():
    sleep(6)
    
def SLBreak():
    sleep(30)
    
def SelectDates(num_days=90, start_date=None, weekday=Weekdays.thu):
    if start_date:
        start_time = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_time = datetime.datetime.now()
    if weekday is None:
        using_weekdays = range(7)
    else:
        try:
            iter(weekday)
        except TypeError:
            using_weekdays = [int(weekday)]
        else:
            using_weekdays = [int(d) for d in weekday]
    sel_dates = [start_time + datetime.timedelta(days=offset)
                 for offset in range(num_days)]
    return [dd.date() for dd in sel_dates if dd.weekday() in using_weekdays]

def FormatDate(dd):
    dt = datetime.datetime(dd.year, dd.month, dd.day)
    return dt.strftime('%m/%d/%Y')

def ParseDuration(dtext):
    if not dtext:
        return datetime.timedelta()
    match_res = ParseDuration.matcher.match(dtext)
    hours = 0
    if match_res['hour']:
        hours = int(match_res['hour'])
    minutes = 0
    if match_res['minute']:
        minutes = int(match_res['minute'])
    return datetime.timedelta(hours=hours, minutes=minutes)

ParseDuration.matcher = re.compile(r'((?P<hour>\d+)h)? ?((?P<minute>\d+)m)?')

def ParseHourMinute(ttext):
    parsed_datetime = None
    err_msg = None
    try:
        parsed_datetime = datetime.datetime.strptime(ttext, '%I%p')
    except ValueError:
        try:
            parsed_datetime = datetime.datetime.strptime(ttext, '%I:%M%p')
        except ValueError as err:
            err_msg = f'Failed to parse time {ttext}, error message {err}.'
    if err_msg is not None:
        raise TimeError(err_msg)
    return parsed_datetime.time()
        