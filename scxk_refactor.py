"""scxk.nmpa 网站上化妆品许可信息的抓取."""

import json
import os
import psutil
import requests


def get_id_by_num(num: int) -> list:
    id_list = []
    url = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsList"
    headers = {
        'Origin':
            'http://scxk.nmpa.gov.cn:81',
        'Referer':
            'http://scxk.nmpa.gov.cn:81/xk/',
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    }

    for page_index in range(1, 51):
        data = {
            'on': 'true',
            'page': page_index,
            'pageSize': '15',
            'productName': num,
            'conditionType': '1',
            'applyname': '',
            'applysn': '',
        }

        # print('index{}num{}'.format(page_index, num))
        ids_json = {}
        try:
            ids_json = requests.post(url=url, data=data, headers=headers).json()
        except:
            ids_json['list'] = []
        # print(ids_json['list'])

        if ids_json['list'] == []:
            # print("{} page {}can't get info".format(num, page_index))

            break
        # print('index{}num{}'.format(page_index, num))

        for di in ids_json['list']:
            id_list.append(di['ID'])

    return id_list


def get_max_num(num: int) -> int:

    url = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsList"
    headers = {
        'Origin':
            'http://scxk.nmpa.gov.cn:81',
        'Referer':
            'http://scxk.nmpa.gov.cn:81/xk/',
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    }
    data = {
        'on': 'true',
        'page': 1,
        'pageSize': '15',
        'productName': num,
        'conditionType': '1',
        'applyname': '',
        'applysn': '',
    }
    response = requests.post(url, headers=headers, data=data)
    max_num = response.json()['totalCount']
    print(response.json())
    print(num)

    return max_num


def get_id_all(url: str) -> list:
    id_list = []
    # 网页上最多只显示50页数据
    # 按许可编号查询，许可编号规律：年份+编号(1-9999)

    for year in range(20160000, 20220000, 10000):
        break_count = 0
        # 如果连续100的编号没有读取到
        max_num = get_max_num(int(year / 10000))

        for num in range(1, max_num):
            num_ids = get_id_by_num(year + num)

            if num_ids == []:
                break_count = break_count + 1
            else:
                id_list.extend(num_ids)
                print(len(id_list))

        if break_count == 100:
            break

    print(u'当前占用:%.4f GB' %
          (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024 / 1024))

    # json.dump(id_list, open('ids.json', 'w'))

    return id_list


def get_item_info(id: str) -> dict:

    # 根据ID获取详情页信息,当该id被删除了(过期)，记录在expierd.json中
    r"""
    返回详情页json字典
    :param: id:  id of asd

     """
    url_info = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsById"
    headers = {
        'Origin':
            'http://scxk.nmpa.gov.cn:81',
        'Referer':
            'http://scxk.nmpa.gov.cn:81/xk/itownet/portal/dzpz.jsp?id=' + id,
        'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
    }
    data = {
        'id': id,
    }
    response = requests.post(url_info, headers=headers, data=data)

    item_info: dict = response.json()

    return item_info


def store_item_info(info: dict) -> None:
    pass


if __name__ == "__main__":
    url_id = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsList"

    # 下面的运行一次，将所有id存到本地ids.json
    id_list: list = get_id_all(url_id)
    print(len(id_list))
    json.dump(id_list, open('ids.json', 'w'), ensure_ascii=False)

    # id_list: list = json.load(open('ids.json', 'r'))
    # print(len(id_list))
    # print(type(id_list[0]))
    # print(get_item_info(id_list[0]))

    fp = open('items.json', 'a')
    fp.write('[')
    for id in id_list[:-1]:
        try:
            item_info = get_item_info(id)
        except Exception as e:
            print('{}error{}'.format(id, e))
        print(item_info)
        json.dump(item_info, fp, ensure_ascii=False)
        fp.write(',')
        print(id)
    item_info = get_item_info(id_list[-1])
    json.dump(item_info, fp, ensure_ascii=False)
    fp.write(']')
