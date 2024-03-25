from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)
dicc={"Manchester City FC": 85, "Liverpool FC": 83, "Arsenal": 82, "Manchester United FC": 82, "Tottenham Hotspur FC": 81, "Newcastle United FC": 81, "Aston Villa FC": 80, "Chelsea FC": 80, "AFC Richmond FC": 78, "West Ham United FC": 78, "Everton FC": 77, "Brighton FC": 77, "Fulham FC": 77, "Nottingham Forest FC": 77, "Wolverhamton Wanderers": 76, "Brentford FC": 76, "Crystal Palace FC": 76, "Leicester City FC": 75, "Leeds United FC": 73, "Southampton FC": 73}
def get_past_fixtures():
    api_key = 'd6ddc94733044cfa80cdca7703a1c359'
    endpoint = 'https://api.football-data.org/v2/competitions/2021/matches'  # Premier League competition ID is 2021
    
    headers = {'X-Auth-Token': api_key}
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        past_fixtures = []
        for match in data['matches']:
            fixture_date = datetime.strptime(match['utcDate'], '%Y-%m-%dT%H:%M:%S%z')
            if fixture_date.year <= 2023:  # Filter fixtures up to 2023
                fixture = {
                    'HomeTeam': match['homeTeam']['name'],
                    'AwayTeam': match['awayTeam']['name'],
                    'HomeScore': match['score']['fullTime']['homeTeam'] if match['score']['fullTime']['homeTeam'] is not None else "-",
                    'AwayScore': match['score']['fullTime']['awayTeam'] if match['score']['fullTime']['awayTeam'] is not None else "-"
                }
                past_fixtures.append(fixture)
        return past_fixtures
    else:
        print("Failed to fetch past fixtures data.")
        return None
def predict_match_outcome(team1, team2, past_fixtures):
    team1_points = 0
    team2_points = 0
    
    for fixture in past_fixtures:
        if team1 in [fixture['HomeTeam'], fixture['AwayTeam']]:
            if fixture['HomeScore'] == fixture['AwayScore']:
                team1_points += 1
            elif (team1 == fixture['HomeTeam'] and fixture['HomeScore'] > fixture['AwayScore']) or (team1 == fixture['AwayTeam'] and fixture['AwayScore'] > fixture['HomeScore']):
                team1_points += 3
        
        if team2 in [fixture['HomeTeam'], fixture['AwayTeam']]:
            if fixture['HomeScore'] == fixture['AwayScore']:
                team2_points += 1
            elif (team2 == fixture['HomeTeam'] and fixture['HomeScore'] > fixture['AwayScore']) or (team2 == fixture['AwayTeam'] and fixture['AwayScore'] > fixture['HomeScore']):
                team2_points += 3

    if team1_points > team2_points:
        fixture_prediction = team1
    elif team1_points < team2_points:
        fixture_prediction = team2
    else:
        fixture_prediction = "It's a draw"

    team1_ova = dicc.get(team1, 0)
    team2_ova = dicc.get(team2, 0)

    if team1_ova > team2_ova:
        ova_prediction = team1
    elif team1_ova < team2_ova:
        ova_prediction = team2
    else:
        ova_prediction = "It's a draw"

    return fixture_prediction, ova_prediction


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        team1 = request.form['team1']
        team2 = request.form['team2']
        past_fixtures = get_past_fixtures()
        if past_fixtures:
            fixture_prediction, ova_prediction = predict_match_outcome(team1, team2, past_fixtures)
            return render_template('result.html', team1=team1, team2=team2, fixture_prediction=fixture_prediction, ova_prediction=ova_prediction)
    return render_template('index.html')
@app.route('/predict', methods=['POST'])
def predict():
    team1 = request.form['team1']
    team2 = request.form['team2']
    past_fixtures = get_past_fixtures()
    if past_fixtures:
        fixture_prediction, ova_prediction = predict_match_outcome(team1, team2, past_fixtures)
        return render_template('result.html', team1=team1, team2=team2, fixture_prediction=fixture_prediction, ova_prediction=ova_prediction)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
