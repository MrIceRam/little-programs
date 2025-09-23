import requests

def main(name):
    url = f"https://ddnet.org/players/?json2={name}"

    respons = requests.get(url)
    if respons.status_code == 200:
        JSdata = respons.json()
        xyun9 = JSdata.get("points", {}).get("points", None)
    return xyun9

name = str(input("Name "))
print(main(name))