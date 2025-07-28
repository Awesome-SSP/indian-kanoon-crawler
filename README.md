🏛️ Indian Kanoon PDF Crawler
This Python script automates the process of extracting and downloading Supreme Court case PDFs from IndianKanoon.org, including pagination handling to collect documents from all available pages.

---

📂 Features
✅ Headless browsing with Chrome

✅ Collects all /doc/ links from paginated results

✅ Automatically downloads all available case PDFs

✅ Deduplicates case links

## ✅ Simple and customizable

🔧 Requirements
Python 3.7+

Google Chrome

ChromeDriver (automatically managed with webdriver_manager)

📦 Installation

```bash
git clone https://github.com/Awesome-SSP/indian-kanoon-crawler.git
cd indian-kanoon-crawler

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install required libraries
pip install -r requirements.txt


```

---

requirements.txt

```bash
selenium
webdriver-manager

```

You can modify the URL to filter by year or date range. For example:

```bash
search_url = "https://indiankanoon.org/search/?formInput=doctypes:supremecourt%20year:1952"
```

---

The downloaded PDFs will be saved in the court_docs/ folder.

🔍 How It Works
Loads the search results page.

Extracts all document links (/doc/).

Clicks "Next" using XPath //a[normalize-space()='Next'].

Iterates through all result pages.

Downloads PDFs from individual document pages using the button with ID pdfdoc.

---

## 📁 Output
All downloaded PDF files are saved in the /court_docs directory relative to the script location.
---

```markdown
[Problem Which is Solved](/assest/problem.md)
```

🛠️ Customization
You can adjust the script to:

🔁 Loop over multiple years automatically

🧾 Save metadata (title, date, URL) to CSV

⚡ Use multithreading for faster downloading

🕵️ Add error logging & retry mechanisms

---

📜 License
MIT License — feel free to use, modify, and share.

---

## 🙋‍♂️ Author

Made with ❤️ by Awesome-SSP

Let the law be accessible — one PDF at a time.

---

## Support

For support, you can buy me a coffee

<a href="https://buymeacoffee.com/i.awesomessp" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
