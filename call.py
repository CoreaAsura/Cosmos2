import streamlit as st
import requests

# Space-Track API URL
LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
TLE_URL = "https://www.space-track.org/basicspacedata/query/class/tle_latest/ORDINAL/1"

# --- Streamlit secrets 설정 ---
# st.secrets["spacetrack"]["username"]
# st.secrets["spacetrack"]["password"]

# TLE 누적 저장용 세션 상태
if "tle_list" not in st.session_state:
    st.session_state["tle_list"] = []

def get_tle(query):
    """
    Space-Track에서 위성이름 또는 NORAD ID로 최신 TLE 1세트 가져오기
    (조회할 때마다 로그인)
    """
    session = requests.Session()

    # 로그인 요청
    login_payload = {
        "identity": st.secrets["spacetrack"]["username"],
        "password": st.secrets["spacetrack"]["password"]
    }
    login_response = session.post(LOGIN_URL, data=login_payload)
    if login_response.status_code != 200:
        return f"🚨 로그인 실패: {login_response.status_code}"

    # 위성 이름 또는 NORAD ID에 따라 URL 구성
    if query.isdigit():
        url = f"{TLE_URL}/NORAD_CAT_ID/{query}/orderby/epoch desc/format/tle"
    else:
        url = f"{TLE_URL}/OBJECT_NAME/{query}/orderby/epoch desc/format/tle"

    # TLE 데이터 요청
    response = session.get(url)
    if response.status_code != 200:
        return f"🚨 조회 오류: {response.status_code}"

    tle_text = response.text.strip()
    if not tle_text:
        return "🔍 검색 결과 없음"

    lines = tle_text.splitlines()
    if len(lines) >= 3:
        name = lines[0]
        line1 = lines[1]
        line2 = lines[2]
        return f"{name}\n{line1}\n{line2}"
    else:
        return "⚠️ TLE 데이터 형식 오류"

# --- Streamlit UI ---
st.title("🛰️ Space-Track TLE 조회기")

query = st.text_input("위성이름 또는 NORAD ID 입력")

if st.button("TLE 조회"):
    tle_result = get_tle(query)
    if "오류" not in tle_result and "없음" not in tle_result and "실패" not in tle_result:
        st.session_state["tle_list"].append(tle_result)
        st.success(f"✅ '{query}' TLE 조회 성공")
    else:
        st.error(tle_result)

# 누적된 TLE 출력
if st.session_state["tle_list"]:
    st.subheader("📄 누적된 TLE 결과")
    combined_tle = "\n".join(st.session_state["tle_list"])
    st.code(combined_tle, language="text")
    st.info("※ 위 코드 블록 우측 상단의 복사 버튼을 눌러 전체 TLE를 복사하세요.")
