from bs4 import BeautifulSoup
import requests
import re

class Movie:
	def __init__(self, title, plot, actorsList, release, length, status, genreList, imdbRating):
		self.title = title
		self.plot = plot
		self.actorsList = actorsList
		self.release = release
		self.length = length
		self.status = status
		self.genreList = genreList
		self.imdbRating = imdbRating

	def __str__(self):
		movieStr = "Title: " + self.title + "\nPlot: "
		movieStr += self.plot + "\nActors: "
		for actor in self.actorsList:
			movieStr += actor + ", "
		movieStr = movieStr[:-2]
		movieStr += "\nRelease Date: " + self.release + "\nLength: "
		movieStr += self.length + "\nGenres: "
		for genre in self.genreList:
			movieStr += genre + ", "
		movieStr = movieStr[:-2]
		movieStr += "\nIMDB Rating: " + self.imdbRating
		return movieStr


movieQuery = input("Enter Movie Name:")
url = f'https://www.imdb.com/find?q={movieQuery.replace(" ", "+")}&s=tt'
session = requests.session()
# print(url)
s = session.get(url)
soup = BeautifulSoup(session.get(url).content, "lxml")

moviesList = []
results = soup.find("table", class_ = "findList")
resultList = results.find_all("tr")
for result in resultList[:10]:
	resText = result.find("td", class_ = "result_text")
	rT = resText.text.lower()
	if ("tv " in rT) or (movieQuery.lower() not in rT):
		# print(rT, movieQuery, ("tv " in rT), (movieQuery.lower() not in rT))
		continue
	print(rT)
	movieInfoLink = f'https://www.imdb.com{resText.a["href"]}'
	movieSoup = BeautifulSoup(session.get(movieInfoLink).content, "lxml")

	movieTitle = movieSoup.find("div", class_ = "title_wrapper").h1.text[:-8].replace(",", "")
	
	movieStatus = "To Be Downloaded"
	
	movieSubTextSoup = movieSoup.find("div", class_ = "subtext")
	
	try:
		movieActorsListSoup = movieSoup.find_all("div", "credit_summary_item")
		for mALS in movieActorsListSoup:
			if "Star" in mALS.h4.text:
				mALSoup = mALS.find_all("a")
				break
		if len(mALSoup) == 1 or ("see " not in mALSoup[-1].text.lower()):
			movieActorsListSoup = mALSoup
		else:    
			movieActorsListSoup = mALSoup[:-1]
		movieActorsList = [actor.text for actor in movieActorsListSoup]
	except:
		movieActorsList = []
	
	try:
		movieIMDBRating = movieSoup.find("div", class_ = "ratingValue").text[1:-1]
	except:
		movieIMDBRating = "N/A"
	
	try:
		moviePlot = movieSoup.find("div", class_ = "summary_text").text.replace("\n", " ")
		moviePlot = re.sub(r"^.[ ]+", "",moviePlot)
		moviePlot = re.sub(r"\.\.\..*", "...",moviePlot)
		if "add a plot" in moviePlot.lower():
			moviePlot = "N/A"
	except:
		moviePlot = "N/A"
	
	try:
		movieLength = movieSubTextSoup.time.text
		mLSpan = re.search(r"[1-9].*\n", movieLength).span()
		movieLength = movieLength[mLSpan[0]:mLSpan[1]-1]
	except:
		movieLength = "N/A"
	
	try:
		movieInfo = movieSubTextSoup.find_all("a")
		movieGenres = movieInfo[:-1]
		movieGenreList = [t.text for t in movieGenres]
	except:
		movieGenreList = []
	
	try:
		movieReleaseDate = movieInfo[-1].text[:-1]
		span = re.search(r'[0-9].*[0-9]', movieReleaseDate).span()
		movieReleaseDate = movieReleaseDate[span[0]:span[1]]
	except:
		movieReleaseDate = "N/A"

	movie = Movie(movieTitle, moviePlot, movieActorsList, movieReleaseDate, movieLength, movieStatus, movieGenreList, movieIMDBRating)
	moviesList.append(movie)

for movie in moviesList:
	print(movie,"")

if len(moviesList):
	i = int(input(f"Enter your choice [1-{len(moviesList)}]: "))
	if i in range(1,len(moviesList)+1):
		with open("mvStatus_local.csv", "a") as f:
			movie = moviesList[i-1]
			print(repr(movie.title))
			f.write(f"{movie.title},{movie.release},{movie.status}\n")
	else:
		print("GTFO")