# coding:utf-8
# Description: Common web scraping related functions
# Author: Richard Penman (richard@sitescraper.net) & redice
# License: LGPL
#

import os
import re
import time
import math
import csv
import string
import urllib
import urlparse
import string
import htmlentitydefs
import cookielib
from datetime import datetime, timedelta



# known media file extensions
MEDIA_EXTENSIONS = ['ai', 'aif', 'aifc', 'aiff', 'asc', 'au', 'avi', 'bcpio', 'bin', 'c', 'cc', 'ccad', 'cdf', 'class', 'cpio', 'cpt', 'csh', 'css', 'csv', 'dcr', 'dir', 'dms', 'doc', 'drw', 'dvi', 'dwg', 'dxf', 'dxr', 'eps', 'etx', 'exe', 'ez', 'f', 'f90', 'fli', 'flv', 'gif', 'gtar', 'gz', 'h', 'hdf', 'hh', 'hqx', 'ice', 'ico', 'ief', 'iges', 'igs', 'ips', 'ipx', 'jpe', 'jpeg', 'jpg', 'js', 'kar', 'latex', 'lha', 'lsp', 'lzh', 'm', 'man', 'me', 'mesh', 'mid', 'midi', 'mif', 'mime', 'mov', 'movie', 'mp2', 'mp3', 'mpe', 'mpeg', 'mpg', 'mpga', 'ms', 'msh', 'nc', 'oda', 'pbm', 'pdb', 'pdf', 'pgm', 'pgn', 'png', 'pnm', 'pot', 'ppm', 'pps', 'ppt', 'ppz', 'pre', 'prt', 'ps', 'qt', 'ra', 'ram', 'ras', 'rgb', 'rm', 'roff', 'rpm', 'rtf', 'rtx', 'scm', 'set', 'sgm', 'sgml', 'sh', 'shar', 'silo', 'sit', 'skd', 'skm', 'skp', 'skt', 'smi', 'smil', 'snd', 'sol', 'spl', 'src', 'step', 'stl', 'stp', 'sv4cpio', 'sv4crc', 'swf', 't', 'tar', 'tcl', 'tex', 'texi', 'tif', 'tiff', 'tr', 'tsi', 'tsp', 'tsv', 'txt', 'unv', 'ustar', 'vcd', 'vda', 'viv', 'vivo', 'vrml', 'w2p', 'wav', 'wrl', 'xbm', 'xlc', 'xll', 'xlm', 'xls', 'xlw', 'xml', 'xpm', 'xsl', 'xwd', 'xyz', 'zip']

# US_STATES
US_STATES = ['AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','PR','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']


def to_ascii(html):
    """Return ascii part of html
    """
    return ''.join(c for c in html if ord(c) < 128)

def to_int(s):
    """Return integer from this string

    >>> to_int('90')
    90
    >>> to_int('a90a')
    90
    >>> to_int('a')
    0
    """
    return int(to_float(s))

def to_float(s):
    """Return float from this string
    """
    valid = string.digits + '.'
    return float('0' + ''.join(c for c in s if c in valid))


def is_html(html):
    """Returns whether content is HTML
    """
    try:
        result = re.search('html|head|body', html) is not None
    except TypeError:
        result = False
    return result


def unique(l):
    """Remove duplicates from list, while maintaining order

    >>> unique([3,6,4,4,6])
    [3, 6, 4]
    >>> unique([])
    []
    >>> unique([3,6,4])
    [3, 6, 4]
    """
    checked = []
    for e in l:
        if e not in checked:
            checked.append(e)
    return checked


def flatten(ls):
    """Flatten sub lists into single list

    >>> [[1,2,3], [4,5,6], [7,8,9]]
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    return [e for l in ls for e in l]


def nth(l, i, default):
    return l[i] if len(l) > i else default

def first(l, default=''):
    """Return first element from list or default value if empty

    >>> first([1,2,3])
    1
    >>> first([], None)
    None
    """
    return nth(l, 0, default)

def last(l, default=''):
    """Return last element from list or default value if empty
    """
    return l[-1] if l else default


def any_in(es, l):
    """Returns True if any element of es are in l

    >>> any_in([1, 2, 3], [3, 4, 5])
    True
    >>> any_in([1, 2, 3], [4, 5])
    False
    """
    for e in es:
        if e in l:
            return True
    else:
        return False

def all_in(es, l):
    """Returns True if all elements of es are in l

    >>> all_in([1, 2, 3], [2, 3, 1, 1])
    True
    >>> all_in([1, 2, 3], [1, 2])
    False
    """
    for e in es:
        if e not in l:
            return False
    return True


def remove_tags(html, keep_children=True):
    """Remove HTML tags leaving just text
    If keep children is True then keep text within child tags

    >>> remove_tags('hello <b>world</b>!')
    'hello world!'
    >>> remove_tags('hello <b>world</b>!', False)
    'hello !'
    """
    if not keep_children:
        # XXX does not work for multiple nested tags
        html = re.compile('<.*?>(.*?)</.*?>', re.DOTALL).sub('', html)
    return re.compile('<[^<]*?>').sub('', html)


def unescape(text, encoding='utf-8'):
    """Interpret escape characters

    >>> unescape('&lt;hello&nbsp;&amp;&nbsp;world&gt;')
    '<hello & world>'
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == '&#':
            # character reference
            try:
                if text[:3] == '&#x':
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    try:
        text = text.decode(encoding, 'ignore')
    except UnicodeError:
        pass
    text = urllib.unquote(text).replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub('&#?\w+;', fixup, urllib.unquote(text))
    try:
        text = text.encode(encoding, 'ignore')
    except UnicodeError:
        pass
    #replace "\xc2\xa0", fixed by redice 2010.12.17
    return text.replace("\xc2\xa0"," ")


