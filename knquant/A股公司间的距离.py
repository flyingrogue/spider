# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import pymysql
import requests
import json
from urllib.parse import urlencode
from math import radians, cos, sin, asin, sqrt

MYSQL_HOST='192.168.1.208'
MYSQL_USER='quant'
MYSQL_PASSWORD='knquant@99'
MYSQL_DB1='wind'
MYSQL_DB2='test'
MYSQL_PORT=3306
HOLDSHARE='ASHARECOMPANYHOLDSHARES_18up'
SALE='ASHARESALESSEGMENT_18up'

class Distance():
    def __init__(self,host=MYSQL_HOST,user=MYSQL_USER,password=MYSQL_PASSWORD,
                 db1=MYSQL_DB1,db2=MYSQL_DB2,port=MYSQL_PORT):
        self.db1=pymysql.connect(host,user,password,database=db1,port=port)
        self.db2 = pymysql.connect(host, user, password, database=db2, port=port)
        self.cursor1=self.db1.cursor()
        self.cursor2=self.db2.cursor()
        self.cursor3=self.db2.cursor()

    def __del__(self):
        self.db1.close()
        self.db2.close()

    #接入百度地图获取地址的经纬度
    def getlnglat(self,address):
        base_url = 'http://api.map.baidu.com/geocoder/v2/?'
        ak = '2U9UhaUBPVE8cuM3wAgvhMO6G9WjVpHR'
        params = {
            'address': address,
            'output': 'json',
            'ak': ak
        }
        url = base_url + urlencode(params)
        res = requests.get(url)
        temp = json.loads(res.text)
        return temp

    #根据经纬度计算两地间的距离
    def geodistance(self,lng1,lat1,lng2,lat2):
        lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
        dlon = lng2 - lng1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        dis = 2 * asin(sqrt(a)) * 6371 * 1000
        return dis


    def main(self):
        sql1 = 'select S_INFO_COMPCODE from ASHAREDESCRIPTION where S_INFO_WINDCODE like "{}.%"'
        sql2 = 'select CITY,LONGITUDE,LATITUDE from COMPINTRODUCTION where COMP_ID="{}"'
        sql3 = 'select CITY,LONGITUDE,LATITUDE,S_CAPITALOPERATION_PCT,VOTING_RIGHTS,S_CAPITALOPERATION_AMOUNT,S_CAPITALOPERATION_COREGCAP' \
               ' from {HOLDSHARE} where S_INFO_WINDCODE like "{code}.%" and ADDRESS is not null and ANN_DT regexp "^2018" and' \
               '(S_CAPITALOPERATION_AMOUNT>=1000 or S_CAPITALOPERATION_COREGCAP>=1000) and (S_CAPITALOPERATION_PCT>=50 or VOTING_RIGHTS>=50)'.format(HOLDSHARE=HOLDSHARE)
        sql4 = 'SELECT S_SEGMENT_ITEM,PCT_SEGMENT_SALES FROM {SALE} where S_INFO_WINDCODE like "{code}.%"' \
               ' and REPORT_PERIOD regexp "^2018" and PCT_SEGMENT_SALES>10 and S_SEGMENT_ITEM regexp ' \
               '"石家庄|保定|秦皇岛|唐山|邯郸|邢台|沧州|承德|廊坊|衡水|张家口|太原|大同|阳泉|长治|临汾|晋中|运城|晋城|忻州|朔州|吕梁|' \
               '呼和浩特|呼伦贝尔|包头|赤峰|乌海|通辽|鄂尔多斯|乌兰察布|巴彦淖尔|大连|盘锦|鞍山|抚顺|本溪|铁岭|锦州|丹东|沈阳|葫芦岛|阜新|' \
               '朝阳|辽阳|营口|长春|通化|白城|四平|辽源|松原|白山|伊春|牡丹江|哈尔滨|大庆|鸡西|鹤岗|绥化|双鸭山|七台河|佳木斯|黑河|齐齐哈尔|无锡|' \
               '常州|南京|扬州|徐州|苏州|连云港|盐城|淮安|宿迁|镇江|南通|泰州|杭州|宁波|绍兴|温州|湖州|嘉兴|台州|金华|舟山|衢州|丽水|合肥|芜湖|亳州|' \
               '马鞍山|池州|淮南|淮北|蚌埠|巢湖|安庆|宿州|宣城|滁州|黄山|六安|阜阳|铜陵|福州|厦门|泉州|漳州|南平|三明|龙岩|莆田|宁德|南昌|' \
               '赣州|景德镇|九江|萍乡|新余|抚州|宜春|上饶|鹰潭|吉安|济南|青岛|潍坊|淄博|威海|枣庄|泰安|临沂|东营|济宁|烟台|菏泽|日照|德州|聊城|' \
               '滨州|莱芜|郑州|洛阳|焦作|商丘|信阳|新乡|安阳|开封|漯河|南阳|鹤壁|平顶山|濮阳|许昌|周口|三门峡|驻马店|武汉|荆门|咸宁|襄樊|' \
               '荆州|黄石|宜昌|随州|鄂州|孝感|黄冈|十堰|长沙|郴州|娄底|衡阳|株洲|湘潭|岳阳|常德|邵阳|益阳|永州|张家界|怀化|广州|深圳|江门|佛山|' \
               '汕头|湛江|韶关|中山|珠海|茂名|肇庆|阳江|惠州|梅州|潮州|揭阳|清远|河源|东莞|汕尾|云浮|南宁|贺州|柳州|桂林|梧州|北海|玉林|' \
               '钦州|百色|防城港|贵港|河池|崇左|来宾|海口|三亚|成都|乐山|雅安|广安|南充|自贡|泸州|内江|宜宾|广元|达州|资阳|绵阳|眉山|巴中|' \
               '攀枝花|遂宁|德阳|贵阳|安顺|遵义|六盘水|昆明|玉溪|大理|曲靖|普洱|昭通|保山|丽江|临沧|拉萨|西安|咸阳|榆林|宝鸡|铜川|渭南|汉中|' \
               '安康|商洛|延安|兰州|白银|武威|金昌|平凉|张掖|嘉峪关|酒泉|庆阳|定西|陇南|天水|西宁|银川|乌鲁木齐|固原|克拉玛依|' \
               '北京|天津|上海|重庆|河北|山西|内蒙古|辽宁|吉林|黑龙江|江苏|浙江|安徽|福建|江西|山东|河南|湖北|湖南|广东|广西|海南|四川|贵州|云南|西藏|陕西|甘肃|青海|宁夏|新疆"'.format(SALE=SALE)

        province={'河北':'石家庄市','山西':'太原市','内蒙古':'呼和浩特市','辽宁':'沈阳市','吉林':'长春市','黑龙江':'哈尔滨市','江苏':'南京市',
                  '浙江':'杭州市','安徽':'合肥市','福建':'福州市','江西':'南昌市','山东':'济南市','河南':'郑州市','湖北':'武汉市','湖南':'长沙市',
                  '广东':'广州市','广西':'南宁市','海南':'海口市','四川':'成都市','贵州':'贵阳市','云南':'昆明市','西藏':'拉萨市','陕西':'西安市',
                  '甘肃':'兰州市','青海':'西宁市','宁夏':'银川市','新疆':'乌鲁木齐市'}
        codes = []
        postion = []
        index=[]
        count1 = 0
        count2=0
        count3=0
        ticker = np.load('/shared/FactorBank/ticker_names.npy')
        for i in range(len(ticker)):
            codes.append(ticker[i].decode('utf-8'))
        for code in codes:
            self.cursor1.execute(sql1.format(code))
            compid = self.cursor1.fetchone()[0]
            if compid:
                #从wind中获取上市公司的注册城市及其经纬度
                self.cursor2.execute(sql2.format(compid))
                temp = self.cursor2.fetchone()
                if temp:
                    city = temp[0]
                    lnglat = (temp[1], temp[2])
                    #从wind中获取上市公司的子公司信息
                    self.cursor2.execute(sql3.format(code=code))
                    results = self.cursor2.fetchall()
                    #如果wind中有含地址的子公司信息，则根据子公司注册资本和持股比例计算出各地的权重
                    if results:
                        allcity = {}
                        for result in results:
                            #注册资本没有就用投资金额，持股比例没有就用投票权
                            if result[3]:
                                if result[6]:
                                    capital = result[3] / 100 * result[6]
                                else:
                                    capital = result[3] / 100 * result[5]
                            elif result[6]:
                                capital = result[4] / 100 * result[6]
                            else:
                                capital = result[4] / 100 * result[5]

                            if result[0] in allcity:
                                allcity[result[0]] += capital
                            else:
                                allcity[result[0]] = capital
                        sum=0
                        for i in allcity.values():
                            sum+=i
                        for key,value in allcity.items():
                            wgt=round(value/sum*100,2)
                            #将子公司所属上市公司的代码及权重组成的元组放入索引列表
                            index.append((code,float(wgt)))
                            #print(code,'此公司在',key,'占比',wgt)
                            for result in results:
                                if result[0]==key:
                                    #将子公司的经纬度及权重放入位置列表
                                    postion.append((result[1],result[2],float(wgt)))
                                    break
                        if city not in allcity.keys():
                            print(code,'此公司注册地无子公司',city,allcity)
                            count1+=1
                    #如果wind中没有含地址的子公司信息，则根据wind的分地区(只选取细分到省或市的)主营业务表得到各地的权重
                    else:
                        self.cursor3.execute(sql4.format(code=code))
                        areas=self.cursor3.fetchall()
                        if areas:
                            #此字典键为城市，值为权重
                            cities={}
                            #如果地区是省份则用省会城市代替
                            for area in areas:
                                if area[0] in province.keys():
                                    if province[area[0]] not in cities.keys():
                                        cities[province[area[0]]]=float(area[1])
                                else:
                                    cities[area[0]+'市']=float(area[1])
                            sum1=0
                            for i in cities.values():
                                sum1+=i
                            #判断是否包含注册城市，不足100%的部分权重就赋予注册城市
                            if city in cities.keys():
                                cities[city]=float(round((100-(sum1-cities[city])),2))
                            else:
                                print(code, '此公司注册地址无业务', city, cities)
                                count3+=1
                                cities[city]=float(round((100-sum1),2))
                            #将各地区的经纬度及权重放入位置列表，公司代码及权重放入索引列表
                            for c,w in cities.items():
                                #print(code,'此公司主业务在',c,'占比',w)
                                res=self.getlnglat(c)
                                if res['status']==0:
                                    lng=res['result']['location']['lng']
                                    lat=res['result']['location']['lat']
                                    postion.append((lng,lat,w))
                                    index.append((code, w))

                        #若分地区主营业务表也无有效信息，则直接用注册城市，权重为100%
                        else:
                            index.append((code,float(100)))
                            postion.append((lnglat[0],lnglat[1],float(100)))
                            #print(code, '此公司无子公司地址及主营业务信息使用注册地址', city)
                            count2+=1
                else:
                    index.append((code,0))
                    postion.append(None)
                    print(code, '无此公司信息')
            else:
                index.append((code,0))
                postion.append(None)
                print(code, '无comid')

        print(len(index),count1,count2,count3)

        #计算各地间的距离，构成一个二维列表
        data = []
        for i in postion:
            dises = []
            for j in postion:
                if i and j:
                    dis = self.geodistance(i[0], i[1], j[0], j[1])
                    dises.append(dis)
                else:
                    dises.append(0)
            data.append(dises)

        np.save('/home/jbliu/projects/distance_2018上.npy',np.array(data))
        np.save('/home/jbliu/projects/postion_2018上.npy',np.array(postion))
        #将索引列表中的元组定义为自定义数组类型，这样才可将索引列表转换为一维数组
        t=np.dtype([('code',np.str,20),('wgt',np.float)])
        np.save('/home/jbliu/projects/index_2018上.npy',np.array(index,dtype=t))

        # index=np.load('/home/jbliu/projects/index.npy').tolist()
        # pos=np.load('/home/jbliu/projects/postion.npy')
        # dis=np.load('/home/jbliu/projects/distance.npy')
        # df_dis = pd.DataFrame(dis, index=pd.MultiIndex.from_tuples(index), columns=pd.MultiIndex.from_tuples(index))
        # df_pos=pd.DataFrame(pos,index=pd.MultiIndex.from_tuples(index),columns=['lng','lat','wgt'])



