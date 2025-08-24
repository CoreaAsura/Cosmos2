import streamlit as st
import requests

# Space-Track API URL
LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
TLE_URL = "https://www.space-track.org/basicspacedata/query/class/tle_latest"
SATCAT_URL = "https://www.space-track.org/basicspacedata/query/class/satcat"

# 세션 상태 초기화
if "tle_list" not in st.session_state:
    st.session_state["tle_list"] = []

def login_to_spacetrack():
    session = requests.Session()
    payload = {
        "identity": st.secrets["spacetrack"]["username"],
        "password": st.secrets["spacetrack"]["password"]
    }
    response = session.post(LOGIN_URL, data=payload)
    if response.status_code == 200 and session.cookies:
        return session
    return None

def get_satellite_name(session, norad_id):
    url = f"{SATCAT_URL}/NORAD_CAT_ID/{norad_id}/format/json"
    response = session.get(url)
    if response.status_code == 200:
        data = response.json()
        if data and "OBJECT_NAME" in data[0]:
            return data[0]["OBJECT_NAME"]
    return f"UNKNOWN-{norad_id}"

def get_tle(query):
    session = login_to_spacetrack()
    if not session:
        return "🚨 로그인 실패. 인증 정보를 확인하세요."

    # URL 구성
    if query.isdigit():
        url = f"{TLE_URL}/NORAD_CAT_ID/{query}/ORDINAL/1/format/tle"
    else:
        url = f"{TLE_URL}/OBJECT_NAME/{query}/ORDINAL/1/format/tle"

    response = session.get(url)
    if response.status_code != 200:
        return f"🚨 조회 오류: {response.status_code}"

    tle_text = response.text.strip()
    lines = tle_text.splitlines()

    # 위성이름 추출
    if len(lines) == 3:
        name_line = lines[0].strip()
    elif len(lines) == 2:
        # 위성이름이 누락된 경우, NORAD ID로 이름 조회
        norad_id = lines[0].split()[1] if lines else query
        name_line = get_satellite_name(session, norad_id)
    else:
        return "⚠️ TLE 형식 오류"

    return f"{name_line}\n{lines[-2]}\n{lines[-1]}"

# --- Streamlit UI ---
st.title("🛰️ Space-Track TLE 조회기")

query = st.text_input("위성이름 또는 NORAD ID 입력")

if st.button("TLE 조회"):
    tle_result = get_tle(query)
    if all(keyword not in tle_result for keyword in ["오류", "없음", "실패"]):
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