def clean(s):
    return unescape(remove_tags(s)).strip()


def safe(s):
    """Return safe version of string for URLs
    """
    safe_chars = string.letters + string.digits + ' '
    return ''.join(c for c in s if c in safe_chars).replace(' ', '-')

def pretty(s):
    """Return pretty version of string for display
    """
    return re.sub('[-_]', ' ', s.title())


def get_extension(url):
    """Return extension from given URL

    >>> get_extension('hello_world.JPG')
    'jpg'
    >>> get_extension('http://www.google-analytics.com/__utm.gif?utmwv=1.3&utmn=420639071')
    'gif'
    """
    return os.path.splitext(urlparse.urlsplit(url).path)[-1].lower().replace('.', '')


def get_domain(url):
    """Extract the domain from the given URL

    >>> get_domain('http://www.google.com.au/tos.html')
    'google.com.au'
    """
    suffixes = 'ac', 'ad', 'ae', 'aero', 'af', 'ag', 'ai', 'al', 'am', 'an', 'ao', 'aq', 'ar', 'arpa', 'as', 'asia', 'at', 'au', 'aw', 'ax', 'az', 'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'biz', 'bj', 'bm', 'bn', 'bo', 'br', 'bs', 'bt', 'bv', 'bw', 'by', 'bz', 'ca', 'cat', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co', 'com', 'coop', 'cr', 'cu', 'cv', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'edu', 'ee', 'eg', 'er', 'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gov', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'info', 'int', 'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 'jobs', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mg', 'mh', 'mil', 'mk', 'ml', 'mm', 'mn', 'mo', 'mobi', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'name', 'nc', 'ne', 'net', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'org', 'pa', 'pe', 'pf', 'pg', 'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'pro', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'st', 'su', 'sv', 'sy', 'sz', 'tc', 'td', 'tel', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'tt', 'tv', 'tw', 'tz', 'ua', 'ug', 'uk', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu', 'wf', 'ws', 'xn', 'ye', 'yt', 'za', 'zm', 'zw'
    url = re.sub('^.*://', '', url).partition('/')[0].lower()
    domain = []
    for section in url.split('.'):
        if section in suffixes:
            domain.append(section)
        else:
            domain = [section]
    return '.'.join(domain)


def same_domain(url1, url2):
    """Return whether URLs belong to same domain
    """
    server1 = get_domain(url1)
    server2 = get_domain(url2)
    return server1 and server2 and (server1 in server2 or server2 in server1)


def pretty_duration(dt):
    """Return english description of this time difference
    """
    if isinstance(dt, datetime):
        # convert datetime to timedelta
        dt = datetime.now() - dt
    if not isinstance(dt, timedelta):
        return ''
    if dt.days >= 2*365: 
        return '%d years' % int(dt.days / 365) 
    elif dt.days >= 365: 
        return '1 year' 
    elif dt.days >= 60: 
        return '%d months' % int(dt.days / 30) 
    elif dt.days > 21: 
        return '1 month' 
    elif dt.days >= 14: 
        return '%d weeks' % int(dt.days / 7) 
    elif dt.days >= 7: 
        return '1 week' 
    elif dt.days > 1: 
        return '%d days' % dt.days 
    elif dt.days == 1: 
        return '1 day' 
    elif dt.seconds >= 2*60*60: 
        return '%d hours' % int(dt.seconds / 3600) 
    elif dt.seconds >= 60*60: 
        return '1 hour' 
    elif dt.seconds >= 2*60: 
        return '%d minutes' % int(dt.seconds / 60) 
    elif dt.seconds >= 60: 
        return '1 minute' 
    elif dt.seconds > 1: 
        return '%d seconds' % dt.seconds 
    elif dt.seconds == 1: 
        return '1 second' 
    else: 
        return ''


def distance(p1, p2):
    """Calculate distance between 2 (latitude, longitude) points
    Multiply result by radius of earth (6373 km, 3960 miles)
    """
    lat1, long1 = p1
    lat2, long2 = p2
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc



def get_zip_codes(city_file, min_distance):
    """Find zip codes that are the given distance apart
    """
    zip_codes = []
    zip_code_positions = {}
    header = None
    for row in csv.reader(open(city_file)):
        if header:
            zip_code, state, city, long1, lat1 = row
            p1 = float(lat1), float(long1)
            success = True
            for z in reversed(zip_codes):
                if distance(p1, zip_code_positions[z]) * 3960 < min_distance:
                    success = False
                    break
            if success:
                zip_codes.append(zip_code)
                zip_code_positions[zip_code] = p1
        else:
            header = row
    return zip_codes



def logerror(logname,logstr):
    """
    write error log
    logname - logfile name
    logstr - log content
    """
    log(logname,logstr)


def log(logname,logstr):
    """
    write log
    logname - logfile name
    logstr - log content
    """
    logf = open(logname,'a+')
    logf.write(str(time.strftime('%Y-%m-%d-%H-%M-%s',time.localtime(time.time())))+'  '+logstr+'\n')
    logf.close()    