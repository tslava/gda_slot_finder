# https://www.gdansk.pl/rezerwacja#wybor

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

GRUPA = "urząd stanu cywilnego"
SPRAWA = "Wpis zagranicznych aktów stanu cywilnego"

# Initialize the Chrome driver (you must have Chrome and chromedriver installed)
driver = webdriver.Chrome()

# Navigate to the web page
driver.get("https://www.gdansk.pl/rezerwacja#wybor")


def parse_web_page():
    # Grupa
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "group"))
    )
    select = Select(select_element)
    select.select_by_visible_text(GRUPA)

    # Sprawa
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "sprawa"))
    )
    select = Select(select_element)
    select.select_by_visible_text(SPRAWA)

    # Miesiąc
    o=0
    # Wait for the information to load after selecting the option (adjust the locator and condition as needed)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "kontener_kalendarz ml-md-3"))
    )

    # Extract the data you need
    data = element.text

    # Close the browser
    driver.quit()


# Now you can parse and use the 'data' variable as needed

if __name__ == "__main__":
    o = parse_web_page()
