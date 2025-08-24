import streamlit as st
import requests

st.title("🛰️ TLE 호출 for MSSB")

norad_id = st.text_input("🔢 NORAD ID (예: 25544)", key="id_input")

def fetch_tle(norad_id):
    urls = [
        f"https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE",
        "https://celestrak.org/NORAD/elements/stations.txt",
        "https://celestrak.org/NORAD/elements/active.txt",
    ]
    headers = {"User-Agent": "Mozilla/5.0 (TLEFetcher/1.0)"}

    for url in urls:
        try:
            st.write(f"🔗 시도: {url}")
            r = requests.get(url, headers=headers, timeout=15)
            lines = r.text.strip().splitlines()

            # gp.php 직접 호출 성공
            if len(lines) >= 3 and lines[1].startswith("1 ") and lines[2].startswith("2 "):
                return "\n".join(lines[:3])

            # stations.txt 또는 active.txt에서 검색
            for i in range(0, len(lines), 3):
                if str(norad_id) in lines[i+1]:
                    return f"{lines[i]}\n{lines[i+1]}\n{lines[i+2]}"

        except Exception as e:
            st.warning(f"⚠️ {url} 접속 실패: {e}")
    return None

if st.button("📡 TLE 호출"):
    if not norad_id.strip():
        st.warning("NORAD ID를 입력하세요.")
    else:
        tle = fetch_tle(norad_id.strip())
        if tle:
            st.success(f"✅ {norad_id} TLE 데이터:")
            st.code(tle, language="text")
        else:
            st.error(f"❌ {norad_id} TLE 데이터를 가져올 수 없습니다.")
