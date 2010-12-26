# coding:utf-8
# cookie function 
# by redice

def cookie2dict(cookie):
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


def dict2cookie(dic):
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


def tidy_cookie(cookie):
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



def merge_cookie(cookie_old,cookie_new):
    """
    Merge two cookie
    """
    dic_old =  cookie2dict(cookie_old)
    dic_new =  cookie2dict(cookie_new)

    dic_old.update(dic_new)

    return dict2cookie(dic_old)


if __name__ == '__main__':

    #Test cookie2dict & dict2cookie

    print tidy_cookie('ASPSESSIONIDCCSQQCDB=NKPFHJIAKJMBELINHGFJNDMC; Path=/; expires=Thu; 30-Oct-1980 16:00:00 GMT;')    
    
    cookie1 = 'ASPSESSIONIDCCSQQCDB=NKPFHJIAKJMBELINHGFJNDMC; blog=pass=123456&user=redice'
    cookie2 = 'blog=pass=654321&user=redice&sex=0'
    print merge_cookie(cookie1,cookie2)