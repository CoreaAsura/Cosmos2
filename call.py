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

# ── 최신 TLE 1개만 가져오기 (이름 또는 NORAD ID)
def fetch_latest_tle(query: str):
    s = get_session()

    # 숫자면 NORAD, 아니면 OBJECT_NAME
    if query.isdigit():
        url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{query}/ORDINAL/1/format/json"
    else:
        # OBJECT_NAME은 정확 일치 경로이므로 인코딩/대문자 시도
        q = urllib.parse.quote(query)
        url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/OBJECT_NAME/{q}/ORDINAL/1/format/json"

    r = s.get(url, timeout=30)
    if r.status_code != 200:
        return None

    data = r.json()
    if not data:
        # 이름 입력이 대소문자/공백 때문에 실패할 수 있어 대문자 재시도
        if not query.isdigit():
            q2 = urllib.parse.quote(query.upper())
            url2 = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/OBJECT_NAME/{q2}/ORDINAL/1/format/json"
            r2 = s.get(url2, timeout=30)
            if r2.status_code == 200 and r2.text.strip():
                data = r2.json()

    if not data:
        return None

    # tle_latest + ORDINAL/1 ⇒ 최신 1개
    rec = data[0]
    return rec["OBJECT_NAME"], rec["TLE_LINE1"], rec["TLE_LINE2"]

# ── UI
user_input = st.text_input("위성이름 또는 NORAD ID를 입력하세요 (예: ISS (ZARYA) 또는 25544)")

col1, col2 = st.columns(2)
with col1:
    if st.button("📥 TLE 조회"):
        q = user_input.strip()
        if not q:
            st.warning("입력값을 넣어주세요.")
        else:
            with st.spinner("조회 중…"):
                res = fetch_latest_tle(q)
            if res:
                name, l1, l2 = res
                block = f"{name}\n{l1}\n{l2}"
                st.session_state.tle_blocks.append(block)
            else:
                st.error("해당 입력으로 TLE을 찾지 못했습니다.")
with col2:
    if st.button("🧹 누적 결과 지우기"):
        st.session_state.tle_blocks.clear()

# ── 누적 출력 (줄 간격 없이)
if st.session_state.tle_blocks:
    output_text = "\n".join(st.session_state.tle_blocks)  # 빈 줄 추가 없음
    st.text_area("누적된 TLE (복사 대상)", value=output_text, height=320, key="tle_out")

    # ── 클립보드 복사 버튼 (JS)
    #   안전하게 복사하기 위해 숨김 textarea에 내용을 넣고 JS로 복사
    hidden_payload = html.escape(output_text)
    st.markdown(
        f"""
        <textarea id="__tle_copy_buf" style="position:absolute;left:-9999px;top:-9999px;">{hidden_payload}</textarea>
        <button
            onclick="navigator.clipboard.writeText(document.getElementById('__tle_copy_buf').value)
                     .then(()=>{{alert('✅ 클립보드로 복사되었습니다.');}})
                     .catch(()=>{{alert('❌ 복사 실패: 브라우저 권한을 확인하세요.');}})">
            📋 클립보드로 복사
        </button>
        """,
        unsafe_allow_html=True
    )
