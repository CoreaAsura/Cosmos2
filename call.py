import streamlit as st
import requests

# 제목
st.title("Space-Track TLE 조회 도구")

# 사용자 입력
user_input = st.text_input("위성이름 또는 NORAD ID를 입력하세요:")

# TLE 결과 저장용 세션 상태
if "tle_results" not in st.session_state:
    st.session_state.tle_results = ""

# 버튼 클릭 시 동작
if st.button("TLE 조회"):
    if user_input:
        # st.secrets에서 계정정보 불러오기
        username = st.secrets["spacetrack"]["username"]
        password = st.secrets["spacetrack"]["password"]

        # 세션 생성
        session = requests.Session()
        login_url = "https://www.space-track.org/ajaxauth/login"
        login_data = {"identity": username, "password": password}
        resp = session.post(login_url, data=login_data)

        if resp.status_code == 200:
            # 입력값이 숫자면 NORAD ID 검색
            if user_input.isdigit():
                query_url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{user_input}/orderby/ORDINAL asc/format/tle"
            else:  # 문자열이면 OBJECT_NAME 검색
                query_url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/OBJECT_NAME/{user_input}/orderby/ORDINAL asc/format/tle"

            tle_resp = session.get(query_url)

            if tle_resp.status_code == 200 and tle_resp.text.strip():
                tle_text = tle_resp.text.strip()
                # 결과를 세션 상태에 누적 (줄간격 추가하지 않음)
                st.session_state.tle_results += tle_text + "\n"
            else:
                st.error("TLE을 찾을 수 없습니다. 입력값을 확인하세요.")
        else:
            st.error("Space-Track 로그인 실패. 계정 정보를 확인하세요.")

# 결과 출력
if st.session_state.tle_results:
    st.text_area("누적된 TLE", st.session_state.tle_results, height=300)

    # 클립보드 복사 버튼 (JS 활용)
    st.markdown(
        """
        <button onclick="navigator.clipboard.writeText(document.getElementById('tle_area').value)">
            📋 클립보드로 복사
        </button>
        <script>
        document.getElementById('tle_area').id = 'tle_area';
        </script>
        """,
        unsafe_allow_html=True
    )
