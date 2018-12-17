from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
import re, os
from datetime import datetime

def match_movie_name(movieQuery, found_movie):
	flag = True
	for term in re.finditer(r'[a-zA-Z]+', movieQuery):
		if term.group(0) not in found_movie:
			flag = False
	return flag

def clean_movieQuery(movieQuery):
	res = ''
	for term in re.finditer(r'[a-zA-Z]+', movieQuery):
		res += '{} '.format(term.group(0))
	return res

def download_movie_from_axemovies(movieQuery, releaseDateQuery, download_dir):
	monthYearQuery = re.search('[A-Za-z].* [0-9]{4}', releaseDateQuery).group(0)
	monthYearQuery = monthYearQuery[:3] + " " + monthYearQuery[-4:]

	url = 'https://axemovies.com/?s={}'.format(clean_movieQuery(movieQuery).replace(" ", "+"))
	sess = requests.session()
	soup = BeautifulSoup(sess.get(url).content, 'lxml')

	movie_links = [x.a['href'] for x in soup.find_all('div', class_='item') ]
	download_folder = os.path.join(download_dir, '{} ({})'.format(clean_movieQuery(movieQuery), monthYearQuery))
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
			and monthYearQuery.lower() in data.span.text.lower() \
			and (( 'hd' in quality.text.lower() and 'cam' not in quality.text.lower()) or '720p' in quality.text.lower()):
				print('Movie found!')
				print('{} {} {}'.format(movieQuery, releaseDateQuery, quality.text))
				browser.get(link)
				browser.find_element_by_xpath('//input[@alt="Download Movie height="]').click()
				result = True
				
				# write to the file that downloading started
				with open('mvStatus_server.csv', 'r+') as f:
					pre_tell = 0
					line = f.readline()
					while len(line) != 0:
						if line.split(',')[0] == movieQuery and monthYearQuery in line.split(',')[1]:
							f.seek(pre_tell)
							f.write('{},{},DIP\n'.format(line.split(",")[0], line.split(",")[1]))
							print('Download Started')
							break
						pre_tell = f.tell()
						line = f.readline()
				break
		except:
			pass
	if result:
		time.sleep(120) # give enough time for download to start
		while True:
			flag = False
			for fil in os.listdir(download_folder):
				if fil[-4:] == 'part':
					flag = True
			if flag:
				time.sleep(300)
			else:
				with open('mvStatus_server.csv', 'r+') as f:
					pre_tell = 0
					line = f.readline()
					while len(line) != 0:
						if line.split(',')[0] == movieQuery and monthYearQuery in line.split(',')[1]:
							f.seek(pre_tell)
							f.write('{},{},DIC\n'.format(line.split(",")[0], line.split(",")[1]))
							break
						pre_tell = f.tell()
						line = f.readline()
				break
	else:
		print('{} Movie not found!'.format(movieQuery))
	browser.quit()
	return result


def go_through_list():
	with open('mvStatus_server.csv', 'r') as f:
		for line in f:
			try:
				if 'TBD' in line.split(',')[2]:
					download_movie_from_axemovies(line.split(',')[0], line.split(',')[1], os.getcwd())
			except:
				pass

# checks the list every 5 minutes for new additions to list
# goes through list if any additions
# or goes through list once in a day to check whether new arrivals at website
# in the old list
def regular_check(last_checked_date, file_last_modified):
	while True:
		stat = os.stat('mvStatus_server.csv')
		today = datetime.now().timetuple().tm_mday
		if stat.st_mtime != file_last_modified:
			file_last_modified = stat.st_mtime
			last_checked_date = today
			try:
				print('File modified! Going through list at {}'.format(datetime.now()))
				go_through_list()
			except:
				pass
		elif last_checked_date != today:
			file_last_modified = stat.st_mtime
			last_checked_date = today
			try:
				print('New Day! Going through list at {}'.format(datetime.now()))
				go_through_list()
			except:
				pass
		else:
			time.sleep(300)

if __name__ == '__main__':
	regular_check(0, 0) # initialise last_checked_dat and file_last_modified
