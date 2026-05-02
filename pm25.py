import pymysql
import pandas
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

url="https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=4c89a32a-a214-461b-bf29-30ff32a61a8a&limit=1000&sort=datacreationdate%20desc&format=JSON"

table_str="""
create table if not exists pm25(
id int auto_increment primary key,
site varchar(20),
county varchar(20),
pm25 int,
datacreationdate datetime,
itemunit varchar(20),
unique key site_time (site,datacreationdate)
)
"""

str_sql="""
insert ignore into pm25(site,county,pm25,datacreationdate,itemunit) values(%s,%s,%s,%s,%s)
"""

conn,cursor=None,None

def open_db():
    global conn,cursor
    try:
        conn=pymysql.connect(
            host=os.getenv("db_host"),
            password=os.getenv("db_password"),
            port=int(os.getenv("db_port",21697)),
            user=os.getenv("db_user"),
            database=os.getenv("db_database"),
        )
        cursor=conn.cursor()
        print("開啟資料庫成功!")
    except Exception as e:
        print(f"錯誤訊息:{e}")

def get_pm25_data():
    try:
        res=requests.get(url)
        datas=res.json()
        return datas
    except Exception as e:
        print(f"錯誤訊息:{e}")

def write_pm25_db():
    datas=get_pm25_data()
    data=[list(data.values()) for data in datas if list(data.values())[2]!=""]
    size=cursor.executemany(str_sql,data)
    conn.commit()
    print(f"寫入{size}筆資料...")
    return {"訊息":"寫入成功!","寫入比數":size}

def close_db():
    try:
        if conn is not None:
            conn.close()
            print("關閉資料庫~")
    except Exception as e:
        print(f"錯誤訊息:{e}")

def write_pm25_data_to_db():
    try:
        open_db()
        size=write_pm25_db()
        return size
    except Exception as e:
        print(f"錯誤訊息:{e}")
    finally:
        close_db()

def select_pm25_from_db():
    try:
        open_db()
        sql_str="""
        select site,county,pm25,datacreationdate,itemunit from pm25
        where datacreationdate=(select max(datacreationdate) from pm25)
        """
        cursor.execute(sql_str)
        datas=cursor.fetchall()

        # 取得最新時間
        sql_str="""
        select max(datacreationdate) from pm25
        """
        cursor.execute(sql_str)
        max_date=cursor.fetchone()[0].strftime("%Y-%m-%d %H:%M:%S")

        # 取得不重複縣市
        sql_str="""
        select county from pm25 group by county
        """
        cursor.execute(sql_str)
        countys=[county[0] for county in cursor.fetchall()]

        return datas,max_date,countys
    except Exception as e:
        print(f"錯誤訊息:{e}")
        return [], "無資料", []
    finally:
        close_db()


def get_pm25_avg_from_db():
    try:
        open_db()
        sql_str="""
        select county,round(avg(pm25),2) from pm25 group by county
        """
        cursor.execute(sql_str)
        datas=cursor.fetchall()
        return datas
    except Exception as e:
        print(f"錯誤訊息:{e}")
    finally:
        close_db()

def get_pm25_by_county(county):
    try:
        open_db()
        sql_str="""
        select site,pm25,datacreationdate from pm25
        where county=%s
        and datacreationdate=(select max(datacreationdate) from pm25)
        """
        cursor.execute(sql_str,(county,))
        datas=cursor.fetchall()
        return datas
    except Exception as e:
        print(f"錯誤訊息:{e}")
    finally:
        close_db()


        
    
if __name__=="__main__":
    open_db()
    cursor.execute(table_str)
    write_pm25_db()
    close_db()