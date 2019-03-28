from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import csv

games_stats = []

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

def set_game_stats(game):
	while True:
		try:
			game_stats = []
			#team 1 is away... team 2 is home
			team_1 = game.find('tr', {'class': 'away'})
			team_1_name = team_1.find('span', {'class': 'sb-team-short'}).text.strip()
			team_1_score = team_1.find('td', {'class': 'total'}).find('span').text.strip()

			team_2 = game.find('tr', {'class': 'home'})
			team_2_name = team_2.find('span', {'class': 'sb-team-short'}).text.strip()
			team_2_score = team_2.find('td', {'class': 'total'}).find('span').text.strip()

			game_id = game['id']
			game_url = f'http://www.espn.com/college-football/matchup?gameId={game_id}'

			game_browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)
			print(f'Getting stats from {team_1_name} vs. {team_2_name} game...')
			game_browser.get(game_url)

			game_html = game_browser.page_source
			game_soup = BeautifulSoup(game_html, 'html.parser')

			game_data = ((game_soup.find('table', {'class': 'mod-data'})).find('tbody')).findAll('tr')

			if int(team_2_score) > int(team_1_score):
				game_stats.append(team_2_name)
				game_stats.append(team_2_score)
				game_stats.append(team_1_name)
				game_stats.append(team_1_score)
				game_stats.append('home')
				game_stats.extend(set_winner_stats(game_data, 'away'))
				game_stats.extend(set_loser_stats(game_data, 'home'))

			else:
				game_stats.append(team_1_name)
				game_stats.append(team_1_score)
				game_stats.append(team_2_name)
				game_stats.append(team_2_score)
				game_stats.append('away')
				game_stats.extend(set_winner_stats(game_data, 'home'))
				game_stats.extend(set_loser_stats(game_data, 'away'))

			game_browser.quit()

			game_stats[6] = find_percentage(game_stats[6])
			game_stats[7] = find_percentage(game_stats[7])
			game_stats[10] = find_percentage(game_stats[10])
			game_stats.insert(17, split_second(game_stats[16]))
			game_stats[16] = split_first(game_stats[16])
			game_stats[21] = convert_time(game_stats[21])
			game_stats[23] = find_percentage(game_stats[23])
			game_stats[24] = find_percentage(game_stats[24])
			game_stats[27] = find_percentage(game_stats[27])
			game_stats.insert(34, split_second(game_stats[33]))
			game_stats[33] = split_first(game_stats[33])
			game_stats[38] = convert_time(game_stats[38])


			return game_stats

		except:
			continue

		else:
			break

options = Options()
options.add_argument('--headless')
options.add_argument('log-level=3');

page_url = 'http://www.espn.com/college-football/scoreboard/_/group/81/year/2013/seasontype/2/week/1'

browser = webdriver.Chrome('C:/ChromeDriver/chromedriver.exe', options=options)
browser.get(page_url)

html = browser.page_source
soup = BeautifulSoup(html, 'html.parser')

games = soup.findAll('article', {'class': 'scoreboard football final home-winner js-show'})

