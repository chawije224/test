import requests
import json

async def getKeyss(pssh, license):
    api_url = "https://getwvkeys.cc/api"
    license_url = license
    PSSH = pssh
    headers = {
        'user_agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'content-type': 'application/json',
        "X-API-Key": '29fde7fec5cb2c4564a8658686f3cabe1cacadd5dbaafb14fd333c33716529ac',
    }
    payload = {
        "license_url": license_url,
        "pssh": PSSH,
    }
    r = requests.post(api_url, headers=headers, json=payload)
    # keyID, key = r.split(':')[3].split('"')[-1], r.split(':')[4].split('"')[0]
    try:
        keyID_key = r.json()['keys'][0]['key']
        # keyStr = "--key  {}".format(keyID_key)
        return keyID_key
    except:
        # message.reply('<b>Not Supported</b>')
        return None
