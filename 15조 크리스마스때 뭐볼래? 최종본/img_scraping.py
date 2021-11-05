from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

from pymongo import MongoClient
client = MongoClient('13.209.85.13', 27017, username='test', password='test')
db = client.dbsparta

driver = webdriver.Chrome('./chromedriver')  # 드라이버를 실행합니다.

url = "https://www.themoviedb.org/movie/now-playing?language=ko-KR"

driver.get(url)  # 드라이버에 해당 url의 웹페이지를 띄웁니다.
sleep(2) # 페이지가 로딩되는 동안 1초 간 기다립니다.

showBtn = driver.find_element_by_css_selector('#pagination_page_1 > p > a')
showBtn.click()
sleep(2)

for i in range(1,3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")  # 1000픽셀만큼 내리기
    sleep(2)

req = driver.page_source  # html 정보를 가져옵니다.
driver.quit()  # 정보를 가져왔으므로 드라이버는 꺼줍니다.

soup = BeautifulSoup(req, 'html.parser')  # 가져온 정보를 beautifulsoup으로 파싱해줍니다.

like = ''
for i in range(1,3):
    movies = soup.select("#page_" + str(i) + "> div")
    baseUrl = "https://www.themoviedb.org"
    for movie in movies:
        ori_movie_img = movie.select_one("div.image > div.wrapper > a > img")['src']
        movie_img = baseUrl + ori_movie_img
        movie_name = movie.select_one("div.content > h2 > a").text
        movie_release = movie.select_one("div.content > p") .text
        print(movie_img, movie_name, movie_release)
        doc = {
            'movie_name': movie_name,
            'movie_img': movie_img,
            'movie_release': movie_release,
            'like': like
        }
        db.movie_list.insert_one(doc)
