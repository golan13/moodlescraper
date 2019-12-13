"""
This python script will login to your moodle account, get your course grades and display them.
You must enter your username and password
"""
import requests
from bs4 import BeautifulSoup

USERNAME = 'FirstName.LastName'
PASSWORD = 'Password'

"""
Returns the payload to be sent to moodle for authentication.
"""
def payload():
    return {'username': USERNAME,
            'password': PASSWORD,
            'vhost': 'standard'
            }

"""
Logs in to the moodle site using the user's credentials and the token from the moodle site
"""
def login(s):
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) '
                                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'})
    s.get('https://my.idc.ac.il/')
    s.post('https://my.idc.ac.il/my.policy', data=payload())
    login_site = s.get('http://moodle.idc.ac.il/2020/my/index.php?lang=en')
    soup = BeautifulSoup(login_site.text, 'html.parser')
    token = soup.find('input', {'name': 'logintoken'}).get('value')
    token_payload = {
        'username': 'golan.cohen',
        'password': 'f5-sso-token',
        'logintoken': token
    }
    main_page = s.post('https://moodle.idc.ac.il/2020/login/index.php?f5-sso-form=login_2020', data=token_payload)
    return main_page

"""
Returns a tuple of the names of the courses you are enrolled in and the affiliated links to the course homepage
"""
def get_courses(main_page):
    soup = BeautifulSoup(main_page.text, 'html.parser')
    dashboard = soup.find('a', {'title': 'My courses'})
    menu = dashboard.next_sibling
    courses = menu.findAll('a')
    courses_links = []
    courses_titles = []
    courses_ids = []
    for course in courses:
        course_title = (course.get('title'))
        if (course_title != "Dashboard"):
            courses_titles.append(course_title)
            courses_links.append(course.get('href'))
            courses_ids.append(course.get('href')[-6:])
    return (courses_titles, courses_links, courses_ids)

"""
Gets the session and a course id and returns a list of grades.
"""
def get_grades(s, id):
    grade_page = s.get('https://moodle.idc.ac.il/2020/grade/report/user/index.php', params={'id': id})
    soup = BeautifulSoup(grade_page.text, 'html.parser')
    table = soup.find('table')
    table_body = table.tbody
    assignments = table_body.find_all('a', {'class': 'gradeitemheader'})
    grades = table_body.select('td.column-grade.level2')
    if id == '200383':
        grades = grades[1:]
    for index,item in enumerate(assignments):
        grade = grades[index].string
        if grade == '-':
            grade = 'No Grade'
        print(str(index+1) + '.', "'" + assignments[index].get_text() + "'",'-', grade)

def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')

def main():
    with requests.session() as s:
        main_page = login(s)
        (courses_titles, courses_links, courses_ids) = get_courses(main_page)
        for i in range(len(courses_titles)):
            print(courses_titles[i])
            get_grades(s, courses_ids[i])
            print('\n')

if __name__ == '__main__':
    main()