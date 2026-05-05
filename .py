import requests
import xml.etree.ElementTree as ET
import tkinter as tk
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Возможно с точки зрения безопасности пихать сюда токен плохая идея (все могут увидеть )
YANDEX_TOKEN = "" # В ковычках вставь свой токен яндекс диска 

CURRENCY = "EUR"

#курс евро по центробанку

url = "http://www.cbr.ru/scripts/XML_daily.asp"# api центробанка
response = requests.get(url)
root = ET.fromstring(response.content)

rate = None

for valute in root.findall("Valute"):
    if valute.find("CharCode").text == CURRENCY:
        value = float(valute.find("Value").text.replace(",", "."))
        nominal = int(valute.find("Nominal").text)
        rate = value / nominal

# конвертация в вечно деревянные

def convert():
    try:
        amount = float(entry_amount.get())
        rub = amount * rate
        label_result.config(text=f"{rub:.2f} RUB")
    except:
        label_result.config(text="Ошибка")

#история валют

def get_history(date_from, date_to):
    daily = requests.get("http://www.cbr.ru/scripts/XML_daily.asp")
    root = ET.fromstring(daily.content)

    valute_id = None
    for valute in root.findall("Valute"):
        if valute.find("CharCode").text == CURRENCY:
            valute_id = valute.attrib["ID"]
            break

    if not valute_id:
        return [], []

    url = f"http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={date_from}&date_req2={date_to}&VAL_NM_RQ={valute_id}"
    response = requests.get(url)
    root = ET.fromstring(response.content)

    dates = []
    values = []

    for rec in root.findall("Record"):
        date = rec.attrib["Date"]
        value = float(rec.find("Value").text.replace(",", "."))

        dates.append(date)
        values.append(value)

    return dates, values

#прогноз на графике

def predict(values, days=3):
    if len(values) < 2:
        return []

    diffs = [values[i] - values[i-1] for i in range(1, len(values))]
    avg = sum(diffs) / len(diffs)

    last = values[-1]
    forecast = []

    for _ in range(days):
        last += avg
        forecast.append(last)

    return forecast

# Загрузка в яндекс

def upload_to_yandex(local_file, remote_path):
    headers = {
        "Authorization": f"OAuth {YANDEX_TOKEN}"
    }

    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"

    params = {
        "path": remote_path,
        "overwrite": "true"
    }

    response = requests.get(url, headers=headers, params=params)
    upload_url = response.json().get("href")

    if not upload_url:
        print("Ошибка загрузки")
        return

    with open(local_file, "rb") as f:
        requests.put(upload_url, files={"file": f})

    print("Загружено в Яндекс.Диск")


# график

def show_graph():
    try:
        date_from = entry_date_from.get()
        date_to = entry_date_to.get()

        dates, values = get_history(date_from, date_to)

        if not dates:
            label_result.config(text="Нет данных")
            return

        dates_dt = [datetime.strptime(d, "%d.%m.%Y") for d in dates]

        forecast = predict(values, 3)
        last_date = dates_dt[-1]
        future_dates = [last_date + timedelta(days=i+1) for i in range(len(forecast))]

        plt.figure()
        plt.plot(dates_dt, values, label="История")
        plt.plot(future_dates, forecast, linestyle="--", label="Прогноз")

        plt.title("Курс EUR к RUB")
        plt.xlabel("Дата")
        plt.ylabel("Рубли")

        plt.legend()
        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()

        # сохраняем файл
        plt.savefig("graph.png")

        # пихаем в облако
        remote_path = f"graph_{datetime.now().strftime('%Y%m%d')}.png"
        upload_to_yandex("graph.png", remote_path)

        plt.show()

    except:
        label_result.config(text="Ошибка")


#Приложуха

root = tk.Tk()
root.title("Анализ EUR 💶")
root.geometry("320x320")

tk.Label(root, text="Сумма в EUR:").pack()
entry_amount = tk.Entry(root)
entry_amount.pack()

tk.Button(root, text="Перевести в RUB", command=convert).pack(pady=5)

label_result = tk.Label(root, text="")
label_result.pack()

tk.Label(root, text="Дата ОТ (дд/мм/гггг):").pack()
entry_date_from = tk.Entry(root)
entry_date_from.pack()

tk.Label(root, text="Дата ДО (дд/мм/гггг):").pack()
entry_date_to = tk.Entry(root)
entry_date_to.pack()

tk.Button(root, text="Построить график + загрузить", command=show_graph).pack(pady=10)

root.mainloop()
