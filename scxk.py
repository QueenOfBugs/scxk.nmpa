import requests
import json
import psutil
import os

if __name__ == "__main__":
    pass
    # 获取id

    headers = {
        'Origin': 'http://scxk.nmpa.gov.cn:81',
        'Referer': 'http://scxk.nmpa.gov.cn:81/xk/',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    }

    id_list = []

    # http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsList

    url = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsList"
    for i in range(1, 10):
        page_index = i

        data = {
            'on': 'true',
            'page': page_index,
            'pageSize': '15',
            'productName': '',
            'conditionType': '1',
            'applyname': '',
            'applysn': '',
        }
        json_ids = requests.post(url, data=data, headers=headers).json()
        for dic in json_ids['list']:
            id_list.append(dic['ID'])

    print(id_list)

    # 获取详情
    items_list = []
    url_info = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsById"
    for item_id in id_list:
        data_info = {
            'id': item_id,
        }
        headers_info = {
            'Origin': 'http://scxk.nmpa.gov.cn:81',
            'Referer': 'http://scxk.nmpa.gov.cn:81/xk/itownet/portal/dzpz.jsp?id=' + item_id,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }
        response_item = requests.post(
            url=url_info, data=data_info, headers=headers_info)
        # response_item.encoding = 'utf-8'
        item_info = response_item.json()
        # print(item_info)
        # print(json.dumps(item_info))
        print(u'当前占用:%.4f GB'% (psutil.Process(os.getpid()).memory_info().rss/1024/1024/1024))
        items_list.append(item_info) 
    print(u'全部读取到列表时占用:%.4f GB'% (psutil.Process(os.getpid()).memory_info().rss/1024/1024/1024))

    with open('items.json', 'w',) as fp:
        json.dump(items_list, fp, ensure_ascii=False)
        print(u'当前占用:%.4f GB'% (psutil.Process(os.getpid()).memory_info().rss/1024/1024/1024))

    print(u'当前占用:%.4f GB'% (psutil.Process(os.getpid()).memory_info().rss/1024/1024/1024))

