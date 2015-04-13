# sitedigger使用举例/Examples #

### 下载网页/Download webpage ###
```
>>> from sitedigger import download
>>> down = download.DownLoad()
>>> result = down.getHtml("http://www.redicecn.com/tools/sitedigger.php")
getHtml:  http://www.redicecn.com/tools/sitedigger.php
Try to get http://www.redicecn.com/tools/sitedigger.php from caches 
Save http://www.redicecn.com/tools/sitedigger.php into caches 
>>> print result
{'html': 'hello world!<br/>', 'cookie': 'PHPSESSID=a0ea3e7e70e30a95222908708ec6e628; '}
```

### 模拟登录,不使用缓存/Login Simulation, without caching ###
```
>>> from sitedigger import download
>>> down = download.DownLoad()
>>> post_data = {'user':'redice','pass':'123456'}
>>> result = down.getHtml("http://www.redicecn.com/tools/sitedigger.php",post_data=post_data,cached=False)
getHtml:  http://www.redicecn.com/tools/sitedigger.php
>>> print result
{'html': 'Welcom! Your user_name:redice', 'cookie': 'PHPSESSID=a5133fb6b4059e306e9436c9effc6c83; '}
```

### 使用代理下载页面/Download webpage with proxy ###
```
>>> from sitedigger import download
>>> down = download.DownLoad()
>>> print down.getHtml("http://www.redicecn.com/tools/ip.php?showproxy=0",cached=False)
getHtml:  http://www.redicecn.com/tools/ip.php?showproxy=0
{'html': '61.185.143.178', 'cookie': ''}
>>> down = download.DownLoad(proxy="60.175.203.243:8080")
>>> print down.getHtml("http://www.redicecn.com/tools/ip.php?showproxy=0",cached=False)
getHtml:  http://www.redicecn.com/tools/ip.php?showproxy=0
{'html': '60.175.203.243', 'cookie': ''}
```

### 下载HTTPS页面/Download HTTPS webpage ###
```
>>> from sitedigger import download
>>> down = download.DownLoad()
>>> print down.getHtml("https://www.alipay.com",cached=False)
getHtml:  https://www.alipay.com
getHttps:  https://www.alipay.com
{'html': '\r\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" ...
```

### 获取301/302/303页面重定向/Fetching 301/302/303 redirection ###
```
>>> from sitedigger import download
>>> down = download.DownLoad()
>>> result = down.getLocation("http://www.redicecn.com/tools/redirect.php",cached=False)
getLocation:  http://www.redicecn.com/tools/redirect.php
>>> print result
http://www.redicecn.com/tools/ip.php
```


---


## 使用授权/License ##
This code is licensed under the LGPL license.

## 声明/Statement ##
<p>sitedigger模块中的common.py以及cache.py采用了Richard的webscraping中的部分代码，在此予以声明，并对Richard表示感谢。</p>
<p>webscraping的项目主页是<a href='http://code.google.com/p/webscraping/'>http://code.google.com/p/webscraping/</a></p>

## 联系我/Contact ##
E-mail: redice@163.com<br />
Gtalk: admin@site-digger.com