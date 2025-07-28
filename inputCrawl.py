import os
import time
import urllib.parse
import calendar
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DOWNLOAD_DIR = os.path.join(os.getcwd(), "download")

def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "plugins.always_open_pdf_externally": True,
        "download.prompt_for_download": False,
        "directory_upgrade": True
    })
    return webdriver.Chrome(options=options)

def wait_and_click(driver, by, value, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()
        return True
    except:
        return False

def build_search_url(court_type, year, month, keyword):
    month = int(month)
    _, last_day = calendar.monthrange(int(year), month)
    from_date = f"1-{month}-{year}"
    to_date = f"{last_day}-{month}-{year}"

    query = f"doctypes:{court_type} fromdate:{from_date} todate:{to_date}"
    if keyword:
        query += f" {keyword}"

    # Correct URL encoding for Indian Kanoon
    return f"https://indiankanoon.org/search/?formInput={urllib.parse.quote(query)}"

def crawl_case_pdfs(start_url):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    driver = init_driver()
    driver.get(start_url)

    time.sleep(2)

    # Find case links
    case_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/doc/"]')
    print(f"🔗 Found {len(case_links)} case links")

    links_to_visit = []
    for a in case_links:
        href = a.get_attribute("href")
        if "/doc/" in href:
            links_to_visit.append(href)

    for link in links_to_visit:
        print(f"🔍 Visiting case: {link}")
        driver.get(link)
        time.sleep(2)

        clicked = wait_and_click(driver, By.XPATH, "//button[@id='pdfdoc']")
        if clicked:
            print(f"📥 PDF download initiated for: {link}")
            time.sleep(5)
        else:
            print(f"⚠️ PDF button not found: {link}")

    driver.quit()
    print("✅ Done. Check the 'download' folder.")

if __name__ == "__main__":
    print("📥 Indian Kanoon PDF Extractor")

    court_type = input("Enter court type (e.g., supremecourt, delhi, bombay): ").strip().lower()
    year = input("Enter year (e.g., 1951): ").strip()
    month = input("Enter month (1-12): ").strip()
    keyword = input("Enter optional keyword or location (or press Enter to skip): ").strip()

    search_url = build_search_url(court_type, year, month, keyword)
    print(f"\n🔗 Search URL: {search_url}\n")

    crawl_case_pdfs(search_url)
