#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/25 0025 11:18
# @Author  : Nan.Liu
# @Contact : 153011784@qq.com
# @File    : DoubanCrawler.py
# @Software: PyCharm
# @Desc    :
import urllib

import bs4
import expanddouban
import csv
from collections import defaultdict

'''
任务1实现函数构造对应类型和地区的URL地址
@:param category 分类 喜剧，动作，科幻之类  必传
@:param location 地区 美国 大陆 日本 必传
@:param form 形式 电影 电视剧 默认电影
@:param sort 排序类型 热度-T 时间-R 评价-S默认S
@:param range 分数 1-1，9，10，2-7之类 默认9,10

'''
def getMovieUrl(category, location,form='电影',sort='S',range='9,10'):

    sort_url='/tag/#/?sort='+sort
    range_url='range='+range

    category_url='tags='+form

    search_url= sort_url+'&'+range_url+'&'+category_url+','+category+','+location


    '''
    使用urllib.parse.urljoin #会消失
    '''
    # reueqst_url='https://movie.douban.com/tag/#/?'+search_url
    reueqst_url=urllib.parse.urljoin('https://movie.douban.com//tag/#/?',search_url)

    return  reueqst_url



'''
https://movie.douban.com/tag/#/: 豆瓣电影分类页面
sort=S: 按评分排序
range=9,10: 评分范围 9 ~ 10
tags=电影: 标签为电影
'''

#: 豆瓣电影分类页面
america_movie_url= getMovieUrl('喜剧','美国')
#  任务2: 获取电影页面 HTML
#html=expanddouban.getHtml(america_movie_url,loadmore=True,waittime=5)
# 任务3: 定义电影类
'''
电影类应该包含以下成员变量

电影名称
电影评分
电影类型
电影地区
电影页面链接
电影海报图片链接
name = “肖申克的救赎”
rate = 9.6
location = "美国"
category = "剧情"
info_link = "https://movie.douban.com/subject/1292052/"
cover_link = “https://img3.doubanio.com/view/movie_poster_cover/lpst/public/p480747492.jpg”
'''
class Movie(object):

    def __init__(self,name, rate, location, category, info_link, cover_link):
        self.name=name
        self.rate=rate
        self.location=location
        self.category=category
        self.info_link=info_link
        self.cover_link=cover_link

# 任务4: 获得豆瓣电影的信息
'''
通过URL返回的HTML，我们可以获取网页中所有电影的名称，评分，海报图片链接和页面链接，
同时我们在任务1构造URL时，也有类型和地区的信息，因为我们可以完整的构造每一个电影，并得到一个列表。
'''

def  getMovies(category, location):
    #电影列表用来存放电影信息
    movie_lists=list()
    #获取请求地址
    url=getMovieUrl(category,location)
    #获取url的html
    html = expanddouban.getHtml(url,loadmore=True,waittime=5)
    soup=bs4.BeautifulSoup(html,'html.parser')
    context_div=soup.find(id='app').find(class_='article').find(class_='list-wp',recursive =False)
    ul_list=soup.find(id='app').find(class_='article').find(class_='tags',recursive =False).find_all('ul',recursive =False)
    #地区
    movie_location=ul_list[-2].find(class_="tag-checked tag").text
    #类型
    movie_category=ul_list[1].find(class_="tag-checked tag").text

    for element in context_div.find_all('a',recursive=False):
        if element.get('href'):

            info_link= element.get('href')
            cover_link=element.find('img').get('src')
            name = element.find('p').find(class_='title',recursive =False).text
            rate = element.find('p').find(class_='rate',recursive =False).text
            m = Movie(name,rate,movie_location,movie_category,info_link,cover_link)
            movie_lists.append(m)

    return movie_lists


movies=getMovies('喜剧','美国')

#任务5: 构造电影信息数据表
'''
任务5: 构造电影信息数据表

从网页上选取你最爱的三个电影类型，然后获取每个地区的电影信息后，我们可以获得一个包含三个类型、所有地区，评分超过9分的完整电影对象的列表。将列表输出到文件 movies.csv
'''

types=['喜剧','动作','战争']
locations=['大陆','美国','香港','台湾','日本','韩国','英国','法国','德国','意大利','西班牙','印度','泰国','俄罗斯','伊朗','加拿大','澳大利亚','爱尔兰','瑞典','巴西','丹麦']
#3种类开的总列表
movies_list = list()
type_dics = {}
for type in types:
    types_total = int()
    for location in locations:
        tmp_list = list()
        # 每次主求回来的
        tmp_list = getMovies(type, location)
        # 全部地区的总列表
        movies_list = movies_list + tmp_list
        # 单独分类地区总列表
        type_dics[type, location] = len(tmp_list)
        # 这个分类的总列表
        types_total = types_total + len(tmp_list)
    # 分类地区下的总数量
    type_dics[type, 'total'] = types_total

#movies.csv文件名


with open('movies.csv','w',newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['影片名称','评分','地区','类型','信息连接','图片连接'])
    writer.writerows([m.name,m.rate,m.location,m.category,m.info_link,m.cover_link] for m in movies_list)
    # for movie in movies_list:
    #     writer.writerow([movie.name,movie.rate,movie.location,movie.category,movie.info_link,movie.cover_link])
    #     print(movie.name,movie.rate,movie.location,movie.category,movie.info_link,movie.cover_link)


# 任务6: 统计电影数据
'''
统计你所选取的每个电影类别中，数量排名前三的地区有哪些，分别占此类别电影总数的百分比为多少？
output.txt
'''
# 喜剧
comedy_dict = dict()
# 动作
action_dict = dict()
# 战争
war_dict = dict()
for key, value in type_dics.items():
    if key[0] == types[0]:
        comedy_dict[key[1]] = value
    elif key[0] == types[1]:
        # 动作
        action_dict[key[1]] = value
    elif key[0] == types[2]:
        # 战争
        war_dict[key[1]] = value

comedy_total = comedy_dict['total']
# 删除这个key
comedy_dict.pop('total')
# 按数量 倒序
comedy_dict_sorted = sorted(comedy_dict.items(), key=lambda e: e[1], reverse=True)

# 动作类总数量
action_total = action_dict['total']
# 删除
action_dict.pop('total')
# 排序
action_dict_sorted = sorted(action_dict.items(), key=lambda e: e[1], reverse=True)


# 战争这个类型的总数量
war_total = war_dict['total']
# 删除这个key
war_dict.pop('total')
# 排序
war_dict_sorted = sorted(war_dict.items(), key=lambda e: e[1], reverse=True)

with open('output.txt','w',encoding='utf-8') as f:
    try:
        f.write('喜剧前三地区:\n')
        for comedy in comedy_dict_sorted[:3]:
            f.write('{}  比例 {} '.format(comedy[0],'%.2f' %(int(comedy[1])/comedy_total*100)))

        f.write('\n动作前三地区:\n')
        for action in action_dict_sorted[:3]:
            f.write(' {} 比例 {} '.format(action[0],'%.2f' %(int(action[1])/action_total*100)))

        f.write('\n战争前三地区:\n')
        for war in war_dict_sorted[:3]:
            f.write( '{} 比例 {} '.format(war[0] ,'%.2f' % (int(war[1])/war_total*100)))

    except IOError as e:
        pass
