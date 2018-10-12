#-*-coding:utf-8-*-
import requests
import hashlib
from bs4 import BeautifulSoup
import re
import time
import imghdr
import os
from aip import AipFace
import base64

def regist_face_client():
    APP_ID="11230930"
    API_KEY="GQp9GcnCsR9Njd1kxNaNleEA"
    SECRET_KEY="zIydrPWzUMHina4FMo6RGnOIGU2hkCwo"
    client = AipFace(APP_ID, API_KEY, SECRET_KEY)
    return client

client = regist_face_client()

def get_img_curl(page):
    url_format = "http://111.205.196.50:8081/News/NewsList.net?page=%d&newstype=5&keywords=" % page
    return url_format

def get_md5_value(str):
    my_md5 = hashlib.md5()  # 获取一个MD5的加密算法对象
    my_md5.update(str)  # 得到MD5消息摘要
    my_md5_Digest = my_md5.hexdigest()  # 以16进制返回消息摘要，32位
    return my_md5_Digest

#原链接找不到图片，通过名字搜索一个图片链接
def get_imgcurl_by_search(session, name):
    tmp_name = re.findall("\((.*?)\)", name)
    if len(tmp_name) > 0:
        name = tmp_name[0]

    curl = "http://111.205.196.50:8081/Search.aspx?username=%s" % name
    res_news = session.get(curl)
    #print res_news.text
    search_res =  re.findall("img.*", res_news.text)
    #print len(search_res)
    if len(search_res) > 0:
        #print search_res[0]
        img_res = re.findall('src="(.*?)"', search_res[0])
        img_curl ="http://111.205.196.50:8081%s" %  img_res[0]
        return img_curl
    else:
        print "invalid name :%s" % name
        return None

def read_image_content(file_path):
    with open(file_path, "rb") as fp:
        return fp.read()

def get_face_score(file_content):
    base64_content = base64.b64encode(file_content)
    parse_res = client.detect(base64_content, "BASE64", options={"face_field": "age,gender,beauty,qualities"})
    if parse_res.has_key("result"):
        if parse_res["result"] is not None and parse_res["result"].has_key("face_list"):
            for key in  parse_res["result"]["face_list"]:
                return key['beauty']
    return 0

#创建图片，通过Curl链接
def create_image(curl, file_name):
    file_img = open(file_name, "wb")
    img_pic = requests.get(curl)
    file_img.write(img_pic.content)
    file_img.close()
    img_type = imghdr.what(file_name)
    if img_type == None:
        #print "invalid file_name:%s\n" % file_name.decode("gbk").encode("utf8")
        os.remove(file_name)
        return False
    else:
        image_content = read_image_content(file_name)
        face_score = get_face_score(image_content)
        file_split = file_name.split('/')
        #print file_split
        new_name = "bin/%d_%s" %(face_score, file_split[1])
        print new_name
        os.rename(file_name, new_name)

    return True

def login():
    session = requests.session()
    # res = session.get('http://my.its.csu.edu.cn/').content
    user_name = 'wanxiubin'
    passw='wwxxbb456'
    md5_passw = get_md5_value(passw)
    #print md5_passw
    login_data = {
        'action': "LoginValid",
        'userID': user_name,
        'userPwd': md5_passw,
        'ischeck': '1'
    }
    session.post('http://111.205.196.50:8081/AjaxHandlers/UserLogin.ashx', data=login_data)
    res = session.get('http://111.205.196.50:8081/Default.aspx')
    tmp_name = 0
    for i in range(0, 133):
        img_url = get_img_curl(i)
        #res_news = session.get('http://111.205.196.50:8081/News/NewsList.net?page=0&newstype=5&keywords=')
        res_news = session.get(img_url)
        #print res_news.text
        pic_div = re.findall('<div(.*?)</dd></dl></div></div>', res_news.text, re.S)
        for data_div in pic_div:
            bs_obj = BeautifulSoup(data_div, "html.parser")
            bs_res = bs_obj.find_all("h3")
            tmp_names =  bs_res[0].string.encode("utf8").split("   ")
            user_name = tmp_names[1]
            file_name = "bin/%s.jpg" % user_name
            file_name =  file_name.decode("utf8").encode("gbk")
            #print file_name
            re_curl = re.findall('img src=(.*?) height', data_div, re.S)
            img_curl = "http://111.205.196.50:8081" + re_curl[0]
            ret = create_image(img_curl, file_name)
            if ret == False:
                img_curl = get_imgcurl_by_search(session, user_name)
                #print img_curl
                if img_curl is not None:
                    create_image(img_curl, file_name)


login()