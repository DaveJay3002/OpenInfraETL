import logging
import os
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging to show timestamp and message
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_driver():
    """Setup and return configured Chrome WebDriver"""
    chrome_binary_path = "/home/jay-dave/chrome114/chrome-linux64/chrome"
    chromedriver_path = "/home/jay-dave/chromedriver114/chromedriver"

    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary_path
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=options)


def scrape_olx_products(url):
    """
    Scrapes product information from OLX website using Selenium
    Args:
        url (str): The URL of the OLX page to scrape
    Returns:
        list: List of dictionaries containing product details
    """
    driver = setup_driver()
    items = []

    try:
        logger.info(f"Attempting to fetch URL: {url}")
        driver.get(url)

        # Wait for product cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "[data-aut-id='itemBox3']")
            )
        )

        # Find all product cards
        products = driver.find_elements(By.CSS_SELECTOR, "[data-aut-id='itemBox3']")
        logger.info(f"Found {len(products)} product cards on the page")

        for i in range(len(products)):
            try:
                # Re-locate the product card to avoid stale element reference
                product = driver.find_elements(
                    By.CSS_SELECTOR, "[data-aut-id='itemBox3']"
                )[i]

                # Extract product details
                title = product.find_element(
                    By.CSS_SELECTOR, "[data-aut-id='itemTitle']"
                ).text

                price = product.find_element(
                    By.CSS_SELECTOR, "[data-aut-id='itemPrice']"
                ).text

                location = product.find_element(
                    By.CSS_SELECTOR, "[data-aut-id='item-location']"
                ).text

                # Get product URL
                product_url = product.find_element(By.TAG_NAME, "a").get_attribute(
                    "href"
                )

                items.append(
                    {
                        "Title": title,
                        "Price": price,
                        "Location": location,
                        "Product URL": product_url,
                    }
                )

                logger.info(f"Successfully extracted details for: {title}")

            except Exception as e:
                logger.error(f"Error extracting product details: {e}")
                continue

    except Exception as e:
        logger.error(f"Error during scraping: {e}")

    finally:
        driver.quit()

    return items


def main():
    url = "https://www.olx.in/items/q-car-cover"
    logger.info("Starting OLX scraper")

    # Scrape product details
    products = scrape_olx_products(url)

    if products:
        # Save the product details to a CSV file
        output_file = "olx_products.csv"
        df = pd.DataFrame(products)
        df.to_csv(output_file, index=False, encoding="utf-8")
        logger.info(f"Product details saved successfully to {output_file}")
    else:
        logger.warning("No products found or failed to scrape the page")


if __name__ == "__main__":
    main()
