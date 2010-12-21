# coding:utf-8
# Description: Page download class
# Author: redice
# License: LGPL

import urllib
import urllib2
import httplib
from urlparse import urlparse
from urllib2 import URLError, HTTPError
from StringIO import StringIO
import common
import cache
import gzip
import socket
import threading
import re
import time

DEBUG = True

#counter for pages downloaded
counter = 0

#create a thread lock to access counter
lock = threading.Lock() 

def synchronous(f):
    def call(*args, **kwargs):
        lock.acquire()
        try:
            return f(*args, **kwargs)
        finally:
            lock.release()
    return call


@synchronous
def add_counter():
    """Increase counter"""
    global counter
    counter = counter +1

def get_counter():
    """Get counter"""
    global counter
    return counter


class DownLoad:
    """Download page and return html"""

    def __init__(self,proxy=None):
        
        self.proxy = proxy
        
        #Create Cache Object
        self.cache = cache.Cache()
        
        socket.setdefaulttimeout(100)
        

    def getHtml(self,url,post_data=None,cookie=None,cached=True,sleep=None):
        """Fetch the target html.
        
        Params:
            url - URL to fetch.
            post_data - POST Entity,Both Dic and String(urlencoded) will be accept.
            cookie - Cookie Header.
        Return:
            return a Dic like {'html':'','cookie':''}.
        """
        if DEBUG:
            print "getHtml: ",url
        
        up = urlparse(url)
        #if need a https connections
        #i find urllib dosen't support https very well
        if up.scheme and up.scheme=='https':
            return self.getHttps(url, post_data, cookie, cached, sleep)
        
        #Increase counter
        add_counter()

        result ={'html':'','cookie':''}
        
        try:
            if cached:
                 result['html'] = self.cache.get(url)
                 if result['html']:               
                    # find the cache data
                    return result
                
            #as the firewall,sometimes need to delay request
            if sleep:
                time.sleep(sleep)
                
            #create a request
            request = urllib2.Request(url)

            #change User-Agent
            request.add_header('User-Agent','Mozilla/5.0')
            
            #change Referrer
            request.add_header('Referrer',url)
            
            #support gzip
            request.add_header('Accept-encoding','gzip')
            
            #if has cookie,add cookie header
            if cookie:
               request.add_header('Cookie',cookie)

            #create a opener
            opener = urllib2.build_opener()

            if self.proxy:
                if isinstance(self.proxy,list):
                    #Take turns to use
                    proxy = self.proxy.pop()
                    self.proxy.insert(0,proxy)
                else:
                    proxy = self.proxy
                
                opener.add_handler(urllib2.ProxyHandler({'http' : proxy}))            
           
            #if has post entity
            if post_data:
                #encode post data
                if isinstance(post_data,dic):
                    post_data = urllib.urlencode(post_data)
                
                response = opener.open(request,post_data)
            else:
                response = opener.open(request)
            
            result['html'] = response.read()
                  
            if response.headers.get('content-encoding') == 'gzip':
                result['html'] = gzip.GzipFile(fileobj=StringIO(result['html'])).read()
            
            if response.headers.get('Set-Cookie'):
                if isinstance(response.headers.get('Set-Cookie'),basestring):
                    result['cookie'] = response.headers.get('Set-Cookie')
                else:
                    for c in response.headers.get('Set-Cookie'):
                        result['cookie'] = result['cookie'] + c + ";"
            
            #fix the cookie
            if result['cookie']:
                result['cookie'] = re.compile(r"path=/[;]?", re.IGNORECASE).sub('',result['cookie'])
                result['cookie'] = result['cookie'].replace(',',';')
                
            response.close()

            #no content,don't save
            if not result['html']:
                return result
            
            if cached:
                #save into chaches
                self.cache.set(url,result['html'])
            
            return  result
        except HTTPError, e:
            if DEBUG:
                print 'Error retrieving data:',e
                print 'Server error document follows:\n'
                #print e.read()
                common.logerror('error.log', "getHTML::Error retrieving data. %s, error reason: %s " % (url,e))
            return result
        except URLError, e:
            if hasattr(e, 'reason'):
                if DEBUG:
                    print 'Failed to reach a server.'
                    print 'Reason: ', e.reason
                    common.logerror('error.log', "getHTML::Failed to reach a server. %s, error reason: %s " % (url,e.reason))
                return result
            elif hasattr(e, 'code'):
                if DEBUG:
                    print 'The server couldn\'t fulfill the request.'
                    print 'Error code: ', e.code
                    common.logerror('error.log', "getHTML::The server couldn\'t fulfill the request. %s, error code: %s " % (url,e.code))
                return result
        except Exception, e:
            if DEBUG:
                print e
                common.logerror('error.log', "getHTML::Unknow Exception. %s, error info: %s " % (url,e))
            return result
    

    def getHttps(self,url,post_data=None,cookie=None,cached=True,sleep=None):
        """Fetch the target html from https.
        
        Params:
            url - URL to fetch.
            post_data - POST Entity.
            cookie - Cookie Header.
        Return:
            return a Dic like {'html':'','cookie':''}.
        """
        if DEBUG:
            print "getHttps: ",url
        
        #Increase counter
        add_counter()

        result ={'html':'','cookie':''}
        
        try:
            if cached:
                 result['html'] = self.cache.get(url)
                 if result['html']:               
                    # find the cache data
                    return result
                
            #as the firewall,sometimes need to delay request
            if sleep:
                time.sleep(sleep)
            
            
            up = urlparse(url)
            host_with_port = up.netloc
            host = up.netloc.partition(':')[0]
            
            conn = httplib.HTTPSConnection(host_with_port)
            conn.connect()
            
            headers = {"Host":host,"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"}
            headers['Accept-encoding']='gzip'
            
            if cookie:
                headers['Cookie'] = cookie
            
            if post_data:
                #encode post data
                if isinstance(post_data,dic):
                    post_data = urllib.urlencode(post_data)
                
                conn.request("POST",up.path + "?" + up.query,post_data,headers)
            else:
                conn.request("GET",up.path + "?" + up.query,None,headers)
                
            response = conn.getresponse()
            result['html'] = response.read()
            
            if response.getheader('content-encoding') == 'gzip':
                result['html'] = gzip.GzipFile(fileobj=StringIO(result['html'])).read()
            
            result['cookie'] = response.getheader("Set-Cookie")
            
            #fix the cookie
            if result['cookie']:
                result['cookie'] = re.compile(r"path=/[;]?", re.IGNORECASE).sub('',result['cookie'])
                result['cookie'] = result['cookie'].replace(',',';')
            
            conn.close()
            
            #no content,don't save
            if not result['html']:
                return result
            
            if cached:
                #save into chaches
                self.cache.set(url,result['html'])
            
            return  result
        except Exception, e:
            if DEBUG:
                print e
                common.logerror('error.log', "getHttps::Unknow Exception. %s, error info: %s " % (url,e))

            return result
    
    
    def getLocation(self,url,post_data=None,cookie=None,cached=True,sleep=None):
        """Fetch the redirect location.
        
        Params:
            url - URL to fetch.
            post_data - POST Entity.
            cookie - Cookie Header.
        Return:
            return the redirect Location.
        Notice: 
            if no redirection, just return the previous url.
        """
        if DEBUG:
            print "getLocation: ",url
        
        #Increase counter
        add_counter()
        
        result = ''
        try:
            if cached:              
                # look up the caches file firstly
                result = self.cache.get(url)
                if result:
                    # find the cache data
                    return result
            #as the firewall,sometimes need to delay request
            if sleep:
                time.sleep(sleep)
                
            up = urlparse(url)
            host_with_port = up.netloc
            host = up.netloc.partition(':')[0]
            
            conn = httplib.HTTPConnection(host_with_port)
            conn.connect()
            
            headers = {"Host":host,"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"}
            
            if cookie:
                headers['Cookie'] = cookie
            
            if post_data:
                #encode post data
                if isinstance(post_data,dic):
                    post_data = urllib.urlencode(post_data)
                
                conn.request("POST",up.path + "?" + up.query,post_data,headers)
            else:
                conn.request("GET",up.path + "?" + up.query,None,headers)
                
            response = conn.getresponse()
            
            #if has Location header
            if response.getheader('Location'):
                result = response.getheader('Location')
                
                #fix the Location
                if result and not urlparse(result).scheme:
                    if result[0]=='/':
                        result = up.scheme + "://" + up.netloc + result
                    else:
                        previous_path = up.scheme + "://" + up.netloc + up.path
                        
                        if previous_path[-1]=='/':
                            result = previous_path + result
                        else:
                            path,slash,fname = previous_path.rpartition('/')
                            result = path + "/" + result
            else:
                return url
            
            if cached:
                #save into caches
                self.cache.set(url,result)
            
            return  result
        except Exception, e:
            if DEBUG:
                print e
                common.logerror('error.log', "getHTML::Unknow Exception. %s, error info: %s " % (url,e))
            return url



if __name__ == '__main__':
    # test performance of DownLoad class
    download = DownLoad()
    
    print download.getHtml('http://www.redicecn.com')
    #print download.getHtml('https://www.alipay.com/')
    #print download.getLocation('http://www.redicecn.com/tools/redirect.php')