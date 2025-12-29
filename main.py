from playwright.sync_api import sync_playwright
from variables import USERID, PASSWORD
import socket


login_url = "https://portal.psut.edu.jo/"
regis_url = "https://portal.psut.edu.jo/Home/RegWebStudent?target=_blank"
regis_url_2 = "https://portal.psut.edu.jo:5050/StudentServices/StudentRegistration.aspx"


row_id_start = "ContentPlaceHolder1_gvRegistrationCoursesSchedule_lblGv"

course_number     = "CourseNo_"
course_name       = "CourseNameEn_"
course_hours      = "Hours_"
course_section    = "Sections_"
course_instructor = "InstructorEn_"
course_day        = "DayEn_"
course_startTime  = "StartTime_"
course_classroom  = "ClassRoomsEn_"
course_maxCap     = "MaxStNo_"
course_registered = "RegStNo_"

add_course_btn = "ContentPlaceHolder1_gvRegistrationCoursesSchedule_lbtnAddCourse_{number}"

tableRowCount = "ContentPlaceHolder1_gvRegistrationCoursesSchedule tr"

mon_wed = 3 
stt = 2

coursesIWant = ['31254', '31374', '11316']
coursesIFollow = ['11435']


sections = ['2','3','1']
sectionsIFollow = ['1']


def notifyBot(message: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 65432))
        s.sendall(message.encode())


def login(loginPage):
    loginPage.fill('input[id="UserID"]', USERID)
    loginPage.fill('input[id="loginPass"]', PASSWORD)
    loginPage.press('input[id="loginPass"]', 'Enter')
    loginPage.wait_for_timeout(1000)
    loginPage.goto(regis_url)
    loginPage.wait_for_timeout(1000)
    loginPage.goto(regis_url_2)
    loginPage.wait_for_timeout(1000)
    return loginPage


def searchForCourse(page, course_id) -> bool:
    course_input = page.locator("#ContentPlaceHolder1_TxtCourseNo")
    if not course_input.count():
        return False

    course_input.fill(course_id)

    # search button (ASP.NET postback)
    search_btn = page.locator("#ContentPlaceHolder1_btnSearch")
    if not search_btn.count():
        return False

    search_btn.click()
    return True


def search(page):
    for crs, course in enumerate(coursesIWant):
        #section = sections[crs]

        if not searchForCourse(page, course):
            continue

        page.wait_for_timeout(500)

        # table rows (skip header)
        rows = page.locator(f"#{tableRowCount}").count()
        for i in range(rows):
            sec_cell = page.locator(f"#{row_id_start}{course_section}{i}")

            if not sec_cell.count():
                continue

            sec = sec_cell.text_content()
            if sec is not None:
                sec = sec.strip()

            add_btn = page.locator(f"a#{add_course_btn.format(number=i)}")
            #if sec == section and add_btn.count():
            if add_btn.count():
                notifyBot(f"registered for course with course id {course}")
                add_btn.click()
                page.wait_for_timeout(2000)

                coursesIWant.remove(course)
                break


    for ind, course in enumerate(coursesIFollow):
        section = sections[ind]
        if not searchForCourse(page, course):
            continue

        page.wait_for_timeout(500)

        rows = page.locator(f"#{tableRowCount}").count()
        for i in range(rows):
            sec_cell = page.locator(f"#{row_id_start}{course_section}{i}")

            if not sec_cell.count():
                continue

            sec = sec_cell.text_content()
            if sec is not None:
                sec = sec.strip()

            add_btn = page.locator(f"a#{add_course_btn.format(number=i)}")
            if sec == section and add_btn.count():
                notifyBot(f"{course} has an empty spot!")
                pass # send signal to bot to send me a message


    # refresh state safely
    page.reload(wait_until="domcontentloaded")



def main():
    notifyBot("this is a test from main()")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        while coursesIWant:
            try:
                page.goto(login_url)
                page = login(page)

                # language button
                lang_btn = page.locator("#lbtnLanguage")
                if lang_btn.count():
                    lang_btn.click()
                page.wait_for_timeout(2000)


                while coursesIWant:
                    search(page)

            except:
                notifyBot("something failed, reset")
                return


main()

