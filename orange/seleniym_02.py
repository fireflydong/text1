from selenium import webdriver
import time
from lxml import etree

driver = webdriver.Chrome()
driver.get("https://www.itjuzi.com/user/login")
time.sleep(1)
driver.find_element_by_id("create_account_email").send_keys("17896050141")
driver.find_element_by_id("create_account_password").send_keys("nihaoma")
driver.find_element_by_id("login_btn").click()
cookie = driver.get_cookies()
driver.get("http://radar.itjuzi.com/company")

driver.maximize_window()

targetElem = driver.find_element_by_xpath("//input[@id='goto_page_btn']")
time.sleep(2)
k=1

driver.get("http://radar.itjuzi.com/investevent")
targetElem = driver.find_element_by_xpath("//input[@id='goto_page_btn']")
f = open("tourongzi.txt","w")
k=0
while True:
    try:
        driver.execute_script("arguments[0].scrollIntoView();", targetElem)
        # driver.find_element_by_xpath("//input[@id='goto_page_btn']").click()
        response = driver.page_source
        html = etree.HTML(response)
        id = html.xpath("//tr//span//a/@href")



        for url_id in id:
            f.write(url_id + "\n")
            print(url_id)

        driver.find_element_by_xpath("//li[@class='next']/a").click()
        k+=1
        for i in range(1,4):
            time.sleep(i)

        if k == 2346:  # 结束循环
            f.close()
            break
    except Exception as e:
        pass
    # finally:
    #     k+=1
