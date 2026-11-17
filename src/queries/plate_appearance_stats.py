import sqlite3
import pandas as pd

DB_PATH = "data/promptedbaseball.db"

HAND_CODES = {"right": "R", "left": "L"}
HAND_WORDS = {"right": "right-handed", "left": "left-handed"}
BASE_NAMES = {"1B": "1st", "2B": "2nd", "3B": "3rd"}

def fmt_rate(value): #puts batting average in correct format
    return f"{value:.3f}".lstrip("0")

def join_words(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1] #This function just adds the word and when there is more than 1 item

def combo_phrase(combo): #combo is a tuple ("1B", "3B")
    if len(combo) == 0:
        return "the bases empty"
    if len(combo) == 3:
        return "the bases loaded"
    if len(combo) == 1:
        return f"a runner on {BASE_NAMES[combo[0]]}"
    return f"runners on {BASE_NAMES[combo[0]]} and {BASE_NAMES[combo[1]]}"

def get_last_x_pa_by_id(player_id, x, pitcher_hand="any", game_type="any", home_away="any",
                        outs=None, innings=None, base_combos=None):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM plate_appearances WHERE batter = ?", conn, params=(player_id,))
    conn.close()

    if pitcher_hand != "any":
        df = df[df["p_throws"] == HAND_CODES[pitcher_hand]]

    if game_type == "regular season":
        df = df[df["game_type"] == "R"]
    elif game_type == "playoffs":
        df = df[df["game_type"] != "R"]

    if home_away == "home":
        df = df[df["is_home"] == 1]
    elif home_away == "away":
        df = df[df["is_home"] == 0]

    if outs:
        df = df[df["outs_when_up"].isin([int(o) for o in outs])]

    if innings:
        numbers = [int(i) for i in innings if i != "extra innings"]
        inning_mask = df["inning"].isin(numbers)
        if "extra innings" in innings:
            inning_mask = inning_mask | (df["inning"] >= 10)
        df = df[inning_mask]

    if base_combos:
        base_strings = ["_".join(combo) if combo else "empty" for combo in base_combos] #[("2B",), ("1B", "3B"), ()] becomes ["2B", "1B_3B", "empty"]
        df = df[df["bases"].isin(base_strings)]

    df = df.sort_values(["game_date", "game_pk", "at_bat_number"])
    df = df.tail(x)

    hits = df["is_hit"].sum()
    at_bats = df["is_ab"].sum()
    home_runs = df["is_hr"].sum()
    walks = df["is_walk"].sum()
    hbp = df["is_hbp"].sum()
    sac_flies = df["is_sac_fly"].sum()
    total_bases = df["total_bases"].sum()

    avg = hits / at_bats if at_bats > 0 else 0
    obp_denominator = at_bats + walks + hbp + sac_flies
    obp = (hits + walks + hbp) / obp_denominator if obp_denominator > 0 else 0
    slg = total_bases / at_bats if at_bats > 0 else 0
    ops = obp + slg

    return hits, at_bats, avg, ops, home_runs, len(df)

def get_pa_sentence(player_id, player_name, x, pitcher_hand="any", game_type="any", home_away="any",
                    outs=None, innings=None, base_combos=None):
    hits, at_bats, avg, ops, home_runs, actual_x = get_last_x_pa_by_id(
        player_id, x, pitcher_hand, game_type, home_away, outs, innings, base_combos
    )

    if actual_x == 0:
        return f"{player_name} has no plate appearances."

    stats_phrase = f"a {fmt_rate(avg)} AVG, {fmt_rate(ops)} OPS"

    conditions = []

    if pitcher_hand != "any":
        conditions.append(f"against {HAND_WORDS[pitcher_hand]} pitchers")

    if game_type == "regular season":
        conditions.append("in the regular season")
    elif game_type == "playoffs":
        conditions.append("in the playoffs")

    if home_away == "home":
        conditions.append("in home games")
    elif home_away == "away":
        conditions.append("in away games")

    if outs:
        out_numbers = sorted(int(o) for o in outs)
        out_text = " or ".join(str(o) for o in out_numbers)
        conditions.append(f"with {out_text} out" if out_numbers == [1] else f"with {out_text} outs")

    if innings:
        numbers = sorted(int(i) for i in innings if i != "extra innings")
        has_extra = "extra innings" in innings
        if not numbers:
            conditions.append("in extra innings")
        elif len(numbers) == 1 and not has_extra:
            conditions.append(f"in inning {numbers[0]}")
        else:
            items = [str(n) for n in numbers] + (["extra innings"] if has_extra else [])
            conditions.append(f"in innings {join_words(items)}")

    if base_combos:
        conditions.append("with " + " or ".join(combo_phrase(combo) for combo in base_combos))

    conditions_phrase = " " + join_words(conditions) if conditions else ""

    if actual_x == 1:
        return f"{player_name} has {stats_phrase} in his last plate appearance{conditions_phrase}."
    return f"{player_name} has {stats_phrase} in his last {actual_x} plate appearances{conditions_phrase}."