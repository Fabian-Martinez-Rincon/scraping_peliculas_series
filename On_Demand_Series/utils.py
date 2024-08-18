import time
import json
import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_to_json(data, file_path):
    """
    Saves the scraped data to a JSON file.

    Args:
    data (list): The data to save.
    file_path (str): The file path to save the data.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logging.info('Data successfully saved to %s', file_path)
    except IOError as e:
        logging.error('Failed to save data to %s: %s', file_path, str(e))

def click_button(driver, selector_type, selector):
    """
    Clicks on a button based on the provided selector type and value.

    Args:
    driver: The WebDriver instance.
    selector_type (str): Type of selector to use (e.g., "XPATH", "CSS_SELECTOR").
    selector (str): The selector value.

    This function attempts to click on an element specified by the selector.
    If the element is not found or not clickable, it handles the
    exception and prints an error message.
    """
    try:
        by_method = getattr(By, selector_type.upper(), None)
        if not by_method:
            raise ValueError(f"Unsupported selector type provided: {selector_type}")

        button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((by_method, selector))
        )
        time.sleep(1)
        button.click()
        print(f"Clicked on button with {selector_type}: {selector}")
        time.sleep(1)
    except TimeoutException as e:
        print(f"Timeout waiting for button with {selector_type} '{selector}': {str(e)}")
    except WebDriverException as e:
        print(f"Error when clicking on button with {selector_type} '{selector}': {str(e)}")

def wait_for_element_by_xpath(driver, xpath, timeout=10):
    """
    Waits for an element to be visible by its XPath.

    Args:
    driver: The WebDriver instance.
    xpath (str): The XPath of the element to wait for.
    timeout (int): The maximum time to wait for the element.

    Returns:
    WebElement: The WebElement once it is visible.
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
    except TimeoutException:
        print(f"Timeout waiting for element with XPath: {xpath}")
        return None

def get_nav_items(nav_element):
    """
    Extracts navigation items from a navigation element.

    Args:
    nav_element: The WebElement containing the navigation items.

    Returns:
    list: A list of dictionaries, each containing the text and link of navigation items.
    """
    nav_items = nav_element.find_elements(By.TAG_NAME, "a")
    buttons = [{'Categoria': item.text, 'Link': item.get_attribute('href')} for item in nav_items]
    return buttons

def click_button_and_get_nav_items(driver, button_xpath):
    """
    Clicks on a button specified by an XPath and retrieves navigation 
    items from a subsequent navigation area.

    Args:
    driver: Instance of Selenium WebDriver.
    button_xpath (str): XPath to the button that needs to be clicked.

    Returns:
    list: A list of dictionaries, each containing the text and link of navigation items.
    """
    nav_xpath = "/html/body/div[1]/div/div/div/div[1]/div/div/div[1]/div/div[1]/div/nav"

    # Wait for and click the button
    button = wait_for_element_by_xpath(driver, button_xpath)
    if button:
        button.click()

    # Wait for the navigation area to be visible
    nav_element = wait_for_element_by_xpath(driver, nav_xpath)
    if nav_element:
        buttons = get_nav_items(nav_element)
        for button in buttons:
            original_href = button['Link']
            button['Link'] = f"https://pluto.tv/latam{original_href[16:]}?lang=en"
            print(f"Categoría: {button['Categoria']}\nLink: {button['Link']}\n{'-'*40}")
        return buttons
    else:
        return []