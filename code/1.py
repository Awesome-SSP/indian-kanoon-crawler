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
    options.add_argument("--headless=new")  # Optional: run in headless mode
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

def crawl_case_pdfs(start_url):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    driver = init_driver()
    driver.get(start_url)

    time.sleep(2)  # Allow results to load

    # Get all case result links
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
            time.sleep(5)  # Wait for download
        else:
            print(f"⚠️ PDF button not found: {link}")

    driver.quit()
    print("✅ Done. Check the downloads folder.")

if __name__ == "__main__":
    # Replace with the actual search results URL
    # search_url = "https://indiankanoon.org/search/?formInput=doctypes:supremecourt+fromdate:1-3-1951+todate:31-10-1951"
    search_url = "https://indiankanoon.org/search/?formInput=doctypes:supremecourt%20year:1952"
    
    crawl_case_pdfs(search_url)