if __name__=='__main__':
    distance=Distance()
    distance.main()


'''
先准备三张表，一张上市公司注册信息表（test.COMPINTRODUCTION）；一张子公司信息表（test.ASHARECOMPANYHOLDSHARES这张表是从wind.ASHARECOMPANYHOLDSHARES中选取每个子公司最新一条记录，sql语句如下：
"insert into test.ASHARECOMPANYHOLDSHARES (OBJECT_ID,S_INFO_WINDCODE,ANN_DT,ENDDATE,S_CAPITALOPERATION_COMPANYNAME,S_CAPITALOPERATION_PCT,VOTING_RIGHTS,S_CAPITALOPERATION_AMOUNT,S_CAPITALOPERATION_COREGCAP,OPDATE) 
select OBJECT_ID,S_INFO_WINDCODE,ANN_DT,ENDDATE,S_CAPITALOPERATION_COMPANYNAME,S_CAPITALOPERATION_PCT,VOTING_RIGHTS,S_CAPITALOPERATION_AMOUNT,S_CAPITALOPERATION_COREGCAP,OPDATE
from (select * from wind.ASHARECOMPANYHOLDSHARES where is_consolidate=1 and relations_code<>3 and relations_code<>6 and relations_code<>8 and relations_code<>10 order by OPDATE desc) as b group by S_CAPITALOPERATION_COMPANYNAME;",

test.ASHARECOMPANYHOLDSHARES18_up这张表是选取ANN_DT具有18年信息的子公司的记录，asc取的是上半年，desc取的是下半年，sql语句如下：
"insert into test.ASHARECOMPANYHOLDSHARES_18up (OBJECT_ID,S_INFO_WINDCODE,ANN_DT,ENDDATE,S_CAPITALOPERATION_COMPANYNAME,S_CAPITALOPERATION_PCT,VOTING_RIGHTS,S_CAPITALOPERATION_AMOUNT,S_CAPITALOPERATION_COREGCAP,OPDATE)
select OBJECT_ID,S_INFO_WINDCODE,ANN_DT,ENDDATE,S_CAPITALOPERATION_COMPANYNAME,S_CAPITALOPERATION_PCT,VOTING_RIGHTS,S_CAPITALOPERATION_AMOUNT,S_CAPITALOPERATION_COREGCAP,OPDATE from  
(select * from wind.ASHARECOMPANYHOLDSHARES where ANN_DT regexp '^2018' and is_consolidate=1 and relations_code<>3 and relations_code<>6 and relations_code<>8 and relations_code<>10 order by OPDATE asc) as b group by S_CAPITALOPERATION_COMPANYNAME;",

向子公司信息表插入地址，sql语句如下:
update test.ASHARECOMPANYHOLDSHARES_18down,test.ASHARECOMPANYHOLDSHARES set test.ASHARECOMPANYHOLDSHARES_18down.PROVINCE=test.ASHARECOMPANYHOLDSHARES.PROVINCE,test.ASHARECOMPANYHOLDSHARES_18down.CITY=test.ASHARECOMPANYHOLDSHARES.CITY,
test.ASHARECOMPANYHOLDSHARES_18down.ADDRESS=test.ASHARECOMPANYHOLDSHARES.ADDRESS,test.ASHARECOMPANYHOLDSHARES_18down.LONGITUDE=test.ASHARECOMPANYHOLDSHARES.LONGITUDE,test.ASHARECOMPANYHOLDSHARES_18down.LATITUDE=test.ASHARECOMPANYHOLDSHARES.LATITUDE
where test.ASHARECOMPANYHOLDSHARES_18down.S_CAPITALOPERATION_COMPANYNAME=test.ASHARECOMPANYHOLDSHARES.S_CAPITALOPERATION_COMPANYNAME;）


一张分地区主营业务表（test.ASHARESALESSEGMENT这张表是从wind.ASHARESALESSEGMENT选取所有上市公司分地区的信息，test.ASHARESALESSEGMENT1这张表则是筛选出18年的记录，sql语句如下：
"insert into test.ASHARESALESSEGMENT_18up (OBJECT_ID,S_INFO_WINDCODE,REPORT_PERIOD,S_SEGMENT_ITEM,S_SEGMENT_SALES,S_SEGMENT_PROFIT,S_SEGMENT_COST,PCT_SEGMENT_SALES,PCT_SEGMENT_PROFIT,PCT_SEGMENT_COST,OPDATE) 
select OBJECT_ID,S_INFO_WINDCODE,REPORT_PERIOD,S_SEGMENT_ITEM,S_SEGMENT_SALES,S_SEGMENT_PROFIT,S_SEGMENT_COST,PCT_SEGMENT_SALES,PCT_SEGMENT_PROFIT,PCT_SEGMENT_COST,OPDATE 
FROM wind.ASHARESALESSEGMENT where S_SEGMENT_ITEMCODE = '455002000' and REPORT_PERIOD regexp '^2018';",更改regexp规则可选取不同年份，一般每年6月一条记录，12月一条）；

遍历A股代码，从test.ASHARECOMPANYHOLDSHARES中选出对应上市公司的符合条件（有地址、持股信息等）的子公司,按城市分组，计算各组权重（依据持股比例、投票权、投资金额、注册资本等计算，计算方式有待商榷），
然后将各组的经纬度及权重组成的元组放入位置列表，将该上市公司的代码及各组的权重组成的元组放入索引列表；
如果没有符合条件的子公司则从test.ASHARESALESSEGMENT中选出符合条件（按省或城市划分的）的分地区主营业务信息，同样按城市分组（省份就用省会代替），计算各组权重（依据主营业务占比），
然后进行上述同样的操作，
若无符合条件的子公司和主营业务信息则直接用上市公司的注册地址，权重为100%，同样将相关元组放入列表；
根据位置列表计算出各地之间的距离，形成二维列表。
'''