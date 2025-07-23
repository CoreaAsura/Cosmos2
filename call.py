import streamlit as st
import requests

st.title("🛰️ TLE 호출 for MSSB")

# 🔁 세션 스테이트 초기화
if "tle_list" not in st.session_state:
    st.session_state.tle_list = []

# 📌 입력 UI
sat_name = st.text_input("🛰️ 위성명칭 (예: STARLINK-32502)", "")
norad_id = st.text_input("🔢 NORAD ID (예: 62116)", "")

# 📡 TLE 호출 함수
def fetch_tle_by_name(satellite_name):
    url = f"https://celestrak.org/NORAD/elements/gp.php?NAME={satellite_name}&FORMAT=tle"
    try:
        r = requests.get(url, timeout=10)
        lines = r.text.strip().splitlines()
        if len(lines) >= 3:
            return f"{lines[0]}\n{lines[1]}\n{lines[2]}"
    except Exception:
        return None
    return None

def fetch_tle_by_id(norad_id):
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=tle"
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

    if sat_name.strip():
        query = sat_name.strip()
        tle = fetch_tle_by_name(query)
    elif norad_id.strip():
        query = norad_id.strip()
        tle = fetch_tle_by_id(query)

    if not query:
        st.warning("위성명칭 또는 NORAD ID 중 하나를 입력해주세요.")
    elif tle:
        st.session_state.tle_list.append(tle)
        st.success(f"✅ '{query}'에 대한 TLE 호출 성공!")
    else:
        st.error(f"❌ '{query}'에 대한 TLE 데이터를 찾을 수 없습니다.")

# 📋 출력 누적된 TLE
if st.session_state.tle_list:
    st.subheader("📄 분석용 TLE 출력 (누적)")
    combined_text = "\n\n".join(st.session_state.tle_list)
    st.text(combined_text)

    # 📋 복사 버튼
    st.download_button(
        label="📎 클립보드 복사용 텍스트 다운로드",
        data=combined_text,
        file_name="tle_block.txt",
        mime="text/plain"
    )
