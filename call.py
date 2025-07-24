import streamlit as st
import requests

st.title("🛰️ TLE 호출 for MSSB")

# 세션 초기화
if "tle_list" not in st.session_state:
    st.session_state["tle_list"] = []

# 🛰️ 입력창
sat_name = st.text_input("🛰️ 위성명칭 (예: STARLINK-32502)", key="name_input")
norad_id = st.text_input("🔢 NORAD ID (예: 62116)", key="id_input")

# TLE 호출 함수
def fetch_tle(query, mode="name"):
    base_url = "https://celestrak.org/NORAD/elements/gp.php"
    param = "NAME" if mode == "name" else "CATNR"
    url = f"{base_url}?{param}={query}&FORMAT=tle"
    try:
        r = requests.get(url, timeout=10)
        lines = r.text.strip().splitlines()
        if len(lines) >= 3:
            return f"{lines[0]}\n{lines[1]}\n{lines[2]}"
    except Exception:
        return None
    return None

# 호출 버튼
if st.button("📡 TLE 호출"):
    query = ""
    tle = None

    # 입력값 판별
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

# 누적된 TLE 출력 및 복사 UI
if st.session_state["tle_list"]:
    st.subheader("📄 분석용 TLE 누적 출력")

    full_text = "\n\n".join(st.session_state["tle_list"])

    # 복사용 텍스트박스
    st.text_area(
        label="📎 아래 내용을 선택한 후 복사해서 분석용 앱에 붙여넣기",
        value=full_text,
        height=300,
        label_visibility="visible"
    )
