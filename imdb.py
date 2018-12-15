from bs4 import BeautifulSoup
import requests

movie = input()
movie = movie.replace(' ', '+')
url = f'https://www.imdb.com/find?q={movie}&s=tt'
sess = requests.session()

print(url)
s = sess.get(url)
soup = BeautifulSoup(sess.get(url).content, 'lxml')

# print(soup.prettify())
with open('mv.html', 'r+') as f:
    f.write(soup.prettify())

