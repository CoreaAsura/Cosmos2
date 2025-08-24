import requests

USERNAME = "your_username"
PASSWORD = "your_password"
NORAD_ID = "25544"

LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
TLE_URL = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{NORAD_ID}/orderby/epoch desc/limit/1/format/tle"

with requests.Session() as s:
    # 로그인
    resp = s.post(LOGIN_URL, data={"identity": USERNAME, "password": PASSWORD})
    resp.raise_for_status()

    # TLE 요청
    tle_resp = s.get(TLE_URL)
    tle_resp.raise_for_status()

    tle_data = tle_resp.text.strip()
    print(tle_data)
