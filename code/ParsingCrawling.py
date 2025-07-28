import os
import time
import csv
import sqlite3
import fitz  # PyMuPDF
import re
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import traceback

# ==== CONFIG ====
BASE_DIR = os.getcwd()
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DB_PATH = os.path.join(OUTPUT_DIR, "kanoon_cases.db")
CSV_PATH = os.path.join(OUTPUT_DIR, "audit_log.csv")
EXCEL_PATH = os.path.join(OUTPUT_DIR, "audit_log.xlsx")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==== SELENIUM ====
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
        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value)))
        element.click()
        return True
    except:
        return False

def get_all_case_links(driver):
    time.sleep(2)
    case_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/doc/"]')
    return list({a.get_attribute("href") for a in case_links if "/doc/" in a.get_attribute("href")})

# ==== PDF PARSER ====
def extract_text_from_pdf(pdf_path):
    try:
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"❌ Failed to parse PDF: {e}")
        return ""

def clean_name(name):
    return name.strip().split(" on ")[0].strip()

def extract_most_recent_date(text):
    import re
    matches = re.findall(r"\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b", text)
    try:
        dates = [datetime.strptime(d.replace('.', '/').replace('-', '/'), "%d/%m/%Y") for d in matches]
        return max(dates).strftime("%d.%m.%Y") if dates else "N/A"
    except:
        return "N/A"

def parse_case_info(text, file):
    import re
 
    case_number = re.search(r"CNR\s*No\.?\s*[:\-]?\s*([A-Z]{2}\d{4}[A-Z]{4}\d{6})", text, re.IGNORECASE)
    if not case_number:
        # Fallback pattern to extract it even if "CNR No." is not printed clearly
        case_number = re.search(r"\b([A-Z]{2}\d{4}[A-Z]{4}\d{6})\b", text)
        
        
    petitioner = re.search(r"(?<=\n)\s*([A-Z][A-Za-z .&]*)\s+v(?:ersus|\.)", text, re.IGNORECASE)
    respondent = re.search(r"v(?:ersus|\.)\s*(.*?)(?=\n|WITH|,|@)", text, re.IGNORECASE)
    status = re.search(r"(?i)(?:presented by|appearing for|status(?:\s*of)?):?\s*(.*)", text)

    file_parts = file.replace(".PDF", "").split("vs")
    fallback_pet = file_parts[0].replace("_", " ") if len(file_parts) > 1 else ""
    fallback_res = file_parts[1].split("on")[0].replace("_", " ") if len(file_parts) > 1 else ""

    return {
        "File Name": file,
        "Case Number": case_number.group(1) if case_number else "",
        "Petitioner": clean_name(petitioner.group(1)) if petitioner else fallback_pet,
        "Respondent": clean_name(respondent.group(1)) if respondent else fallback_res,
        "Hearing Date": extract_most_recent_date(text),
        "Status": status.group(1).strip() if status else "N/A",
        "Timestamp": datetime.now().isoformat()
    }

# ==== DB + CSV ====
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            case_number TEXT,
            petitioner TEXT,
            respondent TEXT,
            hearing_date TEXT,
            status TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    return conn

def save_to_db(cursor, data):
    cursor.execute('''
        INSERT INTO cases (file_name, case_number, petitioner, respondent, hearing_date, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data["File Name"],
        data["Case Number"],
        data["Petitioner"],
        data["Respondent"],
        data["Hearing Date"],
        data["Status"],
        data["Timestamp"]
    ))

def export_logs(records):
    df = pd.DataFrame(records)
    df.to_csv(CSV_PATH, index=False)
    df.to_excel(EXCEL_PATH, index=False)
    print(f"📁 Logs saved: {CSV_PATH}, {EXCEL_PATH}")

# ==== MAIN CRAWLER ====
def crawl_and_extract(user_url, max_pages=10):
    driver = init_driver()
    driver.get(user_url)
    all_case_links = set()

    for page in range(1, max_pages + 1):
        print(f"📄 Scraping page {page}...")
        time.sleep(2)
        all_case_links.update(get_all_case_links(driver))
        try:
            next_button = driver.find_element(By.LINK_TEXT, str(page + 1))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            next_button.click()
        except:
            print("⚠ No more pages or navigation failed.")
            break

    print(f"🔗 Total unique case links: {len(all_case_links)}")

    for idx, link in enumerate(all_case_links):
        print(f"[{idx + 1}/{len(all_case_links)}] Visiting {link}")
        driver.get(link)
        time.sleep(2)
        wait_and_click(driver, By.XPATH, "//button[@id='pdfdoc']")
        time.sleep(3)

    driver.quit()

    # ==== Process Downloaded PDFs ====
    conn = init_db()
    cursor = conn.cursor()
    audit_log = []

    for file in os.listdir(DOWNLOAD_DIR):
        if file.lower().endswith(".pdf"):
            print(f"📑 Processing PDF: {file}")
            pdf_path = os.path.join(DOWNLOAD_DIR, file)
            text = extract_text_from_pdf(pdf_path)
            case_data = parse_case_info(text, file)
            save_to_db(cursor, case_data)
            audit_log.append(case_data)

    conn.commit()
    conn.close()
    export_logs(audit_log)
    print("✅ All done!")

# ==== ENTRY POINT ====
if __name__ == "__main__":
    try:
        user_url = input("🔗 Enter Indian Kanoon search URL (with pagination): ").strip()
        if not user_url.startswith("http"):
            print("❌ Invalid URL.")
        else:
            pages = int(input("🔢 Enter number of pages to scrape (default 10): ") or "10")
            crawl_and_extract(user_url, max_pages=pages)
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
