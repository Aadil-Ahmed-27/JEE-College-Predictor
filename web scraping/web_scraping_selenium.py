import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException

def setup_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # Disable images to speed up loading
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    
    PATH = r"C:\Program Files (x86)\chromedriver-win64\chromedriver.exe"
    service = Service(PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def check_element_exists(driver, by, value, timeout=5):
    """Check if element exists and print its state"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        print(f"Element {value} found")
        print(f"Element displayed: {element.is_displayed()}")
        print(f"Element enabled: {element.is_enabled()}")
        return element
    except Exception as e:
        print(f"Element {value} not found: {str(e)}")
        return None

def wait_for_element(driver, by, value, wait_time=30):
    """Wait for element with debugging info"""
    print(f"\nWaiting for element: {value}")
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((by, value))
        )
        print(f"Element {value} found!")
        
        # Wait for element to be visible
        WebDriverWait(driver, wait_time).until(
            EC.visibility_of(element)
        )
        print(f"Element {value} visible!")
        
        return element
    except Exception as e:
        print(f"Error waiting for {value}: {str(e)}")
        # Print page source for debugging
        print("\nPage source:")
        print(driver.page_source[:500])  # Print first 500 chars
        raise

def select_option_safely(driver, element_name, option_value, by_value=False):
    """Safely select an option with enhanced debugging"""
    print(f"\nAttempting to select {option_value} for {element_name}")
    
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}/{max_attempts}")
            
            # Wait for element
            element = wait_for_element(driver, By.NAME, element_name)
            
            # Scroll element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            print("Scrolled to element")
            time.sleep(2)
            
            # Try to select using both methods
            select = Select(element)
            
            if by_value:
                print(f"Selecting by value: {option_value}")
                # Try normal selection first
                try:
                    select.select_by_value(option_value)
                except:
                    # Fallback to JavaScript
                    js_script = f"""
                    var select = document.getElementsByName('{element_name}')[0];
                    select.value = '{option_value}';
                    var event = new Event('change');
                    select.dispatchEvent(event);
                    """
                    driver.execute_script(js_script)
            else:
                print(f"Selecting by visible text: {option_value}")
                # Print available options
                print("Available options:", [o.text for o in select.options])
                select.select_by_visible_text(option_value)
            
            print(f"Successfully selected {option_value}")
            time.sleep(2)
            return
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise

def main():
    driver = None
    try:
        print("Starting script...")
        driver = setup_driver()
        website = "https://josaa.admissions.nic.in/applicant/SeatAllotmentResult/CurrentORCR.aspx"
        driver.get(website)
        
        print("\nPage Title:", driver.title)
        
        # Initial wait and check page readiness
        time.sleep(10)
        print("\nChecking initial page state...")
        
        # Check if main elements exist
        elements_to_check = [
            "ctl00$ContentPlaceHolder1$ddlroundno",
            "ctl00$ContentPlaceHolder1$ddlInstituteType",
            "ctl00$ContentPlaceHolder1$ddlInstitute",
            "ctl00$ContentPlaceHolder1$ddlBranch",
            "ctl00$ContentPlaceHolder1$ddlSeatType"
        ]
        
        for element_name in elements_to_check:
            check_element_exists(driver, By.NAME, element_name)
        
        # Make selections
        print("\nStarting selections...")
        # Select round (using value)
        select_option_safely(driver, "ctl00$ContentPlaceHolder1$ddlroundno", "1", by_value=True)
        
        # Select other options
        selections = [
            ("ctl00$ContentPlaceHolder1$ddlInstituteType", "ALL"),
            ("ctl00$ContentPlaceHolder1$ddlInstitute", "ALL"),
            ("ctl00$ContentPlaceHolder1$ddlBranch", "ALL"),
            ("ctl00$ContentPlaceHolder1$ddlSeatType", "ALL")
        ]
        
        for name, value in selections:
            select_option_safely(driver, name, value)
        
        print("\nAttempting to click submit...")
        # Click submit button using JavaScript
        submit_button = wait_for_element(driver, By.NAME, "ctl00$ContentPlaceHolder1$btnSubmit")
        driver.execute_script("arguments[0].click();", submit_button)
        
        print("\nWaiting for table...")
        # Wait for table with longer timeout
        table_element = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_GridView1"))
        )
        
        # Extract table HTML
        table_html = table_element.get_attribute("outerHTML")
        
        # Convert to DataFrame
        df = pd.read_html(table_html)[0]
        print("\nDataFrame Info:")
        df.info()
        
        # Save to CSV
        df.to_csv("data.csv", index=False)
        print("\nData saved to data.csv")
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        if driver:
            print("\nFinal page source:")
            print(driver.page_source[:500])
            
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()