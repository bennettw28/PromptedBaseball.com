import requests

player_id = 514888  # Jose Altuve

url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
params = {
    "stats": "gameLog",
    "group": "hitting",
    "season": 2026
}

response = requests.get(url, params=params)
data = response.json()

print(data['stats'][0]['splits'][0])