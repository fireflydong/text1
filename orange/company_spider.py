import requests
import time
import datetime
from logger import Logger
from lxml import etree
import random
import pymongo
import json


class OrangeCompany:
    def __init__(self):
        self.company_times = 0
        self.f_times = 0
        self.m_times = 0
        self.p_times = 0
        self.a_times=0
        self.n_times=0
        self.mongo_ip = "127.0.0.1"
        self.mongo_port = 27017
        self.mongo_db = "orange"
        self.client = pymongo.MongoClient(self.mongo_ip, self.mongo_port)
        self.collection = self.client[self.mongo_db]
        self.url = 'https://www.itjuzi.com/company/{}'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'

        }
        self.data = {'identity': '17896050141',
                     'password': 'nihaoma'}

    def get_content(self):
        s = requests.session()
        logger.info("尝试登陆")
        s.post("https://www.itjuzi.com/user/login?redirect=&flag=&radar_coupon=", headers=self.headers, data=self.data)
        logger.info("登陆成功")
        time.sleep(1)
        # 获取公司/投资
        logger.info("开始爬取公司/项目")
        with open("compony7.txt", "r")as f:
            label = 1
            for line in f.readlines():

                try:
                    url_id = line.split("\n")[0]

                    response = s.get(self.url.format(url_id), headers=self.headers)
                except Exception as e:
                    logger.info(self.url.format(line.split("\n")[0]) + "未请求成功")
                    logger.info(e)
                if response.status_code == 200:
                    response = response.content.decode("utf-8","ignore")

                    self.parse_content(response, label,url_id)

                else:
                    logger.info(self.url.format(line.split("\n")[0] + "状态码为" + response.status_code))

        # 获取投融资速递
        logger.info("开始爬取投融资速递")
        with open("tourongzi.txt", "r")as f:
            label = 2
            for line in f.readlines():
                # self.f_times+=1
                try:
                    url = line.split("\n")[0]
                    response = s.get(url, headers=self.headers)
                except Exception as e:
                    logger.info(e)
                    logger.info("&s未请求成功" % url)
                if response.status_code == 200:
                    response = response.content.decode("utf-8","ignore")
                    self.parse_content(response, label)
                else:
                    logger.info("%s状态码为&s" % (url, response.status_code))


        # 开始爬取投资机构
        logger.info("开始爬投资机构")
        url_list = "https://www.itjuzi.com/investfirm/{}"
        for i in range(1,7139):

            item = {}
            try:
                url = url_list.format(i)

                response = s.get(url, headers=self.headers)
            except Exception as e:
                logger.info("&s未请求成功" % url)
            response = response.content.decode("utf-8","ignore")

            html = etree.HTML(response)
            item["name"] = html.xpath("//div[@class='inner-box']//h1/text()")
            item["logo"] = html.xpath("//div[@class='inner-box']/div[@class='logo-box']/img/@src")
            item["website"] = html.xpath("//a[@class='website-box']/@href")
            item["introduce"] = html.xpath("//ul[@class='list-unstyled base-intro']//text()")
            item["partner"] = html.xpath("//div[@class='col-md-4']//text()")
            item["events"] = html.xpath("//table[@class='list-invecase']//td/span/text()")
            item["exit_events"] = html.xpath("//div[@class='logo-wall']//a//text()")
            item["member"] = html.xpath("//ul[@class='list-prodcase width100']/li//p/text()")
            label = 3
            self.save_mongo(item, label)
            time.sleep(random.uniform(1, 5))

        # 开始爬投资人物
        logger.info("开始爬创投人物")
        url_person_list = 'https://www.itjuzi.com/person?page={}'

        for i in range(5961):
            time.sleep(random.uniform(1, 5))
            label = 4
            url = url_person_list.format(i)
            try:
                response = s.get(url, headers=self.headers)
            except Exception as e:
                logger.info("%s未请求成功" % url)
            html = etree.HTML(response.content.decode("utf-8","ignore"))
            url_list = html.xpath(
                "//ul[@class='list-main-personset person-list-result']/li/i[@class='left']/a[1]/@href")
            for url in url_list:
                item = {}
                time.sleep(random.uniform(1, 5))
                try:
                    response = s.get(url, headers=self.headers)
                except Exception as e:
                    logger.info("%s未请求成功" % url)
                html = etree.HTML(response.content.decode("utf-8","ignore"))
                item["person_introduce"] = html.xpath("//div[@class='block block-v']//text()")
                item["experience"] = html.xpath("//i[@class='incinfo leri long']//span//text()")
                self.save_mongo(item, label)
        # 获取专辑
        logger.info("开始爬取专辑")
        label=5
        while True:

            k = 1
            url = "https://www.itjuzi.com/tag_tree/get_album_info?page={}"
            try:
                response = requests.get(url.format(k), headers=self.headers)
                response = response.content.decode()
            except:
                logger.info("请求失败")
                logger.info(url)
            finally:
                k+=1
            time.sleep(random.uniform(1, 4))


            if len(response) > 100:
                response = json.loads(response)
                data_list = response["data"]
                for data in data_list:
                    item = {}
                    url = data["site_album_url"]
                    try:
                        response = requests.get(url, headers=self.headers)
                        response = response.content.decode()
                    except:
                        logger.info("请求失败")
                        logger.info(url)
                    html = etree.HTML(response)

                    introduce = str(html.xpath("//div[@class='infopad']//text()"))
                    introduce = introduce.replace(" ", "")
                    introduce = introduce.replace("\\n", "")
                    item["introduce"] = introduce
                    company = str(html.xpath("//ul[@class='list-main-icnset widthfreen list-album-com']/li//text()"))
                    company = company.replace(" ", "")
                    company = company.replace("\\n", "")
                    item["company"] = company
                    print(item)
                    self.save_mongo(item,label)
                    time.sleep(random.uniform(1, 4))

            else:

                break
        #对新闻资讯进行爬取
        label=7
        logger.info("开始爬新闻资讯")

        while True:
            url = 'https://www.itjuzi.com/tag_tree/get_fifter_news_info?page={}'

            k = 1
            url = url.format(k)
            try:
                response = requests.get(url, headers=self.headers).content.decode()

            except:
                logger.info(url)
                logger.info("连接请求失败")
            finally:
                k += 1

            if len(response) > 100:
                response = json.loads(response)

                data_list = response["data"]
                for data in data_list:
                    item = {}

                    item["title"] = data["com_new_name"]
                    try:
                        url = data["com_new_url"]

                        response = requests.get(url, headers=self.headers).content.decode()

                        item["content"] = response

                    except:
                        logger.info(url)
                        logger.info("连接请求失败")
                    self.n_times+=1
                    self.save_mongo(item,label)


            else:
                break
        # 对千里马页面进行爬取
        label = 6
        with open("qianlima.txt", "r", encoding="utf-8")as f:
            response = f.readlines()
            html = etree.HTML(str(response))
            a = str(html.xpath("//tbody[@id ='thelistbody']/tr//text()"))
            a = a.replace("\\t", "")
            a = a.replace("\\n", "")
            a = a.replace("\\", "")
            a = a.replace("\'", "")
            item = a.replace("\"", "")
            # a = a.replace(",","")
            self.save_mongo(item, label)
    def parse_content(self, response, label,url_id=0):
        item = {}
        label = label

        html = etree.HTML(response)

        item["name"] = html.xpath("//h1/text()") + html.xpath("//div[@class='info-line']/h2/text()") + html.xpath(
            "//div[@class='info-line']/span/text()")
        item["website"] = html.xpath("//div[@class='link-line']//a/@href")
        item["logo"] = html.xpath("//div[@class='pic']//img/@src")
        item["label"] = html.xpath("//div[@class='tagset dbi c-gray-aset tag-list']//a/text()")
        item["base_photo"] = html.xpath("//div[@class='swiper-slide swiper-slide-prev']/a/img/@src")
        if label == 1:
            if len(item["logo"])>0:
                try:
                    response = requests.get(item["logo"][0],headers=self.headers).content
                except:
                    logger.info(url_id)
                    logger.info("logo图片请求失败")
                try:
                    with open("./photo/logo/%s.png" % url_id, "wb")as f:
                        f.write(response)
                except:
                    logger.info(url_id)
                    logger.info("logo图片存储失败")
            if len(item["base_photo"])>0:
                try:
                    response = requests.get(item["base_photo"][0],headers=self.headers).content
                except:
                    logger.info(url_id)
                    logger.info("base图片存储失败")
                try:
                    with open("./photo/base/%s.png" % url_id, "wb")as f:
                        f.write(response)
                except:
                    logger.info(url_id)
                    logger.info("base图片存储失败")
        item['base_info'] = html.xpath("//div[@class='block']//text()")
        item["financing"] = html.xpath("//tr[@class='feedback-btn-parent']/td[5]/a/@href")
        item["financing"] += html.xpath("//tr[@class='feedback-btn-parent']/td/span//text()")
        # 对融资页面进行爬取
        item["team"] = html.xpath("//li[@class='feedback-btn-parent first-letter-box-4js']//text()")
        item["product_info"] = html.xpath(
            "//ul[@class='list-unstyled product-list limited-itemnum']//a/@href") + html.xpath(
            "//ul[@class='list-unstyled product-list limited-itemnum']//div[@class='product-des line2']/text()")
        item["competitive_product"] = html.xpath("//ul[@class='list-main-icnset list-compete-info']/li//text()")
        item['analysis report'] = html.xpath("//ul[@class='list-unstyled analysis-report-list']//a/@href")
        item["news"] = html.xpath("//ul[@class='list-unstyled news-list']/li//text()")
        item["news_website"] = html.xpath("//ul[@class='list-unstyled news-list']/li//a/@href")
        # 新闻页面爬取
        try :
            for news_url in item['new_website']:
                response = requests.get(news_url,headers=self.headers)
                item[news_url]=response.content.decode("utf-8","ignore")
        except:
            pass
        item["Milepost"] = html.xpath("//div[@class='on-edit-hide']/p/text()")
        item["trademark_information"] = html.xpath("//div[@class='brand-wrap']//text()")
        item["IC_info"]= html.xpath("//table[@class='table table-bordered']//text()")
        item["comment"] = html.xpath("//div[@class='commitlist limited-itemnum']//div[@class='right']//text()")
        print(item)
        self.save_mongo(item, label)
        time.sleep(random.uniform(1, 5))



    def save_mongo(self, item, label):

        try:
            if label == 1:
                self.collection["company"].insert_one(item)
                self.company_times += 1
            elif label == 2:
                self.collection["financing"].insert_one(item)
                self.f_times += 1
            elif label == 3:
                self.collection["mechanism"].insert_one(item)
                self.m_times += 1
            elif label == 4:
                self.collection["Investment_person"].insert_one(item)
                self.p_times += 1
            elif label ==5:
                self.collection["Album"].insert_one(item)
                self.a_times+=1
            elif label==6:
                self.collection["qianlima"].insert(item)
                logger.info("千里马爬取完毕")
            elif label==7:
                self.collection["news_information"].insert(item)
        except Exception as e:
            logger.info(item)
            logger.info(label)
            logger.info("存储失败")
if __name__ == '__main__':
    logger = Logger().logger
    orange_company = OrangeCompany()
    response = orange_company.get_content()
    orange_company.client.close()
    logger.info("公司/项目爬取条数%s"% orange_company.company_times)
    logger.info("投融资速递爬取条数%s" % orange_company.f_times)
    logger.info("投资机构爬取条数%s" % orange_company.m_times)
    logger.info("创投人物爬取条数%s" % orange_company.p_times)
    logger.info("专辑爬取条数%s"%orange_company.a_times)
    logger.info("爬取新闻资讯条数%s"%orange_company.n_times)
