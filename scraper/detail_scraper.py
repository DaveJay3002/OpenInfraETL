import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from db.database import SessionLocal
from db.models import Project

chrome_binary_path = os.getenv("CHROME_BINARY_PATH", "/usr/bin/google-chrome")
chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")


def get_driver():
    options = Options()
    options.binary_location = chrome_binary_path
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=options)


def scrape_promoter_details(driver):
    wait = WebDriverWait(driver, 10)

    # 🔁 Try to click the "Promoter Details" tab
    try:
        promoter_tab = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//a[contains(text(),"Promoter Details")]')
            )
        )
        driver.execute_script("arguments[0].click();", promoter_tab)
        time.sleep(2)
    except Exception as e:
        print(f"[❌] Failed to click Promoter Details tab: {e}")
        return {}

    # ✅ Wait for promoter section to appear
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//label[contains(text(), "Company Name")]')
            )
        )
    except Exception as e:
        print(f"[❌] Promoter details not loaded in time: {e}")
        return {}

    soup = BeautifulSoup(driver.page_source, "html.parser")
    promoter_section = soup.find("div", class_="card-body")
    if not promoter_section:
        print("[❌] Promoter section not found.")
        return {}

    def safe_get_text(label_name):
        label = promoter_section.find("label", string=label_name)
        if label:
            strong = label.find_next("strong")
            if strong:
                return strong.get_text(strip=True)
        return None

    # 🔍 Extract each field clearly
    fields = {
        "company_name": "Company Name",
        "registration_no": "Registration No.",
        "correspondence_office_address": "Correspondence Office Address",
        "registered_office_address": "Registered Office Address",
        "entity": "Entity",
        "email_id": "Email Id",
        "mobile": "Mobile",
        "telephone_no": "Telephone No.",
        "gst_no": "GST No.",
    }

    promoter_details = {}
    for key, label in fields.items():
        value = safe_get_text(label)
        if not value:
            print(f"[⚠️] Missing: {label}")
        promoter_details[key] = value

    return promoter_details


def scrape_projects(pages=2):
    driver = get_driver()
    base_url = "https://rera.odisha.gov.in/projects/project-list"
    driver.get(base_url)
    time.sleep(4)

    db = SessionLocal()

    for page in range(1, pages + 1):
        print(f"[📄] Scraping page {page}...")

        # Handle modal after each page load
        close_swal_modal_if_present(driver)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        project_cards = soup.find_all("div", class_="card project-card mb-3")

        for index, card in enumerate(project_cards[:2]):
            try:
                project_name = card.find("h5", class_="card-title").get_text(strip=True)
                promoter_name = (
                    card.find("small").get_text(strip=True).replace("by ", "")
                )
                address = (
                    card.find("label", string="Address")
                    .find_next("strong")
                    .get_text(strip=True)
                )
                rera_no = card.find("span", class_="fw-bold").get_text(strip=True)

                existing = db.query(Project).filter(Project.rera_no == rera_no).first()
                if existing:
                    print(f"[!] Skipped (already exists): {project_name}")
                    continue

                # Find "View Details" button via Selenium
                project_elements = driver.find_elements(
                    By.CSS_SELECTOR, "div.card.project-card.mb-3"
                )
                project_element = project_elements[index]

                # 🔒 Handle modal if it appears before interaction
                close_swal_modal_if_present(driver)

                view_details_button = project_element.find_element(
                    By.XPATH, './/a[contains(text(), "View Details")]'
                )
                driver.execute_script("arguments[0].click();", view_details_button)

                # Wait for project detail tabs to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "li.nav-item"))
                )

                # 🔒 Handle modal again just in case it appears after navigation
                close_swal_modal_if_present(driver)

                # Scrape promoter details
                promoter_details = scrape_promoter_details(driver)

                project = Project(
                    rera_no=rera_no,
                    project_name=project_name,
                    promoter_name=promoter_name,
                    promoter_address=address,
                    promoter_company_name=promoter_details.get("company_name"),
                    promoter_registration_no=promoter_details.get("registration_no"),
                    promoter_correspondence_office_address=promoter_details.get(
                        "correspondence_office_address"
                    ),
                    promoter_registered_office_address=promoter_details.get(
                        "registered_office_address"
                    ),
                    promoter_entity=promoter_details.get("entity"),
                    promoter_email=promoter_details.get("email_id"),
                    promoter_mobile=promoter_details.get("mobile"),
                    promoter_telephone=promoter_details.get("telephone_no"),
                    promoter_gst_no=promoter_details.get("gst_no"),
                )
                db.add(project)
                db.commit()
                print(f"[+] Inserted: {project_name}")

                # Go back to listing
                driver.back()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.card.project-card.mb-3")
                    )
                )
                time.sleep(2)

            except Exception as e:
                print(f"[❌] Failed to process project '{project_name}': {e}")

        # Next page
        try:
            # Wait until the pagination bar appears again
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//button[@aria-label="Next"]')
                )
            )
            next_button = driver.find_element(By.XPATH, '//button[@aria-label="Next"]')

            if "disabled" in next_button.get_attribute("class"):
                break

            driver.execute_script("arguments[0].click();", next_button)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.card.project-card.mb-3")
                )
            )
            time.sleep(2)
        except Exception as e:
            print(f"[⚠️] Could not navigate to next page: {e}")
            break

    db.close()
    driver.quit()
    print("[✅] Scraping completed.")


def close_swal_modal_if_present(driver, timeout=5):
    try:
        wait = WebDriverWait(driver, timeout)
        modal_ok_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.swal2-confirm"))
        )
        print("[⚠️] SweetAlert2 modal detected. Clicking OK...")
        modal_ok_button.click()

        # Optional: wait for modal to disappear
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "swal2-popup")))
        print("[✔️] Modal dismissed successfully.")
        time.sleep(1)
    except Exception as e:
        print("[ℹ️] No modal present or already dismissed.")


if __name__ == "__main__":
    scrape_projects(pages=2)
