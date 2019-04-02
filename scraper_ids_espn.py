from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv

team_id_categories = ['TeamName', 'TeamId']

team_ids = []

options = Options()
options.add_argument('--headless')
options.add_argument('log-level=3');

def get_ids(row):
	team_info = []
	team_name = row.find('td').find('a', {'name': '&lpos=ncf:teamclubhouse:standings:team'}).text.strip()
	print('Name: ' + team_name)
	team_id = get_id(row.find('a', {'name': '&lpos=ncf:teamclubhouse:standings:team'})['href'])
	print('ID ' + team_id)
	team_info.append(team_name)
	team_info.append(team_id)
	team_ids.append(team_info)


def get_id(data):
	data = data.split('/')
	id = data[5]
	return id


page_url = 'http://www.espn.com/college-football/conference?id=81&_slug_=fcs-aa'

browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)
browser.get(page_url)

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')

table = (soup.find('article', {'class': 'sub-module standings'})).find('table', {'class', 'mod-data'})
table_body = table.findAll('tbody')

for body in table_body:
	teams = body.findAll('tr')
	for row in teams:
		get_ids(row)

browser.close()

with open('fcs_team_ids.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow(team_id_categories)
	writer.writerows(team_ids)