import streamlit as st
import requests

st.title("🛰️ TLE 호출 for MSSB")

# 🔁 세션 상태 초기화
if "tle_list" not in st.session_state:
    st.session_state["tle_list"] = []

# 입력창 정의 (초기 키 등록)
if "name_input" not in st.session_state:
    st.session_state["name_input"] = ""
if "id_input" not in st.session_state:
    st.session_state["id_input"] = ""

# 🛰️ 입력 폼
sat_name = st.text_input("🛰️ 위성명칭 (예: STARLINK-32502)", value=st.session_state["name_input"], key="name_input")
norad_id = st.text_input("🔢 NORAD ID (예: 62116)", value=st.session_state["id_input"], key="id_input")

# 📡 Celestrak TLE 호출 함수
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

# 📡 호출 버튼
if st.button("📡 TLE 호출"):
    query = ""
    tle = None

    # 입력 값 판별
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

        # 🔄 입력값 초기화
        st.session_state["name_input"] = ""
        st.session_state["id_input"] = ""
    else:
        st.error(f"❌ '{query}'에 대한 TLE 데이터를 찾을 수 없습니다.")

# 📋 누적된 TLE 출력 + 복사
if st.session_state["tle_list"]:
    st.subheader("📄 분석용 TLE 누적 출력")
    full_text = "\n\n".join(st.session_state["tle_list"])

    # 🔹 텍스트박스: 전체 선택 가능 → 복사
    st.text_area("📎 복사해서 붙여넣기 (Ctrl+C 또는 ⌘+C)", value=full_text, height=300, label_visibility="visible")
