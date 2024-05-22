from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import traceback
import time
import json

# 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 github token cli for later

login_info = {
    "UserID": "20230798",
    "Password": "Yamen153246846!"
}

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = ChromeService()
driver = webdriver.Chrome(service=service, options=chrome_options)

login_url = "https://portal.psut.edu.jo/"
regis_url = "https://portal.psut.edu.jo/Home/RegWebStudent?target=_blank"
regis_url_2 = "https://portal.psut.edu.jo:5050/StudentServices/StudentRegistration.aspx"

subjects = {}


def process_data():
    try:
        login()
        nav_to_stud_reg()
        load_data()
        # print_data()
        write_data()

    except Exception:
        print(traceback.format_exc())

    finally:
        driver.quit()


def login():
    driver.get(login_url)
    username_field = driver.find_element(By.NAME, list(login_info.keys())[0])
    username_field.send_keys(login_info["UserID"])
    password_field = driver.find_element(By.NAME, list(login_info.keys())[1])
    password_field.send_keys(login_info["Password"])
    password_field.send_keys(Keys.RETURN)


def nav_to_stud_reg():
    # Navigate to StudentRegistration
    WebDriverWait(driver, 3).until(EC.url_contains("Home"))

    # MUST be done this way, psut website is weird (or I'm stupid)
    driver.get(regis_url)
    driver.get(regis_url_2)

    # Change language to english
    driver.find_element(By.ID, "lbtnLanguage").click()

    # Click the search button
    driver.find_element(By.ID, "ContentPlaceHolder1_btnSearch").click()
    time.sleep(2)


def load_data():
    # Do page 1 first as it's the landing page (no page button for current page exists for some reason lol)
    page1 = (
        driver
        .find_element(By.ID, "ContentPlaceHolder1_gvRegistrationCoursesSchedule")
        .text
        .split('\n')
    )
    pages = page1[32:]
    add_data(page1[1:len(page1) - len(pages) - 1])
    time.sleep(1)

    for pg_num in pages:
        driver.find_element(By.LINK_TEXT, pg_num).click()

        # Wait to ensure data loaded after clicking page button
        time.sleep(1)
        page = (
            driver
            .find_element(By.ID, "ContentPlaceHolder1_gvRegistrationCoursesSchedule")
            .text
            .split('\n')
        )
        add_data(page[1:len(page) - len(pages) - 1])


def add_data(page):
    for subject in page:
        data: list[str] = subject.split()[1:]
        course_title = ""

        while True:
            if data[0].isdigit():
                break

            else:
                course_title += f"{data[0]} "

            data.pop(0)

        key = f"{course_title}Section {data[1]}"
        subjects[key] = {}
        i = -2

        # If course is not full (it would add two items, "Add" and "course")
        if "Add" in data:
            i -= 2

        subjects[key]["Max seats"] = int(data[i])
        subjects[key]["Current seats"] = int(data[i+1])


def print_data():
    for s, v in subjects.items():
        print(f"{s}: {v}")


def write_data():
    with open("data.json", "r") as file:
        previous_data = json.load(file)

    for k, v in subjects.items():
        if k not in previous_data or v != previous_data[k]:
            print()
            print(f"{k} was updated:\n"
                  f"\tOld: {previous_data[k] if k in previous_data else 'Was not available'}\n"
                  f"\tNew: {subjects[k]}.")

    with open("data.json", "w") as file:
        json.dump(subjects, file, indent=4)


if __name__ == '__main__':
    process_data()
