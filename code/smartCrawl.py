import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# === Config ===
SEARCH_URL = "https://indiankanoon.org/"
SEARCH_QUERY = "doctypes:supremecourt fromdate:1-3-1951 todate:31-3-1951"
OUTPUT_DIR = "court_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Setup driver ===
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def log(msg):
    print(msg)

def download_pdf(pdf_button):
    try:
        pdf_url = pdf_button.get_attribute("href")
        if not pdf_url.endswith(".pdf"):
            log(f"❌ Not a direct PDF: {pdf_url}")
            return
        filename = os.path.join(OUTPUT_DIR, pdf_url.split("/")[-1])
        r = requests.get(pdf_url, stream=True)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            log(f"✅ PDF Downloaded: {filename}")
        else:
            log(f"❌ PDF Request Failed: {pdf_url}")
    except Exception as e:
        log(f"❌ Error downloading PDF: {e}")

try:
    # Step 1: Open the site
    driver.get(SEARCH_URL)
    time.sleep(2)

    # Step 2: Input search query
    search_box = driver.find_element(By.NAME, "term")
    search_box.send_keys(SEARCH_QUERY)
    driver.find_element(By.XPATH, "//input[@value='Search']").click()
    time.sleep(3)

    # Step 3: Click on the first result
    try:
        first_result = driver.find_element(By.XPATH, "//a[contains(@href,'/doc')]")
        doc_url = first_result.get_attribute("href")
        driver.get(doc_url)
        time.sleep(2)

        # Step 4: Click “Get this document in PDF”
        pdf_button = driver.find_element(By.LINK_TEXT, "Get this document in PDF")
        download_pdf(pdf_button)

    except NoSuchElementException:
        log("❌ No results or PDF link found.")
    except Exception as e:
        log(f"❌ Unexpected error: {e}")

finally:
    driver.quit()
    log("✅ Done.")
