#!/usr/bin/env python
'''****************************************************************************
FILE: apache_log_helper.py

PURPOSE: Used to extract data from logfile.

PROJECT: Land Satellites Data System Science Research and Development (LSRD)
    at the USGS EROS

LICENSE TYPE: NASA Open Source Agreement Version 1.3

AUTHOR: ngenetzky@usgs.gov
****************************************************************************'''
import logging
import datetime
import urllib


def fail_to_parse(value, line, strict=True ):
    '''Runs when any function fails to extract value

    If strict is False then silently fail. (return 'BAD_PARSE')
    If strict is True then an exception is raised.
    '''
    # Get the logger
    logger = logging.getLogger(__name__)
    logger.debug('Failed to parse for {0} in <\n{1}>'.format(value, line))
    #if is_invalid_line(line) and not strict:
    #    return 'BAD_PARSE'
    if strict:
        raise Exception(line)
    else:
        return 'BAD_PARSE'

def verify_line(line):
    def is_valid(return_val):
        if(return_val == 'BAD_PARSE'):
            return False
        # Invalid datetime
        if(return_val == datetime.datetime.max):
            return False
        return True

    # Keys of this dict must be functions of in the namespace
    verify_dict = {
                   'get_datetime': is_valid(get_datetime(line)),
                   'get_date': is_valid(get_date(line)),
                   'get_bytes': is_valid(get_bytes(line)),
                   'get_rtcode': is_valid(get_rtcode(line)),
                   'get_user_email': is_valid(get_user_email(line)),
                   'get_email_category': is_valid(get_email_category(line)),
                   'get_scene_id': is_valid(get_scene_id(line)),
                   'get_order_id': is_valid(get_order_id(line)),
                   }

    return verify_dict

def is_invalid_line(line):
    # Invalid line could contain a user request with no spaces:
    if(2==substring_between(line, ' "', '" ').count(' ')):
        return False  # Should have 2 spaces
    return True

def substring_between(s, start, finish):
    '''Find string between two substrings'''
    end_of_start = s.index(start) + len(start)
    start_of_finish = s.index(finish, end_of_start)
    return s[end_of_start:start_of_finish]

def ordertype_filter_decorator(mapper, order_type):
    if('production' == order_type):
        def new_mapper(line):
            if(is_production_order(line)):
                return mapper(line)

    elif('dswe' == order_type):
        def new_mapper(line):
            if(is_dswe_order(line)):
                return mapper(line)

    elif('burned_area' == order_type):
        def new_mapper(line):
            if(is_burned_area_order(line)):
                return mapper(line)
    else:
        raise ValueError('Not valid ordertype')

    return new_mapper

def timefilter_decorator(mapper, start_date, end_date):
    '''Returns mapper than will first filter down to lines with dates in date range

    Precondition:
        start_date and end_date are datetime objects
        mapper is a function that accepts a single parameter, line.
    Postcondition:
        returns a mapper that will return None if date is not in range
    '''
    def new_mapper(line):
        dt = get_datetime(line)
        if(start_date <= dt and dt <= end_date):
            return mapper(line)
    return new_mapper


def get_datetime(line):
    try:
        time_local = substring_between(line, '[', '] "')
    except ValueError:
        raise Exception('Could not find datetime in line:{0}'.format(line))
    else:
        try:
            return datetime.datetime.strptime(time_local,
                                              '%d/%b/%Y:%H:%M:%S -0500')
        except ValueError:
            raise ValueError('Datetime is not format correctly in:{0}'.format(time_local))

def get_date(line):
    return get_datetime(line).date()


def get_bytes(line):
    '''Obtain number of downloaded bytes from a line of text

    Precondition: line is a ' ' separated list of data.
                Bytes downloaded is an int after the 8th space.
    Postcondition: return bytes_downloaded
    '''
    data = line.split()
    if(data[9].isdigit()):
        return data[9]
    else:
        return fail_to_parse('downloaded_bytes', line)


def get_rtcode(line):
    '''Obtain a return_code from a line of text

    Precondition:line is a ' ' separated list of data.
                 Return code is an int after the 9th space.
    Postcondition: return return_code
    '''
    data = line.split()
    if(data[8].isdigit()):
        return data[8]
    else:
        return fail_to_parse('return_code', line)


def get_user_email(line):
    '''Extracts the user email from the orders/ subdirectory

    Precondition:
        is_production_order(line) == True
            If this is violated then the desired contents may not be present.
        user_email must be surrounded with very specific characters
            These characters are defined by format of the filepath
            See code for details
    Postcondition:
        Returns the user_email
    Issues:
        Does not support emails that contain the following strings (exclude ''):
            '-'
            '" '
            ' '
    '''
    request = substring_between(line, '] "', '" ')
    request = urllib.unquote(request)
    try:
        return substring_between(request, 'orders/', '-')
    except ValueError:
        if(is_production_order(line)):
            return fail_to_parse('user_email', line, strict=True)
        else:
            return fail_to_parse('user_email', line, strict=False)


def get_email_category(line):
    email = get_user_email(line)
    if '.gov' in email:
        if('usgs.' in email):
            return 'usgs.gov'
        else:
            return 'not-usgs.gov'
    elif '.edu' in email:
        return '*.edu'
    else:
        return 'other'


def get_scene_id(line):
    try:
        response_after_orderid = substring_between(line, 'orders/', '" ')
        return substring_between(response_after_orderid, '/', '.tar.gz')
    except ValueError:
        try:
            response_after_orderid = substring_between(line, 'orders/', '" ')
            return substring_between(response_after_orderid, '/', '.cksum')
        except ValueError:
            return fail_to_parse('sceneid', line)


def get_order_id(line):
    request = substring_between(line, '] "', '" ')
    try:
        return substring_between(request, 'orders/', '/')
    except ValueError:
        return fail_to_parse('orderid', line)

#
#    Filters
#


def is_successful_request(line):
    '''Extracts return code and then returns true if code indicates success'''
    return_code = get_rtcode(line)
    if(return_code=='BAD_PARSE'):
        return 'BAD_PARSE'
    else:
        return (return_code in ['200', '206'])


def is_production_order(line):
    return (('GET /orders/' in line) and ('.tar.gz' in line))

def is_dswe_order(line):
    return (('GET /downloads/provisional/dswe/' in line)
            and ('.tar.gz' in line))

def is_burned_area_order(line):
    return (('GET /downloads/provisional/burned_area/' in line)
            and ('.tar.gz' in line))


def is_404_request(line):
    '''Extracts return code and returns true if indicates file-not-found'''
    return_code = get_rtcode(line)
    if(return_code=='BAD_PARSE'):
        return 'BAD_PARSE'
    else:
        return (return_code in ['404'])

