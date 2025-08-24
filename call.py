import streamlit as st
import requests

# Space-Track API URL
LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
TLE_BASE_URL = "https://www.space-track.org/basicspacedata/query/class/tle_latest"

# 세션 상태 초기화
if "tle_list" not in st.session_state:
    st.session_state["tle_list"] = []

def get_tle(query):
    """
    Space-Track에서 위성이름 또는 NORAD ID로 최신 TLE 1세트 가져오기
    첫 줄은 위성 이름으로 표시
    """
    session = requests.Session()

    # 로그인
    login_payload = {
        "identity": st.secrets["spacetrack"]["username"],
        "password": st.secrets["spacetrack"]["password"]
    }
    login_response = session.post(LOGIN_URL, data=login_payload)

    if login_response.status_code != 200 or not session.cookies:
        return f"🚨 로그인 실패 또는 인증 쿠키 누락: {login_response.status_code}"

    # URL 구성
    if query.isdigit():
        url = f"{TLE_BASE_URL}/NORAD_CAT_ID/{query}/ORDINAL/1/format/tle"
    else:
        url = f"{TLE_BASE_URL}/OBJECT_NAME/{query}/ORDINAL/1/format/tle"

    response = session.get(url)
    if response.status_code != 200:
        return f"🚨 조회 오류: {response.status_code}"

    tle_text = response.text.strip()
    if not tle_text:
        return "🔍 검색 결과 없음"

    lines = tle_text.splitlines()
    if len(lines) == 3:
        # 첫 줄이 NORAD ID일 경우 위성 이름으로 대체
        return f"{query}\n{lines[1]}\n{lines[2]}"
    elif len(lines) == 2:
        return f"{query}\n{lines[0]}\n{lines[1]}"
    else:
        return "⚠️ TLE 데이터 형식 오류"

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
