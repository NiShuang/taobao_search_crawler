import datetime
import requests
import re
import json
import openpyxl
import mysql.connector


class TaobaoCrawler:
    def __init__(self):
        # 如果爬虫失效，cookie信息需要及时更新
        self.cookie = '_samesite_flag_=true; cookie2=148e00b715ea5f51b02ae40f00ff1679; t=335a385901210ee2473af124fbf3f1a7; _tb_token_=357e98e91713; cna=LsYsGbOKj3wCAXeIWqY3hVRi; xlly_s=1; sgcookie=E100S0BruDWyjWf3VHK%2Fy%2BAFe7gFSudfphCChjoEvfX2Y8FLDsscXB%2Bb3QkQD15OW2%2BaasNR%2BhdBfYDb4xapsB1Y9A%3D%3D; uc3=lg2=UIHiLt3xD8xYTw%3D%3D&id2=UonciUs0wvLz%2Bg%3D%3D&vt3=F8dCuw1WQTp8bb88hT4%3D&nk2=CNu7fvUK%2FEvBzGe9; csg=3c002717; lgc=klqbtnsns123; dnk=klqbtnsns123; skt=374481f92e885dba; existShop=MTYyMzc0MDEwMA%3D%3D; uc4=id4=0%40UOE2TvXBiZgbbixofj36CmHkpueN&nk4=0%40Cr41%2F76IEx0j3iF0t2sGFj3mRQ%2BN%2BUs%3D; tracknick=klqbtnsns123; _cc_=VT5L2FSpdA%3D%3D; mt=ci=7_1; hng=CN%7Czh-CN%7CCNY%7C156; thw=cn; enc=t60ygk%2B9lrYlq8HaMbk8FBTVED0hTbPO4bY1U2qwXQlFPZwunC119%2BYLENYEomOcYm1CsiHZdRJgqwWWXo6ldA%3D%3D; alitrackid=i.taobao.com; lastalitrackid=i.taobao.com; uc1=existShop=false&pas=0&cookie21=W5iHLLyFeYFnNZKBCYQf&cookie14=Uoe2zs7efaTuKA%3D%3D&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D; _m_h5_tk=4adc8a4f589945ac32a12e964cd62ebd_1623762094655; _m_h5_tk_enc=88cc6b80890f4f1be20df8ed03d7f7bf; _uab_collina=162375313714987702802518; x5sec=7b227365617263686170703b32223a223266363230366266366334383339663830376637383332653361623763333739435066546f6f5947455069636836656a36632b444c526f4d4d5467334d446b794e7a59774e4473784d4b6546677037382f2f2f2f2f77453d227d; JSESSIONID=75BCE2616866C1F8E9B3F20AE6940CFF; tfstk=cHGdB3Tp4FQLnwatuvpMFDWfJVTGZ8JT49ZcwelljgO9Dl1RimGmMrc6RrNgPFC..; l=eBLPUYL7j-hxb3uoBOfwlurza77OSIRxBuPzaNbMiOCPOufp5V_lW6OTczY9C3hVh65WR3lqRWpDBeYBcIv4n5U62j-la_kmn; isg=BNDQjnyBhJsvl1jykn_PfyCsoRgimbTjqUIjJ8qhnCv-BXCvcqmEcyY32M3lhGy7'
        # 输出的Excel文件路径名
        self.target_path = '/Users/insta360/Downloads/result.xlsx'
        self.host = 'localhost'
        self.port = 3306
        # 用户名
        self.user = 'root'
        # 密码
        self.password = '12345678'
        # 数据库名
        self.db = 'crawler'
        self.charset = 'utf8'

    def main(self, product, page_num):
        data = []
        for i in range(1, page_num + 1):
            data.extend(self.search(product, i))

        items = []
        for item in data:
            items.append(self.parse_item(item))
        # self.save_to_excel(items)
        self.save_to_db(items)

    def connect_database(self):
        return mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            passwd=self.password,
            db=self.db,
            charset=self.charset,
            auth_plugin='mysql_native_password'
        )

    # 商品搜索
    def search(self, product, page):
        keyword = product.replace(' ', '+')
        date = datetime.date.today().strftime('%Y%m%d')
        url = 'https://s.taobao.com/search?q=' + keyword + '&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_' + date + '&ie=utf8&sort=sale-desc' + '&s=' + str((page - 1) * 44)
        print(url)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': 'Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'upgrade-insecure-requests': '1',
            'cookie': self.cookie
        }
        try:
            response = requests.get(url, headers=headers).text
            pattern = re.compile('g_page_config = (.*?)g_srp_loadCss', re.S)
            res = re.search(pattern, response)
            groups = res.groups()
            json_str = groups[0]
            json_str = json_str[0: json_str.rfind(';')]
            json_data = json.loads(json_str)
            return json_data['mods']['itemlist']['data']['auctions']
        except:
            print('Cookie 过期，请更新Cookie')
            exit()


    def parse_item(self, item):
        sales = ''
        if 'view_sales' in item:
            sales = item['view_sales']
        return [item['nid'], item['raw_title'], item['view_price'], sales,
                    'https:' + item['detail_url'], 'https:' + item['pic_url'], item['nick'], 'https:' + item['shopLink'], item['item_loc'], '天猫' if item['shopcard']['isTmall'] else '淘宝']

    def save_to_db(self, data):
        conn = self.connect_database()
        cursor = conn.cursor()

        sql = 'DELETE FROM taobao_commodity'
        cursor.execute(sql)
        conn.commit()

        sql1 = 'INSERT INTO taobao_commodity(`commodity_id`, `commodity`, `price`, `sales`, `link`, `pic_url`, `shop`, `shop_link`, `area`, `site`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.executemany(sql1, data)
        conn.commit()
        print('已保存至数据库')

    # 导出excel
    def save_to_excel(self, data):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(['商品id', '商品标题', '价格', '销量', '链接', '图片链接', '店铺', '店铺链接', '地区', '站点'])
        for item in data:
            ws.append(item)
        wb.save(self.target_path)

if __name__ == '__main__':
    crawler = TaobaoCrawler()
    # 采集销量排名前n页的口红信息
    crawler.main('口红', 3)


