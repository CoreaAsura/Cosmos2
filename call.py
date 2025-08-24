# app.py
import html
import urllib.parse
import requests
import streamlit as st

st.title("📡 Space-Track TLE 조회 도구")

# ── 상태 초기화
if "tle_blocks" not in st.session_state:
    st.session_state.tle_blocks = []

# ── Space-Track 로그인 세션
def get_session():
    try:
        username = st.secrets["spacetrack"]["username"]
        password = st.secrets["spacetrack"]["password"]
    except Exception:
        st.error("🔒 st.secrets에 spacetrack 자격증명을 설정하세요: [.streamlit/secrets.toml]")
        st.stop()

    s = requests.Session()
    r = s.post(
        "https://www.space-track.org/ajaxauth/login",
        data={"identity": username, "password": password},
        timeout=20,
    )
    if r.status_code != 200:
        st.error("❌ Space-Track 로그인 실패")
        st.stop()
    return s

# ── 최신 TLE 1개만 가져오기
def fetch_latest_tle(query: str):
    s = get_session()
    if query.isdigit():
        url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{query}/ORDINAL/1/format=json"
    else:
        q = urllib.parse.quote(query)
        url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/OBJECT_NAME/{q}/ORDINAL/1/format/json"

    r = s.get(url, timeout=30)
    if r.status_code != 200:
        return None
    data = r.json()
    if not data and not query.isdigit():
        q2 = urllib.parse.quote(query.upper())
        r2 = s.get(
            f"https://www.space-track.org/basicspacedata/query/class/tle_latest/OBJECT_NAME/{q2}/ORDINAL/1/format/json",
            timeout=30,
        )
        if r2.status_code == 200:
            data = r2.json()

    if not data:
        return None

    rec = data[0]
    return rec["OBJECT_NAME"], rec["TLE_LINE1"], rec["TLE_LINE2"]

# ── UI
user_input = st.text_input("위성이름 또는 NORAD ID를 입력하세요 (예: ISS (ZARYA) 또는 25544)")

col1, col2 = st.columns(2)
with col1:
    if st.button("📥 TLE 조회"):
        q = user_input.strip()
        if q:
            with st.spinner("조회 중…"):
                res = fetch_latest_tle(q)
            if res:
                name, l1, l2 = res
                st.session_state.tle_blocks.append(f"{name}\n{l1}\n{l2}")
            else:
                st.error("해당 입력으로 TLE을 찾지 못했습니다.")
with col2:
    if st.button("🧹 누적 결과 지우기"):
        st.session_state.tle_blocks.clear()

# ── 출력
if st.session_state.tle_blocks:
    output_text = "\n".join(st.session_state.tle_blocks)

    # 텍스트 영역 + copy 버튼을 하나의 블록으로 구성
    st.markdown(
        f"""
        <div style="position: relative">
            <textarea id="tle_out" style="width:100%;height:320px;" readonly>{html.escape(output_text)}</textarea>
            <button onclick="navigator.clipboard.writeText(document.getElementById('tle_out').value)"
                    style="position: absolute; top: 5px; right: 5px; padding:4px 8px; font-size:12px;">
                Copy to clipboard
            </button>
        </div>
        """,
        unsafe_allow_html=True
    )
