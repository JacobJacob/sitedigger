# coding:utf-8
# Description: Page download class
# Author: redice

import urllib
import urllib2
from urllib2 import URLError, HTTPError
from StringIO import StringIO
import cache
import gzip
import socket
import threading

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
        
        socket.setdefaulttimeout(120)
        

    def getHtml(self,url,post_data=None,cookie=None,cached=True):
        """Fetch the target html
        url - URL to fetch
        post_data - POST Entity
        cookie - Cookie Header
        """
        if DEBUG:
            print "getHtml: ",url
        
        #Increase counter
        add_counter()

        result =''
        
        try:
            if cached:
                 result = self.cache.get(url)
                 if result!='':               
                    # find the cache data
                    return result


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
                opener.add_handler(urllib2.ProxyHandler({'http' : self.proxy}))            
           
            #if has post entity
            if post_data:
                #encode post data
                post_data = urllib.urlencode(post_data)
                
                response = opener.open(request,post_data)
            else:
                response = opener.open(request)
            
            result = response.read()
                  
            if response.headers.get('content-encoding') == 'gzip':
                result = gzip.GzipFile(fileobj=StringIO(result)).read()
            
            cs ='{'
            for sc in response.headers.get('Set-Cookie'):
                cs = cs + sc
            cs = cs +"}"
                
            response.close()

            #no content,don't save
            if not result or len(result)==0:
                return ''
            
            if cached:
                #save into chaches
                self.cache.set(url,result)
            
            return  result + cs
        except HTTPError, e:
            if DEBUG:
                print 'Error retrieving data:',e
                print 'Server error document follows:\n'
                #print e.read()
            return ''
        except URLError, e:
            if hasattr(e, 'reason'):
                if DEBUG:
                    print 'Failed to reach a server.'
                    print 'Reason: ', e.reason
                return ''
            elif hasattr(e, 'code'):
                if DEBUG:
                    print 'The server couldn\'t fulfill the request.'
                    print 'Error code: ', e.code
                return ''
        except Exception, e:
            if DEBUG:
                print e
            return ''
    
        
    def getLocation(self,url,post_data=None,cookie=None,cached=True):
        """Fetch the redirect location
        url - URL to fetch
        post_data - POST Entity
        cookie - Cookie Header
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
                if result!='':
                    # find the cache data
                    return result
            
            #create a request
            request = urllib2.Request(url)

            #change User-Agent
            request.add_header('User-Agent','Mozilla/5.0')
            
            #change Referrer
            request.add_header('Referrer',url)
            
            #if has cookie,add cookie header
            if cookie:
               request.add_header('Cookie',cookie) 
           
            opener = urllib2.build_opener(SmartRedirectHandler())

            if self.proxy:
                opener.add_handler(urllib2.ProxyHandler({'http' : self.proxy}))            
                                        
            #if has post entity
            if post_data:
                #encode post data
                post_data = urllib.urlencode(post_data)
                
                response = opener.open(request,post_data)
            else:
                response = opener.open(request)
            
            
            #get redirect location
            if isinstance(response,basestring):
                result = response
            elif isinstance(response,urllib2.addinfourl):
                #not a redirect response
                if DEBUG:
                    #print response.read(),url
                    print "%s response no redirect" % (url)

                response.close()
                result = url
            
            #no content,don't save
            if not result or len(result)==0:
                return ''
            
            if cached:
                #save into caches
                self.cache.set(url,result)
            
            return  result
        except HTTPError, e:
            if DEBUG:
                print 'Error retrieving data:',e
                print 'Server error document follows:\n'
                #print e.read()
            return ''
        except URLError, e:
            if hasattr(e, 'reason'):
                if DEBUG:
                    print 'Failed to reach a server.'
                    print 'Reason: ', e.reason
                return ''
            elif hasattr(e, 'code'):
                if DEBUG:
                    print 'The server couldn\'t fulfill the request.'
                    print 'Error code: ', e.code
                return ''
        except Exception, e:
            if DEBUG:
                print e
            return ''


class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        
        return headers['Location']
        #result = urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)   
        #result.status = code
        #return result

    def http_error_302(self, req, fp, code, msg, headers):
        
        return headers['Location']
        #result = urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        #result.status = code
        #return result


if __name__ == '__main__':
    # test performance of DownLoad class
    download = DownLoad()
    url=''
    while url=='':
      url = raw_input("Please input the url:")
    
    #print download.getHtml(url)
    print download.getLocation(url)