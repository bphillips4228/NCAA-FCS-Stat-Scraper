import pandas as pd
import math
import csv
import random
import numpy as np
from numpy import newaxis
import pickle

team_elos = pickle.load(open("team_elos.pickle", "rb"))
team_stats = pickle.load(open("team_stats.pickle", "rb"))
base_elo = 1600
final_data = []
prediction_year = 2018
prediction_range =[2018]

def get_elo(season, team):
	try:
		return team_elos[season][team]
	except:
		try:
			team_elos[season][team] = team_elos[season-1][team]
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

def predict_winner(team_1, team_2, model, season, stat_fields):
	team_1_features = []
	team_2_features = []

	team_1_features.append(get_elo(season, team_1))
	for stat in stat_fields:
		team_1_features.append(get_stats(season, team_1, stat))

	team_2_features.append(get_elo(season, team_2))
	for stat in stat_fields:
		team_2_features.append(get_stats(season, team_2, stat))

	matchup_features = [a - b for a, b in zip(team_1_features, team_2_features)]

	return model.predict(prepare_data(matchup_features))

def prepare_data(features):
	features = np.array(features)
	features = features[newaxis, :]
	return features

def build_team_dict():
	team_ids = pd.read_csv('data/fcs_team_ids.csv')
	team_id_map = {}
	for index, row in team_ids.iterrows():
		team_id_map[row['TeamId']] = row['TeamName']
	return team_id_map

def build_team_record():
	team_ids = pd.read_csv('data/bigsky_season.csv')
	team_record = {}
	for index, row in team_ids.iterrows():
		team_record[row['TeamID']] = {}
		team_record[row['TeamID']]['wins'] = 0
		team_record[row['TeamID']]['losses'] = 0
	return team_record

def get_teams(team_list, year):
	for i in range(len(team_list)):
			for j in range(i + 1, len(team_list)):
				if team_list[i] < team_list[j]:
					prediction = predict_winner(team_list[i], team_list[j], model, year, stat_fields)
					label = str(year) + '_' + str(team_list[i]) + '_' + str(team_list[j])
					final_data.append([label, prediction[0]])

stat_fields = ['score', 'first_down', 'third_down', 'fourth_down', 'total_yards', 'passing', 'comp_perc', 'yards_per_pass', 'rushing', 'rushing_attempts', 'yards_per_rush',
'penalties', 'penality_yards', 'turnovers', 'fumbles', 'interceptions', 'possession']

model = pickle.load(open("models/model.sav", "rb"))

print("Getting teams")
print("Predicting matchups")

seeds = pd.read_csv('data/bigsky_season.csv')
teams = []
for year in prediction_range:
	for index, row in seeds.iterrows():
		if row['Season'] == year:
			teams.append(row['TeamID'])
	teams.sort()

	get_teams(teams, year)
	teams.clear()

prediction_path = 'predictions/bigsky_prediction.csv'

print(f"Writing {len(final_data)} results")
with open(prediction_path, 'w', newline='') as f:
	writer = csv.writer(f)
	writer.writerow(['ID', 'Pred'])
	writer.writerows(final_data)


print("Outputting readable results")
team_id_map = build_team_dict()
team_record = build_team_record()
team_records = []
readable = []
for pred in final_data:
	parts = pred[0].split('_')
	if pred[1] > 0.5:
		winning = int(parts[1])
		losing = int(parts[2])
		probability = pred[1]
		team_record[winning]['wins'] += 1
		team_record[losing]['losses'] += 1
	else:
		winning = int(parts[2])
		losing = int(parts[1])
		probability = 1 - pred[1]
		team_record[winning]['wins'] += 1
		team_record[losing]['losses'] += 1

	readable.append([f"{team_id_map[winning]} beats {team_id_map[losing]}: {probability}"])

for i, j in team_record.items():
	team_records.append([team_id_map[i], j])

with open('predictions/bigsky_readable_predictions.csv', 'w') as f:
	writer = csv.writer(f)
	writer.writerows(team_records)
	writer.writerows(readable)