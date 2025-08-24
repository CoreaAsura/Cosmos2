import requests
import streamlit as st

# 🔑 Spacetrack 계정정보는 st.secrets에 저장
# .streamlit/secrets.toml 파일에 아래처럼 설정
# [spacetrack]
# username = "your_username"
# password = "your_password"

# ------------------------------------------------------
# 로그인 세션 획득
# ------------------------------------------------------
def get_session():
    login_url = "https://www.space-track.org/ajaxauth/login"
    data = {
        "identity": st.secrets["spacetrack"]["username"],
        "password": st.secrets["spacetrack"]["password"]
    }
    session = requests.Session()
    resp = session.post(login_url, data=data)
    if resp.status_code != 200:
        st.error("Space-Track 로그인 실패")
        return None
    return session

# ------------------------------------------------------
# TLE 조회 함수 (위성이름 또는 NORAD ID)
# ------------------------------------------------------
def get_latest_tle(query):
    session = get_session()
    if session is None:
        return None

    base_url = "https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1/"
    # 숫자인 경우 NORAD ID, 문자면 위성이름으로 조회
    if query.isdigit():
        url = f"{base_url}NORAD_CAT_ID/{query}/orderby/TLE_LINE1 asc/format/json"
    else:
        url = f"{base_url}OBJECT_NAME/{query}/orderby/TLE_LINE1 asc/format/json"

    resp = session.get(url)
    if resp.status_code != 200:
        st.error("TLE 조회 실패")
        return None
    
    tle_data = resp.json()
    if len(tle_data) == 0:
        return None

    # 최신 TLE 1개만 반환
    tle = tle_data[0]
    return tle["OBJECT_NAME"], tle["TLE_LINE1"], tle["TLE_LINE2"]

# ------------------------------------------------------
# Streamlit UI
# ------------------------------------------------------
st.title("TLE 조회 도구")

query = st.text_input("위성이름 또는 NORAD ID 입력")

if "tle_list" not in st.session_state:
    st.session_state["tle_list"] = []

if st.button("조회"):
    tle = get_latest_tle

