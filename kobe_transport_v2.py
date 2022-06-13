from flask import Flask, render_template
import requests
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
import datetime
import pytz

def transport_pred(param,param2):
    #モデル読み込み後引数を7次多項式に変換し、予測を返す
    reg = pickle.load(open('kobe_transport_v3.pkl','rb'))
    poly_ap = PolynomialFeatures(degree = 7)
    param2 = np.array(param2)
    param2 = param2.reshape(-1,1)
    param = poly_ap.fit_transform(param.reshape(-1,1))
    param = np.append(param,param2,axis=1)
    pred = reg.predict(param)
    return pred

endtime = "0000-00-00"

app = Flask(__name__)

@app.route('/')
def transport():
    global endtime
    global day,maxtemp,weather,weather_img,headsup
    
    pred = []
    denger = []
    rain_d = []

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
        
    for i in weather:
        if "雨" in i:
            rain_d.append(1)
        else:
            rain_d.append(0)
        print(i)

    print(rain_d)
    print(weather)

    #maxtempにNoneがあるとtypeエラーになるためifで分ける
    for i in range(3):
        if maxtemp[i] is None:
            pred.append("測定エラー")
        else:
            maxtemp[i] = np.array(int(maxtemp[i]))
            pred.append(round(float(transport_pred(maxtemp[i],rain_d[i])),1))
            print(pred)

    #predから危険度を振り分ける
    for i in pred:
        if i == '測定エラー':
            denger.append("測定エラー")
        elif i>= 20:
            denger.append("危険度：超危険！") 
        elif i >= 15:
            denger.append("危険度：大")
        elif i >= 5:
            denger.append("危険度：中")
        else:
            denger.append("危険度：小")
    print(pred,denger)
    
    #当日の危険度に応じた注意喚起画像を表示する
    if denger[0] == "危険度：超危険":
        headsup = "/static/css/image/denger_ex.png"
    elif denger[0] == "危険度：大":
        headsup = "/static/css/image/denger_L.png"
    elif denger[0] == "危険度：中":
        headsup = "/static/css/image/denger_m.png"
    elif denger[0] == "危険度：小":
        headsup = "/static/css/image/denger_small.png"
    else:
        headsup = '/static/css/image/error.png'
    
    #最後にapiを呼び出した日付を格納
    endtime = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).date()
    
    #endtime = endtime - datetime.timedelta(days=1)
    
    #HTMLに渡す変数を返す
    return render_template("table.html",
                           today_pred = pred[0], today_maxtemp = maxtemp[0],today = day[0], today_weather = weather[0], today_denger = denger[0], today_weather_img = weather_img[0],
                           tomorrow_pred = pred[1], tomorrow_maxtemp = maxtemp[1], tomorrow = day[1], tomorrow_weather = weather[1], tomorrow_denger = denger[1], tomorrow_weather_img = weather_img[1],
                           dat_pred = pred[2], dat_maxtemp = maxtemp[2], dat = day[2], dat_weather = weather[2], dat_denger = denger[2], dat_weather_img = weather_img[2],
                           headsup=headsup)

if __name__ == '__main__':

    app.run(debug=True)
