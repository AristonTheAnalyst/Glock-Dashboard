from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

# Setup Chrome with webdriver-manager
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # run without GUI
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Navigate to Glock Pistols page
driver.get("https://eu.glock.com/en/Products/Pistols")

# Wait until the pistol blocks are loaded
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, "pistol-list-item__information"))
)

# Extract product names and links
items = driver.find_elements(By.CLASS_NAME, "pistol-list-item__information")
results = []

for item in items:
    try:
        anchor = item.find_element(By.TAG_NAME, "a")
        name = anchor.text.strip()
        link = anchor.get_attribute("href")
        results.append((name, link))
    except Exception as e:
        print("Skipping item due to error:", e)

# Save to CSV
with open("glock_products.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "url"])
    writer.writerows(results)

print(f"✅ Scraped {len(results)} products.")
driver.quit()
