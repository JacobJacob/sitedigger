# coding:utf-8
# Description: Page cache class
# Author: redice

import sqlite3
import threading

DEBUG = True

#create a thread lock to access SQLite
lock = threading.Lock() 

def synchronous(f):
    def call(*args, **kwargs):
        lock.acquire()
        try:
            return f(*args, **kwargs)
        finally:
            lock.release()
    return call


class Cache:
    """Cache pages"""
    
    @synchronous
    def __init__(self,db_name='html_cache.db'):

        self.create(db_name)
    
    def create(self,db_name='html_cache.db'):
        """Create and connect SQLite Database
        """
        self.conn = sqlite3.connect(db_name,timeout=100,isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.conn.text_factory = lambda x: unicode(x, 'utf-8', 'replace')
        self.curs = self.conn.cursor()

        #create if htmls tables dosen't exist
        self.curs.execute('''CREATE TABLE if not exists htmls(url VARCHAR(255) UNIQUE,content TEXT,size INTEGER);''')
        self.conn.commit()

    @synchronous
    def set(self,url,data,trytimes=1):
        """Save page data into caches
        """
        self.set_(url, data, trytimes)


    def set_(self,url,data,trytimes=1):
        if DEBUG:
            print "Save %s into caches " % (url)

        try:
            self.curs.execute("insert into htmls values(?,?,?);", (url,data,len(data)))
            self.conn.commit()
            return
        except sqlite3.IntegrityError:
            if DEBUG:
                print "%s already exist" % (url)
            return
        except Exception, e: # for example "database is locked"
            if DEBUG:
                print 'error from set_'
                print e
            
            self.conn.close()
            self.create()
            
            if trytimes>0:
               self.set_(url, data, trytimes-1)
            else:    
                return


    @synchronous
    def get(self,url,trytimes=1):
        """Get page from caches
        """
        return self.get_(url, trytimes)
        
        
    def get_(self,url,trytimes=1):
        if DEBUG:
            print "Try to get %s from caches " % (url)
        
        try:        
            self.curs.execute("select * from htmls where url=?;" ,(url,))
            row = self.curs.fetchone()
            if row:
                # find the cache data
                return row[1]
            return ''
        except Exception, e:
            if DEBUG:
                print 'error from get_'
                print e
            
            self.conn.close()
            self.create()
            
            if trytimes>0:
               return self.get_(url, trytimes-1)
            else:    
                return ''


if __name__ == '__main__':
    # test performance of Cache class
    cache = Cache()
    cache.set('http://www.redicecn.com', 'This is redice\'s blog!')
    print cache.get('http://www.redicecn.com')