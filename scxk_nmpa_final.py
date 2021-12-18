import requests
import json

cities = [
    "京",
    "津",
    "冀",
    "晋",
    "内",
    "辽",
    "吉",
    "黑",
    "沪",
    "苏",
    "浙",
    "皖",
    "闽",
    "赣",
    "鲁",
    "豫",
    "鄂",
    "湘",
    "粤",
    "桂",
    "琼",
    "川",
    "贵",
    "云",
    "渝",
    "藏",
    "陕",
    "甘",
    "青",
    "宁",
    "新",
    # "港",
    # "澳",
    # "台",
]
headers = {
    'Origin':
        'http://scxk.nmpa.gov.cn:81',
    'Referer':
        'http://scxk.nmpa.gov.cn:81/xk/',
    'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
}


def get_all_id(kw: str) -> list:

    ids = list()
    page_count = get_pages_status(kw)["page_count"]
    total_count = get_pages_status(kw)["total_count"]
    print("{} 的总共数据条数{}".format(kw,total_count))
    # 页数小于50:
    if page_count <= 50 and page_count > 0:
        ids = get_pages(page_count, kw)
        print("关键词{}的查询条数{}".format(kw,len(ids)))
    else:
        print(kw, "开始按年查找")
        year = 2016
        while len(ids) < total_count:
            print("year search loop")
            kw_year = kw + str(year)
            total_amount = get_pages_status(kw_year)["total_count"]
            page_amount = get_pages_status(kw_year)["page_count"]
            if page_amount <= 50:
                ids.extend(get_pages(page_amount,kw_year))
                print("{}:{}".format(kw_year, total_amount))
            else:
                print(kw_year, "开始按编号查找")
                num = 0
                print("ids",len(ids), "total_amount", total_amount)
                ids_year = list()
                while len(ids_year) < total_amount:
                    kw_num = kw_year + "{:0>2}".format(num)
                    print("查找总数据条数:", total_amount,"以获取条数:", len(ids_year),"kw:",kw_num)
                    pages = get_pages_status(kw_num)["page_count"]
                    print(" 关键词:", kw_num)
                    ids_year.extend(get_pages(pages,kw_num))
                    num += 1
                ids.extend(ids_year)
                print("ids_year",len(ids_year),kw_year)
            year += 1
    return ids


def get_ids_by_year(kw, total) -> list:
    year = 2016
    ids = list()
    kw = kw + str(year)
    while len(ids) < total:
        pass


def get_pages(page, kw) -> list:
    """获取所有分页的id."""
    id_list = list()
    for i in range(1, page + 1):
        data = {
            'on': 'true',
            'page': i,
            'pageSize': '15',
            'productName': kw,
            'conditionType': '1',
            'applyname': '',
            'applysn': '',
        }
        list_url = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsList"
        response = requests.post(url=list_url, data=data, headers=headers)
        result = response.json()
        # total_count = result["totalCount"]
        # page_count = result["pageCount"]
        ids = [i["ID"] for i in result["list"]]
        id_list.extend(ids)
    return id_list

def get_pages_status(kw) -> dict:
    """获取分页总数."""
    pages_status = dict()
    list_url = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsList"
    data = {
        'on': 'true',
        'page': "1",
        'pageSize': '15',
        'productName': kw,
        'conditionType': '1',
        'applyname': '',
        'applysn': '',
    }
    response = requests.post(url=list_url, data=data, headers=headers)
    result = response.json()
    page_count = result["pageCount"]
    total_count = result["totalCount"]
    pages_status["page_count"] = page_count
    pages_status["total_count"] = total_count
    return pages_status

def get_detail(id: str) -> dict:
    url = "http://scxk.nmpa.gov.cn:81/xk/itownet/portalAction.do?method=getXkzsById"
    data = {"id": id}
    response = requests.post(url=url, data=data, headers=headers)
    result = response.json()
    detail_data = result
    return detail_data


def save_data(fp, data) -> None:
    json.dump(data, fp, ensure_ascii=False, sort_keys=True, indent=4)


def main():
    id_all = list()
    for city in cities:
        kw = city + "妆"
        ids = get_all_id(kw)
        id_all.extend(ids)
        print("总共已经获取id数",len(id_all))
    # id_all = get_all_id("粤妆")
    # print(len(id_all))
    # print(len(set(id_all)))
    details = list()
    for id in id_all:
        print(" 正在抓取 id: {}的详情信息".format(id))
        details.append(get_detail(id))
    fp = open("./results.json", "w")
    json.dump(details, fp, ensure_ascii=False, sort_keys=True, indent=4)



if __name__ == "__main__":
    main()
