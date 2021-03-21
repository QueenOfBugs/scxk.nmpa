# scxk.nmpa

国家药品监督管理局-所有化妆品生产许可信息爬取：

- 网站地址：http://scxk.nmpa.gov.cn:81/xk/
- 详情页地址：http://scxk.nmpa.gov.cn:81/xk/itownet/portal/dzpz.jsp?id=ed59438f34ae47e794f4c7ee5137c1f7

网站地址每页显示 15 条数据,显示数据是由 ajax 请求获取,ajax 请求:

- Request URL:http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsList
- Request Method:POST
- User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36
- Origin: http://scxk.nmpa.gov.cn:81
- Referer: http://scxk.nmpa.gov.cn:81/xk/
- form data:

```
on: true
page: 4
pageSize: 15
productName:
conditionType: 1
applyname:
applysn:
```

详情页的数据也是通过ajax请求获取，ajax请求:

- Request URL:http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsById
- Request Method:POST
- Origin: http://scxk.nmpa.gov.cn:81
- Referer: http://scxk.nmpa.gov.cn:81/xk/itownet/portal/dzpz.jsp?id=ed59438f34ae47e794f4c7ee5137c1f7
- User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36
- form data:

```
id: ed59438f34ae47e794f4c7ee5137c1f7
```


scxk.py: 初步实现数据爬取的功能，尝试批量爬取，并查看程序运行时所占用内存情况.
