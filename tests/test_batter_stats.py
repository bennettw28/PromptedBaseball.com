import pandas as pd
from src.queries.batter_stats import add_latest_team
from unittest.mock import patch
from src.queries.batter_stats import get_batter_list

def test_top_inning_uses_away_team():
    df = pd.DataFrame({
        "batter": [1],
        "game_date": ["2024-04-01"],
        "home_team": ["LAD"],
        "away_team": ["SF"],
        "inning_topbot": ["Top"],
    })
    result = add_latest_team(df)
    assert result.iloc[0]["team"] == "SF"

def test_keeps_most_recent_team():
    df = pd.DataFrame({
        "batter": [1, 1],
        "game_date": ["2024-04-01", "2024-05-01"],
        "home_team": ["LAD", "NYY"],
        "away_team": ["SF", "BOS"],
        "inning_topbot": ["Top", "Top"],
    })
    result = add_latest_team(df)
    assert result.iloc[0]["team"] == "BOS"

def test_empty_table():
    df = pd.DataFrame({
        "batter": [],
        "game_date": [],
        "home_team": [],
        "away_team": [],
        "inning_topbot": [],
    })
    result = add_latest_team(df)
    assert len(result) == 0

def test_get_batter_list_with_fakes():
    fake_pitches = pd.DataFrame({
        "game_date": ["2024-04-01", "2024-05-01"],
        "home_team": ["LAD", "NYY"],
        "away_team": ["SF", "BOS"],
        "inning_topbot": ["Top", "Top"],
    })
    fake_names = pd.DataFrame({
        "key_mlbam": [1],
        "name_first": ["Test"],
        "name_last": ["Player"],
    })
    with patch("src.queries.batter_stats.sqlite3.connect"), \
         patch("src.queries.batter_stats.pd.read_sql", return_value=fake_pitches), \
         patch("src.queries.batter_stats.playerid_reverse_lookup", return_value=fake_names):
        result = get_batter_list()
    assert len(result) == 1
    assert result.iloc[0]["team"] == "BOS"