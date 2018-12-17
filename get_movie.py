from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
import re, os

def match_movie_name(movieQuery, found_movie):
	flag = True
	for term in re.finditer(r'[a-zA-Z]+', movieQuery):
		if term[0] not in found_movie:
			flag = False
	return flag

def clean_movieQuery(movieQuery):
	res = ''
	for term in re.finditer(r'[a-zA-Z]+', movieQuery):
		res += f'{term[0]} '
	return res

def download_movie_from_axemovies(movieQuery, releaseDateQuery, download_dir):
	yearQuery = re.search('[0-9]{4}', releaseDateQuery)[0]

	url = f'https://axemovies.com/?s={clean_movieQuery(movieQuery).replace(" ", "+")}'
	sess = requests.session()
	soup = BeautifulSoup(sess.get(url).content, 'lxml')

	movie_links = [x.a['href'] for x in soup.find_all('div', class_='item') ]
	download_folder = os.path.join(download_dir, f'{clean_movieQuery(movieQuery)} ({yearQuery})')
	profile = webdriver.FirefoxProfile()
	profile.set_preference('browser.download.folderList', 2)
	profile.set_preference('browser.download.manager.showWhenStarting', False)
	profile.set_preference('browser.download.dir', download_folder)
	profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'video/x-flv, video/mp4, application/x-mpegUR, video/MP2T, video/3gpp, video/quicktime, video/x-msvideo, video/x-ms-wmv, video/webm, application/octet-stream' )
	profile.set_preference('browser.helperApps.alwaysAsk.force', False)
	profile.set_preference('browser.download.manager.alertOnEXEOpen', False)
	profile.set_preference('browser.download.manager.focusWhenStarting', False)
	profile.set_preference('browser.download.manager.useWindow', False)
	profile.set_preference('browser.download.manager.showAlertOnComplete', False)
	profile.set_preference('browser.download.manager.closeWhenDone', True)
	browser = webdriver.Firefox(profile)

	result = False # whether downloaded or not downloaded
	for link in movie_links:
		s = BeautifulSoup(requests.get(link).content, 'lxml')
		data = s.find('div', class_='data')
		quality = s.find('span', 'calidad2')
		try:
			if match_movie_name(movieQuery.lower(), data.span.text.lower()) \
			and yearQuery.lower() in data.span.text.lower() \
			and (( 'hd' in quality.text.lower() and 'cam' not in quality.text.lower()) or '720p' in quality.text.lower()):
				print('Movie found!')
				print(f'{movieQuery} {releaseDateQuery} {quality.text}')
				browser.get(link)
				browser.find_element_by_xpath('//input[@alt="Download Movie height="]').click()
				result = True
				
				# write to the file that downloading started
				with open('mvStatus_local.csv', 'r+') as f: # currently for local
					pre_tell = 0
					line = f.readline()
					while len(line) != 0:
						if line.split(',')[0] == movieQuery and yearQuery in line.split(',')[1]:
							f.seek(pre_tell)
							f.write(f'{line.split(",")[0]},{line.split(",")[1]},DIP\n')
							print('Download Started')
							break
						pre_tell = f.tell()
						line = f.readline()
				break
		except:
			pass
	if result:
		time.sleep(60) # give enough time for download to start
		while True:
			flag = False
			for fil in os.listdir(download_folder):
				if fil[-4:] == 'part':
					flag = True
			if flag:
				time.sleep(300)
			else:
				with open('mvStatus_local.csv', 'r+') as f: # currently for local
					pre_tell = 0
					line = f.readline()
					while len(line) != 0:
						if line.split(',')[0] == movieQuery and yearQuery in line.split(',')[1]:
							f.seek(pre_tell)
							f.write(f'{line.split(",")[0]},{line.split(",")[1]},DIC\n')
							break
						pre_tell = f.tell()
						line = f.readline()
				break
	else:
		print(f'{movieQuery} Movie not found!')
	browser.quit()
	return result


with open('mvStatus_local.csv', 'r') as f:
	for line in f:
		if 'TBD' in line.split(',')[2]:
			download_movie_from_axemovies(line.split(',')[0], line.split(',')[1], os.getcwd())

# print(match_movie_name("Mission: Impossible - Fallout".lower(), "Mission Impossible Fallout".lower()))

				
		
			





