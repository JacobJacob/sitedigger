# coding:utf-8
# httpcookie.py
# httpcookie Class 
# by redice

import re

class httpcookie:
    def __init__(self):
        self.cookie_cache = {}
        
    def cookie2dict(self,cookie):
        """
        Convert Cookie to Dict
        """
        cookie_dic = {}
        param_array = cookie.split(';')
        for param in param_array:
            if not param: continue
            if '=' not in param: continue

            param = param.strip()

            #type1: ASPSESSIONIDCCSQQCDB=NKPFHJIAKJMBELINHGFJNDMC; 
            if '&' not in param:
                name,equal,value = param.partition('=')
                if not name: continue
                
                cookie_dic[name] = value
            else:
                #type2: blog=pass=123456&user=redice
                farther,equal,pairs = param.partition('=')

                pairs = pairs.split('&')
                children = {}
                for pair in pairs:
                    name,eaual,value = pair.partition('=')
                    if not name: continue
                    
                    children[name] = value

                cookie_dic[farther] = children

        return cookie_dic


    def dict2cookie(self,dic):
        """
        Convert Dict to Cookie
        """
        cookie = ''
        for key in dic:
           value = dic[key]

           if isinstance(value,basestring):
               cookie = cookie + key + '=' + value + ';'
               
           if isinstance(value,dict):
              subdic = value
              cookie = cookie + key + '='

              for key in subdic:
                  value = subdic[key]
                  cookie = cookie + key + '=' + value + '&'

              if cookie[-1]=='&':
                  cookie = cookie[0:-1]

              cookie = cookie + ';'   

        return cookie


    def tidy_cookie(self,cookie):
        """
        Tidy cookie
        """
        param_array = cookie.split(';')
        cookie = ''
        for param in param_array:
            if not param: continue
            if '=' not in param: continue

            param = param.strip()

            name,equal,value = param.partition('=')

            if name.lower() == 'expires' or name.lower() == 'path': continue

            cookie = cookie + param + ';'


        return cookie            



    def merge_cookie(self,cookie_old,cookie_new):
        """
        Merge two cookie
        """
        dic_old =  self.cookie2dict(cookie_old)
        
        dic_new =  self.cookie2dict(cookie_new)

        dic_old.update(dic_new)

        return self.dict2cookie(dic_old)

    

    def resolve_cookie(self,raw_cookie,default_domain = None):
        """
        Resolve cookie for httplib
        Store cookie by domain
        """
        cookies = {}
        raw_cookie = re.compile(r"expires=(.*?);?", re.DOTALL|re.IGNORECASE).sub('',raw_cookie)
        cookie_groups = raw_cookie.split(',')
        for _group in cookie_groups:

            pairs =  _group.split(';')
            _domain = ''
            tmp = ''
            for pair in pairs:
                if '=' not in pair: continue
                pair = pair.strip()

                name,equal,value = pair.partition('=')

                if name.lower() == 'domain':
                    _domain = value
                else:
                    if name.lower() == 'path': continue
                    tmp = tmp +  pair + ';'               

            if not _domain:
                _domain = default_domain if default_domain else 'unknow'

            if cookies.has_key(_domain):            
                cookies[_domain] = self.merge_cookie(cookies[_domain],tmp)
            else:
                cookies[_domain] = tmp

        self.cookie_cache.update(cookies)


    def get_cookie(self,domain):
        """
        Get cookie by domain
        """
        cookie = ''
        if self.cookie_cache.has_key(domain):
            cookie = self.cookie_cache[domain]

        if self.cookie_cache.has_key('.'+domain):
            cookie = cookie + ';' + self.cookie_cache['.'+domain]
        
        hostname,dot,domain = domain.partition('.')
        if self.cookie_cache.has_key('.'+domain):
            cookie = cookie + ';' + self.cookie_cache['.'+domain]
        
        return cookie       


if __name__ == '__main__':

    #Test httpcookie

    cookie = httpcookie()

    cookie.resolve_cookie('MSPRequ=lt=1293416888&co=1&id=N; path=/;version=1, MSPOK=$uuid-24e2dac0-944a-45bc-86a4-9b2a4b6b779f; domain=login.live.com;path=/;version=1','login.live.com')
    print cookie.get_cookie('login.live.com')

    