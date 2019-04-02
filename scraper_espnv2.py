from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv
import pandas as pd


team_ids = {}
game_num = 0
season = 2015
week = 1
season_range = [2015, 2016, 2017, 2018]
games_stats = []

stat_categories = ['Season', 'Week', 'WId', 'WScore', 'LId', 'LScore', 'WLoc', 'WFirst_Downs', 'WThird_Downs', 'WFourth_Downs', 'WTotal_Yards', 'WPassing',
'WComp_Perc', 'WYards_Per_Pass', 'WInterceptions_Thrown', 'WRushing', 'WRushing_Attempts', 'WYards_Per_Rush', 'WPenalties', 'WPenalty_Yards',
'WTurnovers', 'WFumbles_Lost', 'WInterceptions_Thrown', 'WPossession','LFirst_Downs', 'LThird_Downs', 'LFourth_Downs', 'LTotal_Yards', 'LPassing',
'LComp_Perc', 'LYards_Per_Pass', 'LInterceptions_Thrown', 'LRushing', 'LRushing_Attempts', 'LYards_Per_Rush', 'LPenalties', 'LPenalty_Yards',
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

def dict_to_list(dict):
	dict_list = []
	for i, j in dict.iteritems():
		dict_list.append([i, j])
	return dict_list

def set_game_stats(game):
	game_stats = []
	#team 1 is away... team 2 is home

	game_id = game.find('a')['href'].split('/')[7]
	game_url = f'http://www.espn.com/college-football/matchup?gameId={game_id}'

	game_browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)

	while True:
		try:
			game_browser.get(game_url)
		except:
			continue
		break

	game_html = game_browser.page_source
	game_soup = BeautifulSoup(game_html, 'html.parser')

	team_1 = game_soup.find('div', {'class': 'team away'})

	try:
		team_1_name = team_1.find('span', {'class': 'long-name'}).text.strip()
		team_1_score = team_1.find('div', {'class': 'score-container'}).text.strip()
		team_1_id = team_1.find('div', {'class': 'team-info-wrapper'}).find('a')['href'].split('/')[5]
	except:
		pass

	team_2 = game_soup.find('div', {'class': 'team home'})
	try:
		team_2_name = team_2.find('span', {'class': 'long-name'}).text.strip()
		team_2_score = team_2.find('div', {'class': 'score-container'}).text.strip()
		team_2_id = team_2.find('div', {'class': 'team-info-wrapper'}).find('a')['href'].split('/')[5]
	except:
		pass

	try:
		print(f'Getting stats from Game {game_num}: {team_1_name} vs. {team_2_name} game({season}: Week {week})...')
		game_data = (game_soup.find('table', {'class': 'mod-data'}).find('tbody')).findAll('tr')

		if int(team_2_score) > int(team_1_score):
			game_stats.append(season)
			game_stats.append(week)
			game_stats.append(team_2_id)
			game_stats.append(team_2_score)
			game_stats.append(team_1_id)
			game_stats.append(team_1_score)
			game_stats.append(1) #1 equals home
			game_stats.extend(set_winner_stats(game_data, 'away'))
			game_stats.extend(set_loser_stats(game_data, 'home'))

		else:
			game_stats.append(season)
			game_stats.append(week)
			game_stats.append(team_1_id)
			game_stats.append(team_1_score)
			game_stats.append(team_2_id)
			game_stats.append(team_2_score)
			game_stats.append(0) #0 equals away
			game_stats.extend(set_winner_stats(game_data, 'home'))
			game_stats.extend(set_loser_stats(game_data, 'away'))

		game_browser.quit()

		game_stats[8] = find_percentage(game_stats[8])
		game_stats[9] = find_percentage(game_stats[9])
		game_stats[12] = find_percentage(game_stats[12])
		game_stats.insert(19, split_second(game_stats[18]))
		game_stats[18] = split_first(game_stats[18])
		try:
			game_stats[23] = convert_time(game_stats[23])
		except:
			game_stats[23] = 0
		game_stats[25] = find_percentage(game_stats[25])
		game_stats[26] = find_percentage(game_stats[26])
		game_stats[29] = find_percentage(game_stats[29])
		game_stats.insert(36, split_second(game_stats[35]))
		game_stats[35] = split_first(game_stats[35])
		try:
			game_stats[40] = convert_time(game_stats[40])
		except:
			game_stats[40] = 0

		return game_stats

	except:
		game_browser.quit()
		pass

options = Options()
options.add_argument('--headless')
options.add_argument('log-level=3')
prefs={"profile.managed_default_content_settings.images": 2, 'disk-cache-size': 4096 }
options.add_experimental_option("prefs", prefs)

team_ids = seeds = pd.read_csv('data/fcs_team_ids.csv')

teams = []
for index, row in team_ids.iterrows():
	teams.append(row['TeamId'])
teams.sort()

for team in teams:
	for season in season_range:
		season = season
		print('Season: ' + str(season))
		page_url = f'http://www.espn.com/college-football/team/schedule/_/id/{team}/season/{season}'

		browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)
		browser.get(page_url)

		html = browser.page_source
		soup = BeautifulSoup(html, 'html.parser')

		games = soup.findAll('span', {'class': 'ml4'})
		for game in games:
			game_num = game_num + 1
			game_data = set_game_stats(game)
			if game_data != None:
				games_stats.append(game_data)

			with open('fcs_data_2015_2018_2.csv', 'a', newline='') as f:
				writer = csv.writer(f)
				writer.writerows(games_stats)
				games_stats.clear()

			week = week + 1
			browser.quit()

		game_num = 0
		week = 1







