import numpy as np
import os
import math
import pandas as pd
import random
import pickle
import csv

training_data = []
base_elo = 1600
team_elos = {}
team_stats = {}
prediction_year = 2018

def init_data():
	for i in range(2015, prediction_year+1):
		team_elos[i] = {}
		team_stats[i] = {}

def calc_elo(win_team, lose_team, season):
	winner_rank = get_elo(season, win_team)
	loser_rank = get_elo(season, lose_team)

	rank_diff = winner_rank - loser_rank
	exp = rank_diff * -1/400
	odds = 1 / (1 + math.pow(10, exp))

	if winner_rank < 2100:
		k = 64
	elif winner_rank >= 2100 and winner_rank < 2400:
		k = 32
	else:
		k = 24

	new_winner_rank = round(winner_rank + (k*(1 - odds)))
	new_rank_diff = new_winner_rank - winner_rank
	new_loser_rank = loser_rank - new_rank_diff

	return new_winner_rank, new_loser_rank

def get_elo(season, team):
	try:
		return team_elos[season][team]
	except:
		try:
			team_elo = team_elos[season-1][team]
			team_elo = (.65*team_elo)+(.35*base_elo)
			team_elos[season][team] = team_elo
			return team_elos[season][team]
		except:
			team_elos[season][team] = base_elo
			return team_elos[season][team]

def get_stats(season, team, field):
	try:
		l = team_stats[season][team][field]
		return sum(l) / float(len(l))
	except:
		return 0

def update_stats(season, team, fields):
	if team not in team_stats[season]:
		team_stats[season][team] = {}

	for key, value in fields.items():
		if key not in team_stats[season][team]:
			team_stats[season][team][key] = []

		if len(team_stats[season][team][key]) >= 9:
			team_stats[season][team][key].pop()

		team_stats[season][team][key].append(value)

def build_season_data(all_data):
	print("Building season data.")

	for index, row in all_data.iterrows():
		skip = 0
		team_1_elo = get_elo(row['Season'], row['WId'])
		team_2_elo = get_elo(row['Season'], row['LId'])

		team_1_features = [team_1_elo]
		team_2_features = [team_2_elo]

		for field in stat_fields:
			team_1_stat = get_stats(row['Season'], row['WId'], field)
			team_2_stat = get_stats(row['Season'], row['LId'], field)

			if team_1_stat is not None and team_2_stat is not None:
				team_1_features.append(team_1_stat)
				team_2_features.append(team_2_stat)
			else:
				skip = 1

		if skip == 0:
			matchup_features = [row['WLoc']]
			if random.random() > 0.5:
				for i in range(17):
					matchup_features.append(team_1_features[i] - team_2_features[i])
				training_data.append([matchup_features, 1])
			else:
				for i in range(17):
					matchup_features.append(team_2_features[i] - team_1_features[i])
				training_data.append([matchup_features, 0])

		if row['WTotal_Yards'] != 0 and row['LTotal_Yards'] != 0:
			stat_1_fields = {
				'score': row['WScore'],
				'first_down': row['WFirst_Downs'],
				'third_down': row['WThird_Downs'],
				'fourth_down': row['WFourth_Downs'],
				'total_yards': row['WTotal_Yards'],
				'passing': row['WPassing'],
				'comp_perc': row['WComp_Perc'],
				'yards_per_pass': row['WYards_Per_Pass'],
				'rushing': row['WRushing'],
				'rushing_attempts': row['WRushing_Attempts'],
				'yards_per_rush': row['WYards_Per_Rush'],
				'penalties': row['WPenalties'],
				'penality_yards': row['WPenalty_Yards'],
				'turnovers': row['WTurnovers'],
				'fumbles': row['WFumbles_Lost'],
				'interceptions': row['WInterceptions_Thrown'],
				'possession': row['WPossession']
			}
			stat_2_fields = {
				'score': row['LScore'],
				'first_down': row['LFirst_Downs'],
				'third_down': row['LThird_Downs'],
				'fourth_down': row['LFourth_Downs'],
				'total_yards': row['LTotal_Yards'],
				'passing': row['LPassing'],
				'comp_perc': row['LComp_Perc'],
				'yards_per_pass': row['LYards_Per_Pass'],
				'rushing': row['LRushing'],
				'rushing_attempts': row['LRushing_Attempts'],
				'yards_per_rush': row['LYards_Per_Rush'],
				'penalties': row['LPenalties'],
				'penality_yards': row['LPenalty_Yards'],
				'turnovers': row['LTurnovers'],
				'fumbles': row['LFumbles_Lost'],
				'interceptions': row['LInterceptions_Thrown'],
				'possession': row['LPossession']
			}
			update_stats(row['Season'], row['WId'], stat_1_fields)
			update_stats(row['Season'], row['LId'], stat_2_fields)

		new_winner_rank, new_loser_rank = calc_elo(row['WId'], row['LId'], row['Season'])
		team_elos[row['Season']][row['WId']] = new_winner_rank
		team_elos[row['Season']][row['LId']] = new_loser_rank

stat_fields = ['score', 'first_down', 'third_down', 'fourth_down', 'total_yards', 'passing', 'comp_perc', 'yards_per_pass', 'rushing', 'rushing_attempts', 'yards_per_rush',
'penalties', 'penality_yards', 'turnovers', 'fumbles', 'interceptions', 'possession']

init_data()
season_data = pd.read_csv('data/fcs_data_2015_2018.csv')

build_season_data(season_data)
random.shuffle(training_data)


train_X = []
train_y = []

for features, label in training_data:
	train_X.append(features)
	train_y.append(label)

train_X = np.array(train_X)

pickle_out = open("X.pickle", "wb")
pickle.dump(train_X, pickle_out)
pickle_out.close()

pickle_out = open("y.pickle", "wb")
pickle.dump(train_y, pickle_out)
pickle_out.close()

pickle_out = open("team_elos.pickle", "wb")
pickle.dump(team_elos, pickle_out)
pickle_out.close()

pickle_out = open("team_stats.pickle", "wb")
pickle.dump(team_stats, pickle_out)
pickle_out.close()