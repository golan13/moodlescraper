"""
This python script will login to your moodle account, get your course grades and display them.
You must enter your username and password
"""

import requests
from bs4 import BeautifulSoup
import Growl
import schedule
import time

"""Global Variables"""
USERNAME = 'YOUR_USERNAME'
PASSWORD = 'YOUR_PASSWORD'
updated_header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) '
                                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
idc_url = 'https://my.idc.ac.il/'
moodle_url = 'https://moodle.idc.ac.il/2020/'
grades_dict = {}
courses_links = []
courses_titles = []
courses_ids = []

"""
Logs in to the moodle site using the user's credentials and the token from the moodle site. Returns the session and the 
main page
"""


def login():
    s = requests.session()
    s.headers.update(updated_header)
    s.get(idc_url)
    payload = {'username': USERNAME,
               'password': PASSWORD,
               'vhost': 'standard'
               }
    s.post(idc_url + 'my.policy', data=payload)
    login_site = s.get(moodle_url + '/my/index.php?lang=en')
    soup = BeautifulSoup(login_site.text, 'html.parser')
    token = soup.find('input', {'name': 'logintoken'}).get('value')
    token_payload = {
        'username': USERNAME,
        'password': 'f5-sso-token',
        'logintoken': token
    }
    main_page = s.post(moodle_url + 'login/index.php?f5-sso-form=login_2020', data=token_payload)
    return s, main_page


"""
This function will fill the grade dictionary.
"""


def set_grade_dict(s, main_page):
    get_courses(main_page)
    for i in range(len(courses_titles)):
        get_grades(s, i, True)


"""
Returns a tuple of the names of the courses you are enrolled in and the affiliated links to the course homepage
"""


def get_courses(main_page):
    soup = BeautifulSoup(main_page.text, 'html.parser')
    dashboard = soup.find('a', {'title': 'My courses'})
    menu = dashboard.next_sibling
    courses = menu.findAll('a')
    for course in courses:
        course_title = (course.get('title'))
        if course_title != "Dashboard":
            courses_titles.append(course_title)
            courses_links.append(course.get('href'))
            courses_ids.append(course.get('href')[-6:])


def update_dict():
    print("Updating grades at " + time.ctime(time.time()))
    s, main_page = login()
    for i in range(len(courses_titles)):
        get_grades(s, i, False)


def get_grades(s, i, first_run):
    grade_page = s.get(moodle_url + 'grade/report/user/index.php', params={'id': courses_ids[i]})
    soup = BeautifulSoup(grade_page.text, 'html.parser')
    table = soup.find('table')
    assignments = table.tbody.find_all('a', {'class': 'gradeitemheader'})
    for index, a in enumerate(assignments):
        grade = a.parent.find_next_sibling('td', {'class': 'column-grade'}).string
        if grade == '-':
            continue
        key = (courses_titles[i], assignments[index].get_text())
        if first_run:
            grades_dict[key] = str(grade)
        else:
            if key not in grades_dict:
                print("Updated grade - " + courses_titles[i] + ' ' + assignments[index].get_text() + ' ' + grade)
                grades_dict[key] = str(grade)
                Growl.send_notification(courses_titles[i], assignments[index].get_text(), grade)


# noinspection PyBroadException
def main():
    print("Logging in to moodle as " + USERNAME)
    session = None
    main_page = None
    try:
        session, main_page = login()
    except:
        print("An error occurred while loggin in")
        print("The program will now exit")
        exit(1)
    print("Log in successful.")
    print("Updating current grades...")
    try:
        set_grade_dict(session, main_page)
    except:
        print("An error occurred while initializing grade dictionary")
        print("The program will now exit")
        exit(2)
    print(grades_dict)
    print("Program will now check for grades every hour and notify when a new grade arrives.")
    schedule.every().hour.do(update_dict)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except:
            print("There was an error trying to update the grades...")
            print("Please check your internet connection")


if __name__ == '__main__':
    main()
