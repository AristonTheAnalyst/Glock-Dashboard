from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os

# Setup Chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# Ensure folder for failed pages exists
os.makedirs("failed_pages", exist_ok=True)

# Load URLs from CSV
with open("glock_products.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    urls = [row["url"] for row in reader]

results = []

for url in urls:
    try:
        driver.get(url)

        # Wait until the name is visible, not just present
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "player3d__gun-info__name"))
        )

        name_el = driver.find_elements(By.CLASS_NAME, "player3d__gun-info__name")
        desc_el = driver.find_elements(By.CLASS_NAME, "pistoldetail__description")

        name = name_el[0].text.strip() if name_el else ""
        desc = desc_el[0].text.strip() if desc_el else ""

        if name:
            results.append((name, desc, url))
            print(f"✅ Scraped: {name}")
        else:
            print(f"⚠️ Skipped (no name): {url}")


    except Exception as e:
        print(f"❌ Error at {url} — {e}")
        # Save the HTML for investigation
        debug_path = f"failed_pages/debug_{urls.index(url)}.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"🕵️ Saved failed HTML to: {debug_path}")
        continue  # Keep going after failure

# Save results to CSV
with open("glock_products_full.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "description", "url"])
    writer.writerows(results)

driver.quit()
print(f"\n✅ Done. Scraped {len(results)} pistols.")
