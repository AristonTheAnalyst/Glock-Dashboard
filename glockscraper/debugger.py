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

# Print page source to debug
print("Page title:", driver.title)
print("Current URL:", driver.current_url)

try:
    # Use XPath to find all divs with that class
    divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'pistoldetail__technicaldata__info')]")
    
    print(f"Found {len(divs)} matching divs")
    
    # Extract text from each div
    for i, div in enumerate(divs):
        print(f"\nDiv {i+1}:")
        print("Full HTML:", div.get_attribute('outerHTML'))
        print("Text content:", div.text)
        
        # Try to find any child elements within each div
        children = div.find_elements(By.XPATH, "./*")
        print(f"Found {len(children)} child elements")
        
        for j, child in enumerate(children):
            print(f"  Child {j+1} text: {child.text}")
            
except Exception as e:
    print("Error:", e)
    
finally:
    driver.quit()