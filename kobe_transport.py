from flask import Flask, render_template
import requests
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
import datetime
import pytz

def transport_pred(param):
    #モデル読み込み後引数を7次多項式に変換し、予測を返す
    reg = pickle.load(open('kobe_transport.pkl','rb'))
    poly_ap = PolynomialFeatures(degree = 7)
    param = poly_ap.fit_transform(param.reshape(-1,1))
    pred = reg.predict(param)
    return pred

#変数の初期設定
#time = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).date()
endtime = "0000-00-00"
#pred = []
#denger = []

#apiを叩く
# url = "https://weather.tsukumijima.net/api/forecast/city/280010"
# weather = requests.get(url)

# weather_json = weather.json()
# day = [weather_json["forecasts"][0]["date"], weather_json["forecasts"][1]["date"], weather_json["forecasts"][2]["date"]]
# weather = [weather_json["forecasts"][0]["telop"], weather_json["forecasts"][1]["telop"], weather_json["forecasts"][2]["telop"]]
# maxtemp = [weather_json["forecasts"][0]["temperature"]["max"]["celsius"], weather_json["forecasts"][1]["temperature"]["max"]["celsius"], weather_json["forecasts"][2]["temperature"]["max"]["celsius"]]

# for i in maxtemp:
#     if isinstance(i, str):
#         i = np.array(int(i))
#         pred.append(round(float(transport_pred(i)),3))
#     else:
#         i = "測定エラー"
#         pred.append(i)

# print(maxtemp[1])


# print(transport_pred(today_maxtemp))

app = Flask(__name__)

@app.route('/')
def transport():
    global endtime
    global day,maxtemp,weather,weather_img
    
    pred=[]
    denger=[]

    #アクセス時の日付を格納
    time = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).date()
    
    #timeがendtime(最後にapi取得した時)と異なる場合、apiを呼び出す
    if time != endtime:
        url = "https://weather.tsukumijima.net/api/forecast/city/280010"
        weather_api = requests.get(url)
        weather_json = weather_api.json()
        day = [weather_json["forecasts"][0]["date"], weather_json["forecasts"][1]["date"], weather_json["forecasts"][2]["date"]]
        weather = [weather_json["forecasts"][0]["telop"], weather_json["forecasts"][1]["telop"], weather_json["forecasts"][2]["telop"]]
        maxtemp = [weather_json["forecasts"][0]["temperature"]["max"]["celsius"], weather_json["forecasts"][1]["temperature"]["max"]["celsius"], weather_json["forecasts"][2]["temperature"]["max"]["celsius"]]
        weather_img = [weather_json["forecasts"][0]["image"]["url"], weather_json["forecasts"][1]["image"]["url"], weather_json["forecasts"][2]["image"]["url"]]
        print("api get")
        print(maxtemp)
        print(weather_img)

    #maxtempにNoneがあるとtypeエラーになるためifで分ける
    for i in maxtemp:
        if i is None:
            pred.append("測定エラー")
        else:
            i = np.array(int(i))
            pred.append(round(float(transport_pred(i)),3))
            print(pred)

    #predから危険度を振り分ける
    for i in pred:
        if i == '測定エラー':
            denger.append("測定エラー")
        elif i>= 20:
            denger.append("危険度：超危険！") 
        elif i >= 15:
            denger.append("危険度：高")
        elif i >= 5:
            denger.append("危険度：中")
        else:
            denger.append("危険度：小")
    print(pred,denger)
    
    #最後にapiを呼び出した日付を格納
    endtime = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).date()
    
    #endtime = endtime - datetime.timedelta(days=1)
    
    #HTMLに渡す変数を返す
    return render_template("index.html",
                           today_pred = pred[0], today_maxtemp = maxtemp[0],today = day[0], today_weather = weather[0], today_denger = denger[0], today_weather_img = weather_img[0],
                           tomorrow_pred = pred[1], tomorrow_maxtemp = maxtemp[1], tomorrow = day[1], tomorrow_weather = weather[1], tomorrow_denger = denger[1], tomorrow_weather_img = weather_img[1],
                           dat_pred = pred[2], dat_maxtemp = maxtemp[2], dat = day[2], dat_weather = weather[2], dat_denger = denger[2], dat_weather_img = weather_img[2])

if __name__ == '__main__':

    app.run(debug = True)
