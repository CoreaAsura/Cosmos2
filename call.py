import streamlit as st
import requests

# Space-Track API URL
LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
TLE_URL = "https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1"

# --- Streamlit secrets 설정 ---
# st.secrets["spacetrack"]["username"]
# st.secrets["spacetrack"]["password"]

def get_tle(query):
    """
    Space-Track에서 위성이름 또는 NORAD ID로 최신 TLE 1세트 가져오기
    """
    session = requests.Session()

    # 로그인
    login_payload = {
        "identity": st.secrets["spacetrack"]["username"],
        "password": st.secrets["spacetrack"]["password"]
    }
    session.post(LOGIN_URL, data=login_payload)

    # 입력값이 숫자면 NORAD ID, 아니면 SATNAME 검색
    if query.isdigit():
        url = f"{TLE_URL}/NORAD_CAT_ID/{query}/orderby/epoch desc/format/tle"
    else:
        url = f"{TLE_URL}/OBJECT_NAME/{query}/orderby/epoch desc/format/tle"

    # 최신 TLE 1개 가져오기
    response = session.get(url)
    if response.status_code != 200:
        return f"조회 오류: {response.status_code}"

    tle_text = response.text.strip()
    if not tle_text:
        return "검색 결과 없음"

    # TLE는 보통 3줄 단위 (이름 + Line1 + Line2)
    lines = tle_text.splitlines()
    if len(lines) >= 2:
        satname = query
        line1 = lines[0]
        line2 = lines[1]
        return f"{satname}\n{line1}\n{line2}"
    else:
        return "TLE 데이터 형식 오류"


# --- Streamlit UI ---
st.title("Space-Track TLE 조회기")

query = st.text_input("위성이름 또는 NORAD ID 입력")

if st.button("TLE 조회"):
    tle_result = get_tle(query)
    if "오류" not in tle_result and "없음" not in tle_result:
        st.text_area("TLE 결과", tle_result, height=100)

        # 복사 버튼
        st.code(tle_result)
        st.download_button(
            label="TLE 복사/저장",
            data=tle_result,
            file_name=f"{query}_tle.txt",
            mime="text/plain"
        )
    else:
        st.error(tle_result)
