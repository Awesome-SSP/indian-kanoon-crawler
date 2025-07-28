import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DOWNLOAD_DIR = os.path.join(os.getcwd(), "court_docs")

def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
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

def extract_case_links(driver):
    links = []
    case_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/doc/"]')
    for elem in case_elements:
        href = elem.get_attribute("href")
        if href and "/doc/" in href:
            links.append(href)
    return list(set(links))  # Deduplicate

def go_to_next_page(driver):
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Next']"))
        )
        next_button.click()
        time.sleep(2)
        return True
    except:
        return False

def crawl_case_pdfs(start_url):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    driver = init_driver()
    driver.get(start_url)

    all_case_links = set()

    print("🔄 Scanning all paginated results...")
    while True:
        current_links = extract_case_links(driver)
        print(f"➕ Found {len(current_links)} links on this page")
        all_case_links.update(current_links)

        if not go_to_next_page(driver):
            print("🚫 No more pages to scan.")
            break

    print(f"📊 Total unique case links collected: {len(all_case_links)}")

    for idx, link in enumerate(all_case_links, start=1):
        print(f"[{idx}] 🔍 Visiting: {link}")
        driver.get(link)
        time.sleep(2)

        clicked = wait_and_click(driver, By.XPATH, "//button[@id='pdfdoc']")
        if clicked:
            print(f"📥 Download started: {link}")
            time.sleep(5)
        else:
            print(f"⚠️ PDF not available or button not found: {link}")

    driver.quit()
    print("✅ All done. Check your folder:", DOWNLOAD_DIR)

if __name__ == "__main__":
    search_url = "https://indiankanoon.org/search/?formInput=doctypes:delhihighcourt%20year:2025"
    crawl_case_pdfs(search_url)
