from playwright.sync_api import sync_playwright
from variables import USERID, PASSWORD
import socket
import threading


response_event = threading.Event()
request_event = threading.Event()
latest_request = None
latest_result = None
lock = threading.Lock()

TIMEOUT = 5


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

coursesIWant = ['31254']
coursesIFollow = []


sections = ['2']
sectionsIFollow = []


def notifyBot(message: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("127.0.0.1", 65432))
        s.sendall(message.encode())


def handle_bot(conn):
    global latest_request, latest_result

    try:
        data = conn.recv(1024).decode()

        with lock:
            latest_request = data
            latest_result = None

        request_event.set()

        if not response_event.wait(timeout=TIMEOUT):
            conn.sendall(b"Something went wrong, timeout hit")
            return

        with lock:
            response = latest_result or "ERROR: empty response"

        conn.sendall(response.encode())

    except Exception as e:
        try:
            conn.sendall(f"ERROR: {e}".encode())

        except:

            pass

    finally:
        response_event.clear()
        conn.close()


def start_request_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 65433))
    s.listen()

    while True:
        conn, _ = s.accept()
        threading.Thread(target=handle_bot, args=(conn,), daemon=True).start()


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
    for course in coursesIWant:
        if not searchForCourse(page, course):
            continue

        page.wait_for_timeout(500)

        # table rows (skip header)
        rows = page.locator(f"#{tableRowCount}").count() - 1
        for i in range(rows):
            sec_cell = page.locator(f"#{row_id_start}{course_section}{i}")

            if not sec_cell.count():
                continue


            sec = sec_cell.text_content()
            if sec is not None:
                sec = sec.strip()

            if request_event.is_set():
                with lock:
                    global latest_result
                    latest_result = f"the service is working properly: section cell: {sec}"
                
                request_event.clear()
                response_event.set()

            add_btn = page.locator(f"a#{add_course_btn.format(number=i)}")
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

        rows = page.locator(f"#{tableRowCount}").count() - 1
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
    notifyBot("Started")
    with sync_playwright() as p:
        while True:
            browser = None
            try:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()

                page.goto(login_url)
                page = login(page)

                lang_btn = page.locator("#lbtnLanguage")
                if lang_btn.count():
                    lang_btn.click()

                page.wait_for_timeout(2000)

                while coursesIWant:
                    search(page)

            except Exception as e:
                notifyBot(f"something failed, resetting...\n{e}")

            finally:
                try:
                    if browser:
                        browser.close()
                except:
                    pass


main()

