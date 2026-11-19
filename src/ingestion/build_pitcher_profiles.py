import sqlite3
import pandas as pd

DB_PATH = "data/promptedbaseball.db"

conn = sqlite3.connect(DB_PATH)
pitches = pd.read_sql("SELECT pitcher, pitch_type FROM pitches WHERE pitch_type IS NOT NULL", conn)

counts = pitches.groupby(["pitcher", "pitch_type"]).size().unstack(fill_value=0) #df 1 row per pitcher 1 col per pitch type
total = counts.sum(axis=1) #1 row per pitcher showing total pitches

usage = counts.div(total, axis=0).add_prefix("usage_") # add_prefix puts usage infront of every column name
usage["pitches_thrown"] = total #sets pitches thrown as total
order = pd.read_sql("SELECT game_pk, at_bat_number, pitch_number, inning_topbot, pitcher FROM pitches", conn)
order = order.sort_values(["game_pk", "at_bat_number", "pitch_number"])

starters = order.groupby(["game_pk", "inning_topbot"]).head(1)
games = order.groupby("pitcher")["game_pk"].nunique()
starts = starters.groupby("pitcher").size()

role = pd.DataFrame({"games": games, "starts": starts.reindex(games.index, fill_value=0)})
role["start_pct"] = role["starts"] / role["games"]
role["role"] = role["start_pct"].apply(lambda p: "starter" if p >= 0.5 else "reliever")

usage = usage.join(role)
usage = usage.reset_index() #turns pitcher_id from row name to just a regular column(numbers rows)

usage.to_sql("pitcher_profiles", conn, if_exists="replace", index=False)
conn.close()

print(f"built pitcher_profiles: {len(usage)} rows")