import streamlit as st
import requests
import re

st.title("🛰️ TLE 호출 for MSSB")

# 입력 UI
sat_name = st.text_input("🛰️ 위성명칭 (예: STARLINK-32502)")
norad_id = st.text_input("🔢 NORAD ID (예: 62116)")

def fetch_tle_by_name(satellite_name):
    url = f"https://celestrak.org/NORAD/elements/gp.php?NAME={satellite_name}&FORMAT=tle"
    try:
        r = requests.get(url, timeout=10)
        lines = r.text.strip().splitlines()
        if len(lines) >= 3:
            return f"{lines[0]}\n{lines[1]}\n{lines[2]}"
    except Exception as e:
        return f"# ⚠️ 오류: {str(e)}"
    return None

def fetch_tle_by_id(norad_id):
    url = f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=tle"
    try:
        r = requests.get(url, timeout=10)
        lines = r.text.strip().splitlines()
        if len(lines) >= 3:
            return f"{lines[0]}\n{lines[1]}\n{lines[2]}"
    except Exception as e:
        return f"# ⚠️ 오류: {str(e)}"
    return None

# 호출 버튼
if st.button("📡 TLE 호출"):
    result = None

    if sat_name.strip():
        result = fetch_tle_by_name(sat_name.strip())
    elif norad_id.strip():
        result = fetch_tle_by_id(norad_id.strip())
    else:
        st.warning("위성명칭 또는 NORAD ID 중 하나를 입력해주세요.")

    if result:
        if result.startswith("#"):
            st.error(result)
        else:
            st.subheader("📄 분석용 TLE 형식 출력")
            st.text(result)
    elif not sat_name.strip() and not norad_id.strip():
        pass
    else:
        st.error("❌ 해당 입력에 대해 TLE 데이터를 찾을 수 없습니다.")
