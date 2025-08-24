import streamlit as st
import requests
import urllib.parse
import time

st.title("🛰️ TLE 호출 for MSSB")

# 세션 초기화
if "tle_list" not in st.session_state:
    st.session_state["tle_list"] = []

# 입력
sat_name = st.text_input("🛰️ 위성명칭 (예: STARLINK-32502)", key="name_input")
norad_id = st.text_input("🔢 NORAD ID (예: 62116)", key="id_input")

# TLE 호출 함수 (URL 인코딩 + 재시도 추가)
def fetch_tle(query, mode="name", retries=2, delay=2):
    base_url = "https://celestrak.org/NORAD/elements/gp.php"
    param = "NAME" if mode == "name" else "CATNR"
    encoded_query = urllib.parse.quote(query)
    url = f"{base_url}?{param}={encoded_query}&FORMAT=tle"

    for attempt in range(retries + 1):
        try:
            r = requests.get(url, timeout=10)
            lines = r.text.strip().splitlines()

            # 디버깅 출력 (Streamlit UI에도 표시)
            st.write(f"📡 [디버깅] 시도 {attempt+1}/{retries+1}, 상태코드:", r.status_code)
            if attempt == retries:
                st.text_area("📡 [디버깅] 최종 응답", r.text, height=150)

            if len(lines) >= 3:
                return f"{lines[0]}\n{lines[1]}\n{lines[2]}"
        except Exception as e:
            st.error(f"❌ [디버깅] 예외 발생 (시도 {attempt+1}/{retries+1}): {e}")

        # 실패 시 대기 후 재시도
        if attempt < retries:
            time.sleep(delay)

    return None

# 호출 버튼
if st.button("📡 TLE 호출"):
    query, tle = "", None

    if sat_name.strip():
        query = sat_name.strip()
        tle = fetch_tle(query, mode="name")
    elif norad_id.strip():
        query = norad_id.strip()
        tle = fetch_tle(query, mode="id")

    if not query:
        st.warning("위성명칭 또는 NORAD ID 중 하나를 입력해주세요.")
    elif tle:
        st.session_state["tle_list"].append(tle)
        st.success(f"✅ '{query}'에 대한 TLE 호출 성공!")
    else:
        st.error(f"❌ '{query}'에 대한 TLE 데이터를 찾을 수 없습니다.")