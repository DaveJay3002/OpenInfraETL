import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from db.database import SessionLocal
from db.models import Project

chrome_binary_path = "/home/jay-dave/chrome114/chrome-linux64/chrome"
chromedriver_path = "/home/jay-dave/chromedriver114/chromedriver"

options = Options()
options.binary_location = chrome_binary_path
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)


def get_driver():
    chrome_binary_path = "/home/jay-dave/chrome114/chrome-linux64/chrome"
    chromedriver_path = "/home/jay-dave/chromedriver114/chromedriver"

    options = Options()
    options.binary_location = chrome_binary_path
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def scrape_projects():
    driver = get_driver()
    driver.get("https://rera.odisha.gov.in/projects/project-list")

    time.sleep(3)  # wait for JS to render

    soup = BeautifulSoup(driver.page_source, "html.parser")
    project_cards = soup.find_all("div", class_="card project-card mb-3")[:6]

    db = SessionLocal()
    for card in project_cards:
        try:
            project_name = card.find("h5", class_="card-title").get_text(strip=True)
            promoter_name = card.find("small").get_text(strip=True).replace("by ", "")
            address = (
                card.find("label", string="Address")
                .find_next("strong")
                .get_text(strip=True)
            )
            rera_no = card.find("span", class_="fw-bold").get_text(strip=True)

            project = Project(
                rera_no=rera_no,
                project_name=project_name,
                promoter_name=promoter_name,
                promoter_address=address,
            )

            # Check duplicate by RERA No
            existing = db.query(Project).filter(Project.rera_no == rera_no).first()
            if not existing:
                db.add(project)
                print(f"[+] Inserted: {project_name}")
            else:
                print(f"[!] Skipped (already exists): {project_name}")
        except Exception as e:
            print(f"[❌] Failed to parse card: {e}")
    db.commit()
    db.close()
    driver.quit()


if __name__ == "__main__":
    scrape_projects()
