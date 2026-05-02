import pymysql
import pandas
import requests
import json
from flask import Flask,render_template,Response
from pm25 import write_pm25_data_to_db,select_pm25_from_db,get_pm25_avg_from_db,get_pm25_by_county

app=Flask(__name__)

@app.route("/roger")
def roger():
    return "roger is very good~~~"

@app.route("/write-pm25-data")
def write_pm25_data():
    size=write_pm25_data_to_db()
    return json.dumps(size,ensure_ascii=False)

@app.route("/")
@app.route("/pm25")
def pm25():
    datas,max_date,countys=select_pm25_from_db()
    columns=["站點名稱","縣市","PM2.5","更新時間","單位"]
    return render_template("pm25.html",datas=datas,columns=columns,max_date=max_date,countys=countys)

@app.route("/avg-pm25")
def avg_pm25():
    datas=get_pm25_avg_from_db()
    countys=[county[0] for county in datas]
    avg_pm25=[float(avg_pm25[1]) for avg_pm25 in datas]
    return Response(
        json.dumps({"countys":countys,"avg_pm25":avg_pm25},ensure_ascii=False),
        mimetype="application/json",
    )

@app.route("/county-pm25/<county>")
def get_county_pm25(county):
    datas=get_pm25_by_county(county)

    if len(datas)==0:
        return Response(
            json.dumps({"result":"取得資料失敗","message":f"無此{county}縣市資料"},ensure_ascii=False),
            mimetype="application/json",
        )
    site=[site[0] for site in datas]
    pm25=[float(pm25[1]) for pm25 in datas]
    datetime=[site[2] for site in datas][0].strftime("%Y-%m-%d %H:%M:%S")
    return Response(
        json.dumps({"site":site,"pm25":pm25,"county":county,"datetime":datetime},ensure_ascii=False),
        mimetype="application/json",
    )

@app.route("/update_db")
def update_db():
    result=write_pm25_data_to_db()
    return json.dumps(result,ensure_ascii=False)







app.run(debug=True)