for game in games:

	game_data = set_game_stats(game)
	if game_data != None:
		print(game_data)
		games_stats.append(game_data)

	print(games_stats)

	browser.quit()

	'''first_downs = game_data.find('tr', {'data-stat-attr': 'firstDowns'})

	if winner == team_1_name:
		winner_first_downs = first_downs.findAll('td')[1].text.strip()
		loser_first_downs = first_downs.findAll('td')[2].text.strip()
	else:
		winner_first_downs = first_downs.findAll('td')[2].text.strip()
		loser_first_downs = first_downs.findAll('td')[1].text.strip()

	print('Winner First Downs: ' + str(winner_first_downs))
	print('Loser First Downs: ' + str(winner_first_downs))

	third_downs = game_data.find('tr', {'data-stat-attr': 'thirdDownEff'})

	if winner == team_1_name:
		winner_third_downs = find_percentage(third_downs.findAll('td')[1].text.strip())
		loser_third_downs = find_percentage(third_downs.findAll('td')[2].text.strip())
	else:
		winner_third_downs = find_percentage(third_downs.findAll('td')[2].text.strip())
		loser_third_downs = find_percentage(third_downs.findAll('td')[1].text.strip())

	print('Winner Third Downs: ' + str(winner_third_downs))
	print('Loser Third Downs: ' + str(loser_third_downs))

	fourth_downs = game_data.find('tr', {'data-stat-attr': 'fourthDownEff'})

	if winner == team_1_name:
		winner_fourth_downs = find_percentage(fourth_downs.findAll('td')[1].text.strip())
		loser_fourth_downs= find_percentage(fourth_downs.findAll('td')[2].text.strip())
	else:
		winner_fourth_downs = find_percentage(fourth_downs.findAll('td')[2].text.strip())
		loser_fourth_downs = find_percentage(fourth_downs.findAll('td')[1].text.strip())

	print('Winner Fourth Downs: ' + str(winner_fourth_downs))
	print('Loser Fourth Downs: ' + str(loser_fourth_downs))

	total_yards = game_data.find('tr', {'data-stat-attr': 'totalYards'})

	if winner == team_1_name:
		winner_total_yards = total_yards.findAll('td')[1].text.strip()
		loser_total_yards= total_yards.findAll('td')[2].text.strip()
	else:
		winner_total_yards = total_yards.findAll('td')[2].text.strip()
		loser_total_yards = total_yards.findAll('td')[1].text.strip()

	print('Winner Total Yards: ' + str(winner_total_yards))
	print('Loser Total Yards: ' + str(loser_total_yards))

	passing = game_data.find('tr', {'data-stat-attr': 'netPassingYards'})

	if winner == team_1_name:
		winner_passing = passing.findAll('td')[1].text.strip()
		loser_passing= passing.findAll('td')[2].text.strip()
	else:
		winner_passing = passing.findAll('td')[2].text.strip()
		loser_passing = passing.findAll('td')[1].text.strip()

	print('Winner Passing Yards: ' + str(winner_passing))
	print('Loser Passing Yards: ' + str(loser_passing))

	comp_percentage = game_data.find('tr', {'data-stat-attr': 'completionAttempts'})

	if winner == team_1_name:
		winner_comp_percentage = find_percentage(comp_percentage.findAll('td')[1].text.strip())
		loser_comp_percentage= find_percentage(comp_percentage.findAll('td')[2].text.strip())
	else:
		winner_comp_percentage = find_percentage(comp_percentage.findAll('td')[2].text.strip())
		loser_comp_percentage = find_percentage(comp_percentage.findAll('td')[1].text.strip())

	print('Winner Completion Percentage: ' + str(winner_comp_percentage))
	print('Loser Completion Percentage: ' + str(loser_comp_percentage))

	passing_yards_per = game_data.find('tr', {'data-stat-attr': 'yardsPerPass'})

	if winner == team_1_name:
		winner_passing_yards_per = passing_yards_per.findAll('td')[1].text.strip()
		loser_passing_yards_per= passing_yards_per.findAll('td')[2].text.strip()
	else:
		winner_passing_yards_per = passing_yards_per.findAll('td')[2].text.strip()
		loser_passing_yards_per = passing_yards_per.findAll('td')[1].text.strip()

	print('Winner Passing Yards Per Attempt: ' + str(winner_passing_yards_per))
	print('Loser Passing Yards Per Attempt: ' + str(loser_passing_yards_per))

	interceptions = game_data.find('tr', {'data-stat-attr': 'interceptions'})

	if winner == team_1_name:
		winner_interceptions = interceptions.findAll('td')[1].text.strip()
		loser_interceptions= interceptions.findAll('td')[2].text.strip()
	else:
		winner_interceptions = interceptions.findAll('td')[2].text.strip()
		loser_interceptions = interceptions.findAll('td')[1].text.strip()

	print('Winner Interceptions Thrown: ' + str(winner_interceptions))
	print('Loser Interceptions Thrown: ' + str(loser_interceptions))

	rushing = game_data.find('tr', {'data-stat-attr': 'rushingYards'})

	if winner == team_1_name:
		winner_rushing = rushing.findAll('td')[1].text.strip()
		loser_rushing= rushing.findAll('td')[2].text.strip()
	else:
		winner_rushing = rushing.findAll('td')[2].text.strip()
		loser_rushing = rushing.findAll('td')[1].text.strip()

	print('Winner Rushing Yards: ' + str(winner_rushing))
	print('Loser Rushing Yards: ' + str(loser_rushing))

	rush_attempts = game_data.find('tr', {'data-stat-attr': 'rushingAttempts'})

	if winner == team_1_name:
		winner_rush_attempts = rush_attempts.findAll('td')[1].text.strip()
		loser_rush_attempts= rush_attempts.findAll('td')[2].text.strip()
	else:
		winner_rush_attempts = rush_attempts.findAll('td')[2].text.strip()
		loser_rush_attempts = rush_attempts.findAll('td')[1].text.strip()

	print('Winner Rush Attempts: ' + str(winner_rush_attempts))
	print('Loser Rush Attempts: ' + str(loser_rush_attempts))

	rush_yards_per = game_data.find('tr', {'data-stat-attr': 'yardsPerRushAttempt'})

	if winner == team_1_name:
		winner_rush_yards_per = rush_yards_per.findAll('td')[1].text.strip()
		loser_rush_yards_per= rush_yards_per.findAll('td')[2].text.strip()
	else:
		winner_rush_yards_per = rush_yards_per.findAll('td')[2].text.strip()
		loser_rush_yards_per = rush_yards_per.findAll('td')[1].text.strip()

	print('Winner Rush Yard Per Attempt: ' + str(winner_rush_yards_per))
	print('Loser Rush Yard Per Attempt: ' + str(loser_rush_yards_per))

	penalties = game_data.find('tr', {'data-stat-attr': 'totalPenaltiesYards'})

	if winner == team_1_name:
		winner_penalties = split_first(penalties.findAll('td')[1].text.strip())
		loser_penalties= split_first(penalties.findAll('td')[2].text.strip())
	else:
		winner_penalties = split_first(penalties.findAll('td')[2].text.strip())
		loser_penalties = split_first(penalties.findAll('td')[1].text.strip())

	print('Winner Penalties: ' + str(winner_penalties))
	print('Loser Penalties: ' + str(loser_penalties))

	penalty_yards = game_data.find('tr', {'data-stat-attr': 'totalPenaltiesYards'})

	if winner == team_1_name:
		winner_penalty_yards = split_second(penalty_yards.findAll('td')[1].text.strip())
		loser_penalty_yards= split_second(penalty_yards.findAll('td')[2].text.strip())
	else:
		winner_penalty_yards = split_second(penalty_yards.findAll('td')[2].text.strip())
		loser_penalty_yards = split_second(penalty_yards.findAll('td')[1].text.strip())

	print('Winner Penalty Yards: ' + str(winner_penalty_yards))
	print('Loser Penalty Yards: ' + str(loser_penalty_yards))

	fumbles = game_data.find('tr', {'data-stat-attr': 'fumblesLost'})

	if winner == team_1_name:
		winner_fumbles = fumbles.findAll('td')[1].text.strip()
		loser_fumbles= fumbles.findAll('td')[2].text.strip()
	else:
		winner_fumbles = fumbles.findAll('td')[2].text.strip()
		loser_fumbles = fumbles.findAll('td')[1].text.strip()

	print('Winner Fumbles Lost: ' + str(winner_fumbles))
	print('Loser Fumbles Lost: ' + str(loser_fumbles))

	possession = game_data.find('tr', {'data-stat-attr': 'possessionTime'})

	if winner == team_1_name:
		winner_possession = convertTime(possession.findAll('td')[1].text.strip())
		loser_possession= convertTime(possession.findAll('td')[2].text.strip())
	else:
		winner_possession = convertTime(possession.findAll('td')[2].text.strip())
		loser_possession = convertTime(possession.findAll('td')[1].text.strip())

	print('Winner Posession: ' + str(winner_possession))
	print('Loser Possession: ' + str(loser_possession))'''


