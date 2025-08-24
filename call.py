import streamlit as st
import requests
import urllib.parse
import time

st.title("🛰️ TLE 호출 for MSSB")

if "tle_list" not in st.session_state:
    st.session_state["tle_list"] = []

sat_name = st.text_input("🛰️ 위성명칭 (예: STARLINK-32502)", key="name_input")
norad_id = st.text_input("🔢 NORAD ID (예: 62116)", key="id_input")

def fetch_tle(query, mode="name"):
    urls = [
        "https://celestrak.org/NORAD/elements/gp.php",
        "https://celestrak.net/NORAD/elements/gp.php",
    ]
    param = "NAME" if mode == "name" else "CATNR"
    encoded_query = urllib.parse.quote(query)
    headers = {"User-Agent": "Mozilla/5.0 (TLEFetcher/1.0)"}

    # 1. API 우선 시도
    for base_url in urls:
        for attempt in range(5):  # 5회까지 재시도
            url = f"{base_url}?{param}={encoded_query}&FORMAT=tle"
            try:
                r = requests.get(url, headers=headers, timeout=(10, 30))
                lines = r.text.strip().splitlines()
                if len(lines) >= 3:
                    return f"{lines[0]}\n{lines[1]}\n{lines[2]}"
            except Exception as e:
                st.warning(f"⚠️ {base_url} 연결 실패 (시도 {attempt+1}/5): {e}")
                time.sleep(2 * (attempt + 1))  # 지수 백오프

    # 2. 카탈로그 파일에서 수동 매칭 시도 (ISS 예시)
    try:
        r = requests.get("https://celestrak.org/NORAD/elements/stations.txt", timeout=20)
        lines = r.text.strip().splitlines()
        for i in range(0, len(lines), 3):
            if query in lines[i] or query == lines[i+1].split()[1]:  # 이름 또는 NORAD ID 매칭
                return f"{lines[i]}\n{lines[i+1]}\n{lines[i+2]}"
    except Exception as e:
        st.warning(f"⚠️ 카탈로그 백업 소스 실패: {e}")

    return None

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

if st.session_state["tle_list"]:
    st.subheader("📄 분석용 TLE 누적 출력")
    combined_text = "\n".join(st.session_state["tle_list"])
    st.code(combined_text, language="text")
    st.info("※ 위 내용 우측 상단의 복사 버튼을 눌러 복사하고, 분석 앱에 붙여넣기 하세요.")
