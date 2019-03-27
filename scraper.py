from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv

season = 2013
season_range = [2013, 2014, 2015, 2016, 2017, 2018]
week_range = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]

games_data = []

winner_stat_categories = ['Wfirst_downs', 'Wfirst_downs_rush', 'Wfirst_down_pass', 'Wfirst_down_penalty',
'Wrushing_yards', 'Wrushing_attempts', 'Wrushing_average', 'Wpassing_yards', 'Wpassing_attempts', 'Wpassing_completions',
'Winterceptions', 'Wpassing_average', 'Wtotal_offense', 'Wtotal_plays', 'Waverage_per_play', 'Wfumbles', 'Wpenalty_yards',
'Wpunts', 'Wavg_per_punt', 'Wpunt_returns', 'Wkickoff_returns', 'Winterception_returns', 'Wthird_down_conversions', 'Wfourth_down_conversions']

loser_stat_categories = ['Lfirst_downs', 'Lfirst_downs_rush', 'Lfirst_down_pass', 'Lfirst_down_penalty',
'Lrushing_yards', 'Lrushing_attempts', 'Lrushing_average', 'Lpassing_yards', 'Lpassing_attempts', 'Lpassing_completions',
'Linterceptions', 'Lpassing_average', 'Ltotal_offense', 'Ltotal_plays', 'Laverage_per_play', 'Lfumbles', 'Lpenalty_yards',
'Lpunts', 'Lavg_per_punt', 'Lpunt_returns', 'Lkickoff_returns', 'Linterception_returns', 'Lthird_down_conversions', 'Lfourth_down_conversions']

stat_categories = ['Season', 'Winner', 'Wscore', 'Loser', 'LScore', 'Winloc']
stat_categories.extend(winner_stat_categories)
stat_categories.extend(loser_stat_categories)

def set_stats(teams):
	while True:
		try:
			game_stats = []
			game_stats.append(season)
			team_1 = teams[0]
			score_1 = team_1.find('span', {'class', 'gamePod-game-team-score'}).text.strip()
			team_1_name = team_1.find('span', {'class', 'gamePod-game-team-name short'}).text.strip()
			team_2 = teams[1]
			score_2 = team_2.find('span', {'class', 'gamePod-game-team-score'}).text.strip()
			team_2_name = team_2.find('span', {'class', 'gamePod-game-team-name short'}).text.strip()

			game_url = game.find('a', {'class', 'gamePod-link'})

			if len(game_url['href']) < 5:
				break

			game_browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)

			print(f'Getting stats from {team_1_name} vs. {team_2_name} game...')

			game_browser.get('https://www.ncaa.com' + game_url['href'] + '/team-stats')
			game_html = game_browser.page_source
			game_browser.quit()

			game_soup = BeautifulSoup(game_html, 'html.parser')
			table = game_soup.find('table', {'class': 'gamecenter-team-stats-table'})

			rows = table.findAll('tr')

			if int(score_2) > int(score_1):
				game_stats.append(team_2_name)
				game_stats.append(score_2)
				game_stats.append(team_1_name)
				game_stats.append(score_1)
				game_stats.append('away')
				game_stats.extend(set_winner_stats(rows, 'away'))
				game_stats.extend(set_loser_stats(rows, 'home'))

			else:
				game_stats.append(team_1_name)
				game_stats.append(score_1)
				game_stats.append(team_2_name)
				game_stats.append(score_2)
				game_stats.append('home')
				game_stats.extend(set_winner_stats(rows, 'home'))
				game_stats.extend(set_loser_stats(rows, 'away'))

			return game_stats

		except:
			continue

		else:
			break

def set_winner_stats(rows, where):
	winner_data = []
	for row in rows:
		for data in row.findAll('td', {'class': where}):
			if data.text.strip() == '-':
				winner_data.append(0)
			else:
				winner_data.append(data.text.strip())

	return winner_data

def set_loser_stats(rows, where):
	loser_data = []
	for row in rows:
		for data in row.findAll('td', {'class': where}):
			if data.text.strip() == '-':
				loser_data.append(0)
			else:
				loser_data.append(data.text.strip())

	return loser_data


options = Options()
options.add_argument('--headless')
options.add_argument('log-level=3');

for season in season_range:
	season = season
	for week in week_range:
		try: 
			if week < 10:
				page_URL = f"https://www.ncaa.com/scoreboard/football/fcs/{season}/0{week}/all-conf"
			else:
				page_URL = f"https://www.ncaa.com/scoreboard/football/fcs/{season}/{week}/all-conf"
		except:
			continue

		browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)
		browser.get(page_URL)

		html = browser.page_source

		soup = BeautifulSoup(html, 'html.parser')

		games = soup.findAll('div', {'class': 'gamePod gamePod-type-game status-final'})

		for game in games:
			teams = game.findAll('li')
			game_data = set_stats(teams)
			if game_data != None:
				print(game_data)
				games_data.append(game_data)

		browser.quit()

with open('fcs_data_2013_2018.csv', 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow(stat_categories)
	writer.writerows(games_data)


