import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# 계정 정보
USERNAME = "your_username"
PASSWORD = "your_password"
NORAD_ID = "25544"  # 예: ISS

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 브라우저 창을 열지 않음
chrome_options.add_argument("--disable-gpu")

# 브라우저 실행
driver = webdriver.Chrome(options=chrome_options)

try:
    # Space-Track 로그인 페이지 이동
    driver.get("https://www.space-track.org/auth/login")

    # 로그인 입력
    driver.find_element(By.ID, "identity").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.NAME, "submit").click()
    time.sleep(3)

    # 로그인 후 TLE 페이지 이동
    tle_url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{NORAD_ID}/orderby/epoch desc/limit/1/format/tle"
    driver.get(tle_url)
    time.sleep(3)

    # 페이지에서 TLE 텍스트 추출
    tle_text = driver.find_element(By.TAG_NAME, "pre").text
    print(tle_text)

finally:
    driver.quit()
