import os
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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


def scrape_projects(pages=5):
    driver = get_driver()
    base_url = "https://rera.odisha.gov.in/projects/project-list"
    driver.get(base_url)
    time.sleep(4)

    db = SessionLocal()
    for page in range(1, pages + 1):
        print(f"[📄] Scraping page {page}...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        project_cards = soup.find_all("div", class_="card project-card mb-3")

        for card in project_cards:
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
                if not existing:
                    project = Project(
                        rera_no=rera_no,
                        project_name=project_name,
                        promoter_name=promoter_name,
                        promoter_address=address,
                    )
                    db.add(project)
                    print(f"[+] Inserted: {project_name}")
                else:
                    print(f"[!] Skipped (already exists): {project_name}")
            except Exception as e:
                print(f"[❌] Failed to parse card: {e}")

        db.commit()

        # Go to next page
        try:
            next_button = driver.find_element(By.XPATH, '//button[@aria-label="Next"]')
            if "disabled" in next_button.get_attribute("class"):
                break
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(4)
        except Exception as e:
            print(f"[⚠️] Could not navigate to next page: {e}")
            break

    db.close()
    driver.quit()
    print("[✅] Scraping completed.")


if __name__ == "__main__":
    scrape_projects(pages=5)
