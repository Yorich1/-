import requests
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk


url = "http://www.cbr.ru/scripts/XML_daily.asp" # центробанк
response = requests.get(url)

root = ET.fromstring(response.content)

rates = {"RUB": 1.0}
currency_names = {"RUB": "Российский рубль"}


for valute in root.findall("Valute"):
    char_code = valute.find("CharCode").text
    name = valute.find("Name").text
    value = valute.find("Value").text.replace(",", ".")
    nominal = int(valute.find("Nominal").text)

    rates[char_code] = float(value) / nominal
    currency_names[char_code] = name


display_currencies = [
    f"{code} ({currency_names[code]})"
    for code in rates.keys()
]

# конвертация
def convert():
    try:
        amount = float(entry_amount.get())

        from_currency = combo_from.get().split(" ")[0]
        to_currency = combo_to.get().split(" ")[0]

        rub = amount * rates[from_currency]
        result = rub / rates[to_currency]

        label_result.config(text=f"{result:.2f} {to_currency}")
    except:
        label_result.config(text="Ошибка")

# приложуха
root = tk.Tk()
root.title("Конвертер валют 💱")
root.geometry("320x220")

tk.Label(root, text="Сумма:").pack()
entry_amount = tk.Entry(root)
entry_amount.pack()

tk.Label(root, text="Из:").pack()
combo_from = ttk.Combobox(root, values=display_currencies)
combo_from.pack()
combo_from.current(0)

tk.Label(root, text="В:").pack()
combo_to = ttk.Combobox(root, values=display_currencies)
combo_to.pack()
combo_to.current(1)

tk.Button(root, text="Конвертировать", command=convert).pack(pady=10)

label_result = tk.Label(root, text="")
label_result.pack()

root.mainloop()
