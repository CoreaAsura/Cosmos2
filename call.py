import streamlit as st
import requests

# Space-Track API URL
LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
TLE_URL = "https://www.space-track.org/basicspacedata/query/class/tle_latest"
SATCAT_SEARCH_URL = "https://www.space-track.org/basicspacedata/query/class/satcat/OBJECT_NAME"

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

def search_satellites_by_name(session, partial_name):
    url = f"{SATCAT_SEARCH_URL}/{partial_name}*/orderby/NORAD_CAT_ID/format/json"
    response = session.get(url)
    if response.status_code == 200:
        data = response.json()
        return [
            f"{item['OBJECT_NAME']} ({item['NORAD_CAT_ID']})"
            for item in data if "OBJECT_NAME" in item and "NORAD_CAT_ID" in item
        ]
    return []

def get_tle_by_norad(session, norad_id):
    url = f"{TLE_URL}/NORAD_CAT_ID/{norad_id}/ORDINAL/1/format/tle"
    response = session.get(url)
    if response.status_code != 200:
        return f"🚨 조회 오류: {response.status_code}"
    tle_text = response.text.strip()
    lines = tle_text.splitlines()
    if len(lines) >= 2:
        return f"{lines[0] if len(lines)==3 else f'NORAD {norad_id}'}\n{lines[-2]}\n{lines[-1]}"
    return "⚠️ TLE 형식 오류"

# --- Streamlit UI ---
st.title("🛰️ TLE 호출 for MSSB")

session = login_to_spacetrack()
if not session:
    st.error("🚨 Space-Track 로그인 실패. 인증 정보를 확인하세요.")
    st.stop()

partial_name = st.text_input("위성이름 일부 입력 (예: COSMOS, STARLINK 등)")
satellite_options = []

if partial_name.strip():
    satellite_options = search_satellites_by_name(session, partial_name.strip())

selected_sat = st.selectbox("관련 위성 선택", satellite_options) if satellite_options else None

if selected_sat and st.button("TLE 조회"):
    # NORAD ID 추출
    norad_id = selected_sat.split("(")[-1].replace(")", "").strip()
    tle_result = get_tle_by_norad(session, norad_id)
    if all(keyword not in tle_result for keyword in ["오류", "없음", "실패"]):
        st.session_state["tle_list"].append(tle_result)
        st.success(f"✅ '{selected_sat}' TLE 조회 성공")
    else:
        st.error(tle_result)

# 누적된 TLE 출력
if st.session_state["tle_list"]:
    st.subheader("📄 누적된 TLE 결과")
    combined_tle = "\n".join(st.session_state["tle_list"])
    st.code(combined_tle, language="text")
    st.info("※ 위 코드 블록 우측 상단의 복사 버튼을 눌러 전체 TLE를 복사하세요.")
