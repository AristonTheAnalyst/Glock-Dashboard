from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup Chrome driver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Load the webpage
url = "https://eu.glock.com/en/products/pistols/g19-t-gen5-mos-fx-fof"
driver.get(url)

# Give the page some time to load
time.sleep(5)

try:
    print("TECHNICAL SPECIFICATIONS:")
    print("-----------------------")
    
    # Find all main container divs
    containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'pistoldetail__technicaldata__info') and not(contains(@class, '__title')) and not(contains(@class, '__description'))]")
    
    for container in containers:
        # Extract the title (first child div)
        title_div = container.find_element(By.XPATH, ".//div[contains(@class, '__title')]")
        
        # Extract the description (second child div with paragraph)
        try:
            description_divs = container.find_elements(By.XPATH, ".//div[contains(@class, '__description')]//p")
            descriptions = [p.get_attribute('textContent').strip() for p in description_divs]
            description_text = " | ".join(descriptions)
            
            # Get the raw text content using get_attribute to avoid empty text issues
            title = title_div.get_attribute('textContent').strip()
            
            print(f"{title}: {description_text}")
        except Exception as e:
            print(f"Error with container: {e}")
    
    print("\nDIMENSIONS:")
    print("-----------------------")
    
    # Find all table rows
    rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'pistoldetail__dimensions__table__row')]")
    
    for row in rows:
        try:
            # Get all td elements in this row
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) >= 2:
                # Extract text from the first and second td elements
                dimension_name = cells[0].get_attribute('textContent').strip()
                dimension_value = cells[1].get_attribute('textContent').strip()
                
                print(f"{dimension_name}: {dimension_value}")
        except Exception as e:
            print(f"Error with table row: {e}")
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    driver.quit()