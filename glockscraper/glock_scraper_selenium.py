from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import os
import time

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
with open("glock_product_urls.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    urls = [row["url"] for row in reader]

results = []
for url in urls:
    try:
        driver.get(url)
        time.sleep(5)  # Give page time to load
        
        # Get basic product info
        name_el = driver.find_elements(By.CLASS_NAME, "player3d__gun-info__name")
        desc_el = driver.find_elements(By.CLASS_NAME, "pistoldetail__description")
        name = name_el[0].text.strip() if name_el else ""
        desc = desc_el[0].text.strip() if desc_el else ""
        
        # Get technical specifications using the working method
        specs = {}
        weight_values = {
            "Weight_without_magazine": "",
            "Weight_with_empty_magazine": "",
            "Weight_with_loaded_magazine": ""
        }
        
        containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'pistoldetail__technicaldata__info') and not(contains(@class, '__title')) and not(contains(@class, '__description'))]")
        
        for container in containers:
            try:
                title_div = container.find_element(By.XPATH, ".//div[contains(@class, '__title')]")
                title = title_div.get_attribute('textContent').strip()
                
                description_divs = container.find_elements(By.XPATH, ".//div[contains(@class, '__description')]//p")
                descriptions = [p.get_attribute('textContent').strip() for p in description_divs]
                description_text = " | ".join(descriptions)
                
                # Handle weight values separately
                if title == "Weight":
                    if "without magazine" in description_text:
                        weight_values["Weight_without_magazine"] = description_text
                    elif "with empty magazine" in description_text:
                        weight_values["Weight_with_empty_magazine"] = description_text
                    elif "with loaded magazine" in description_text:
                        weight_values["Weight_with_loaded_magazine"] = description_text
                else:
                    specs[title] = description_text
            except Exception:
                continue
        
        # Add all weight values to specs
        specs.update(weight_values)
        
        # Get dimensions from the table, theres only one table and this is its xpath
        rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'pistoldetail__dimensions__table__row')]")
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 2:
                    # Essentially saying, get the first td elements, strip them of their text
                    dimension_name = cells[0].get_attribute('textContent').strip()
                    dimension_value = cells[1].get_attribute('textContent').strip()
                    
                    # Add dimension to specs with "Dimension_" prefix to avoid conflicts
                    specs["Dimension_" + dimension_name] = dimension_value
            except Exception:
                continue
        
        if name:
            row_data = {"name": name, "description": desc, "url": url}
            row_data.update(specs)  # Add all specs and dimensions to the row
            results.append(row_data)
            print(f"Scraped: {name}")
        else:
            print(f"Skipped (no name): {url}")
            
    except Exception as e:
        print(f"Error at {url} — {e}")
        debug_path = f"failed_pages/debug_{urls.index(url)}.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Saved failed HTML to: {debug_path}")
        continue

# Determine all column names from the collected data
all_columns = ["name", "description", "url"]
for row in results:
    for key in row.keys():
        if key not in all_columns:
            all_columns.append(key)

# Save results to CSV
with open("glock_dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=all_columns)
    writer.writeheader()
    writer.writerows(results)

driver.quit()
print(f"Done. Scraped {len(results)} pistols.")