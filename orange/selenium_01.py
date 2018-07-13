# coding=utf-8
from selenium import webdriver
import time

driver = webdriver.Chrome()
# driver = webdriver.PhantomJS()

#设置窗口大小
driver.maximize_window()  #最大化窗口
# driver.set_window_size(1920,1080) #设置窗口大小


driver.get('http://www.baidu.com') #请求地址

#定位input的标签，输入内容
driver.find_element_by_id("kw").send_keys("it桔子")

#点击百度一下
driver.find_element_by_id("su").click()


#保存页面图片
driver.save_screenshot("./baidu.png")

#获取页面源码,获取的是element的内容,能够交给lxml处理
# print(driver.page_source)

#获取cookie
print(driver.get_cookies())
print("*"*100)
print({i["name"]:i["value"] for i in driver.get_cookies()})

# 获取当期的url地址
print(driver.current_url)


time.sleep(3)
driver.quit()