from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv


team_ids = {}
season = 2015
season_range = [2015, 2016, 2017, 2018]
week_range = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 'Bowls']
games_stats = []

stat_categories = ['Season', 'WId', 'WScore', 'LId', 'LScore', 'WLoc', 'WFirst_Downs', 'WThird_Downs', 'WFourth_Downs', 'WTotal_Yards', 'WPassing',
'WComp_Perc', 'WYards_Per_Pass', 'WInterceptions_Thrown', 'WRushing', 'WRushing_Attempts', 'WYards_Per_Rush', 'WPenalities', 'WPenality_Yards',
'WTurnovers', 'WFumbles_Lost', 'WInterceptions_Thrown', 'WPossession','LFirst_Downs', 'LThird_Downs', 'LFourth_Downs', 'LTotal_Yards', 'LPassing',
'LComp_Perc', 'LYards_Per_Pass', 'LInterceptions_Thrown', 'LRushing', 'LRushing_Attempts', 'LYards_Per_Rush', 'LPenalities', 'LPenality_Yards',
'LTurnovers', 'LFumbles_Lost', 'LInterceptions_Thrown', 'LPossession']

def find_percentage(data):
	try:
		data = data.split('-')
		success = data[0]
		attempts = data[1]
		percentage = float(int(success)/int(attempts))

		return percentage

	except:
		return 0

def split_first(data):
	data = data.split('-')
	return data[0]

def split_second(data):
	data = data.split('-')
	return data[1]

def convert_time(data):
	data = data.split(':')
	minutes = data[0]
	seconds = data[1]
	minutes = int(minutes) * 60
	time = minutes + int(seconds)
	return time

def set_winner_stats(data, where):
	winner_data = []
	for row in data:
		if where == 'away':
			winner_data.append(row.findAll('td')[1].text.strip())
		else:
			winner_data.append(row.findAll('td')[2].text.strip())

	return winner_data

def set_loser_stats(data, where):
	loser_data = []
	for row in data:
		if where == 'home':
			loser_data.append(row.findAll('td')[2].text.strip())
		else:
			loser_data.append(row.findAll('td')[1].text.strip())

	return loser_data

def get_id(data):
	data = data.split('/')
	id = data[5]
	return id

def collect_id(team, id):
	try:
		team_ids[team] = id
	except:
		pass

def dict_to_list(dict):
	dict_list = []
	for i, j in dict.iteritems():
		dict_list.append([i, j])
	return dict_list

def set_game_stats(game):
	game_stats = []
	#team 1 is away... team 2 is home
	team_1 = game.find('tr', {'class': 'away'})
	try:
		team_1_id = get_id(team_1.find('a', {'name': '&lpos=college-football:scoreboard:team'})['href'])
	except:
		team_1_id  = 0
	team_1_name = team_1.find('span', {'class': 'sb-team-short'}).text.strip()
	try:
		team_1_score = team_1.find('td', {'class': 'total'}).find('span').text.strip()
	except:
		pass

	team_2 = game.find('tr', {'class': 'home'})
	try:
		team_2_id = get_id(team_2.find('a', {'name': '&lpos=college-football:scoreboard:team'})['href'])
	except:
		team_2_id = 0
	team_2_name = team_2.find('span', {'class': 'sb-team-short'}).text.strip()
	try:
		team_2_score = team_2.find('td', {'class': 'total'}).find('span').text.strip()
	except:
		pass

	collect_id(team_1_name, team_1_id)
	collect_id(team_2_name, team_2_id)

	game_id = game['id']
	game_url = f'http://www.espn.com/college-football/matchup?gameId={game_id}'

	game_browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)
	game_browser.get(game_url)

	game_html = game_browser.page_source
	game_soup = BeautifulSoup(game_html, 'html.parser')

	print(f'Getting stats from {team_1_name} vs. {team_2_name} game...')

	try:
		game_data = ((game_soup.find('table', {'class': 'mod-data'})).find('tbody')).findAll('tr')

		if int(team_2_score) > int(team_1_score):
			game_stats.append(season)
			game_stats.append(team_2_id)
			game_stats.append(team_2_score)
			game_stats.append(team_1_id)
			game_stats.append(team_1_score)
			game_stats.append(1) #1 equals home
			game_stats.extend(set_winner_stats(game_data, 'away'))
			game_stats.extend(set_loser_stats(game_data, 'home'))

		else:
			game_stats.append(season)
			game_stats.append(team_1_id)
			game_stats.append(team_1_score)
			game_stats.append(team_2_id)
			game_stats.append(team_2_score)
			game_stats.append(0) #0 equals away
			game_stats.extend(set_winner_stats(game_data, 'home'))
			game_stats.extend(set_loser_stats(game_data, 'away'))

		game_browser.quit()

		game_stats[7] = find_percentage(game_stats[7])
		game_stats[8] = find_percentage(game_stats[8])
		game_stats[11] = find_percentage(game_stats[11])
		game_stats.insert(18, split_second(game_stats[17]))
		game_stats[17] = split_first(game_stats[17])
		try:
			game_stats[22] = convert_time(game_stats[22])
		except:
			game_stats[22] = 0
		game_stats[24] = find_percentage(game_stats[24])
		game_stats[25] = find_percentage(game_stats[25])
		game_stats[28] = find_percentage(game_stats[28])
		game_stats.insert(35, split_second(game_stats[34]))
		game_stats[34] = split_first(game_stats[34])
		try:
			game_stats[39] = convert_time(game_stats[39])
		except:
			game_stats[39] = 0

		return game_stats

	except:
		pass

options = Options()
options.add_argument('--headless')
options.add_argument('log-level=3');

for season in season_range:
	season = season
	print('Season: ' + str(season))
	for week in week_range:
		print('Week: ' + str(week))
		if week == 'Bowl':
			page_url = f'http://www.espn.com/college-football/scoreboard/_/group/81/year/{season}/seasontype/3/week/1'
		else:
			page_url = f'http://www.espn.com/college-football/scoreboard/_/group/81/year/{season}/seasontype/2/week/{week}'

		browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)
		browser.get(page_url)

		html = browser.page_source
		soup = BeautifulSoup(html, 'html.parser')

		games = soup.findAll('article', {'class': 'scoreboard'})

		for game in games:

			game_data = set_game_stats(game)
			if game_data != None:
				games_stats.append(game_data)

			browser.quit()

with open('fcs_data_2015_2018.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow(stat_categories)
	writer.writerows(games_stats)

with open('fcs_team_ids.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow('TeamName', 'TeamID')
	writer.writerows(dict_to_list(team_ids))



