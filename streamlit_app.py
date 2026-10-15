import streamlit as st
from src.queries.pitcher_stats import get_pitcher_list, get_last_x_outings_by_id
from src.queries.batter_stats import get_batter_list, get_last_x_games_by_id

st.set_page_config(page_title="PromptedBaseball")
import unicodedata

def strip_accents(text): #Takes accents off of names
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

def fmt_rate(x): #Formats Stats
    return f"{x:.3f}".lstrip("0")

@st.cache_data #this remembers the batters and pitchers list so it doesnt need to re run every click
def load_pitchers(): 
    df = get_pitcher_list()
    df['display_name'] = df.apply(
        lambda r: strip_accents(r['player_name'].split(", ")[1] + " " + r['player_name'].split(", ")[0]) + " (" + r['team'] + ")",
        axis=1 #Axis =1 tells the function to work across each row not each column
    ) # the 0 and one turn the name from Webb, Logan to Logan Webb, with the , as the split
    return df

@st.cache_data 
def load_batters():
    df = get_batter_list()
    df['display_name'] = df.apply(
        lambda r: strip_accents((r['name_first'] + " " + r['name_last']).title()) + " (" + r['team'] + ")",
        axis=1
    )
    return df

pitchers = load_pitchers()
batters = load_batters()

#everything above this just grabs the pitchers/batters lists from the functions get_pitcher_list() and formats to be First Last

tab1, tab2, tab3 = st.tabs(["Prompt", "Coming Soon", "About Me"])

with tab1:
    st.header("How has a player performed recently?")

    player_type = st.radio("Player type", ["Pitcher", "Hitter"], horizontal=True)

    if player_type == "Pitcher":
        selected_name = st.selectbox("Pitcher", sorted(pitchers['display_name']))
        num_outings = st.number_input("Number of Outings", min_value=1, value=10)

        if st.button("Get stats"):
                player_id = pitchers[pitchers['display_name'] == selected_name]['pitcher'].iloc[0] # first it checks weather every row is equal to Logan Webb (SFG)
                #Pitchers[] keeps only true rows, ['pitcher'] narrows it to just the player id, and iloc[0] unwraps it
                wins, losses, era, actual_outings = get_last_x_outings_by_id(player_id, num_outings)
                if actual_outings == 1:
                    st.write(f"{selected_name} is {wins}-{losses} with a {era} ERA in his last outing.")
                else:
                    st.write(f"{selected_name} is {wins}-{losses} with a {era} ERA in his last {actual_outings} outings.")
    else:
        selected_name = st.selectbox("Hitter", sorted(batters['display_name']))
        num_games = st.number_input("Number of Games", min_value=1, value=10)

        if st.button("Get stats"):
            player_id = batters[batters['display_name'] == selected_name]['batter'].iloc[0]
            hits, at_bats, avg, ops, home_runs, actual_games = get_last_x_games_by_id(player_id, num_games)
            hr_word = "home run" if home_runs == 1 else "home runs"
            games_phrase,was_is = ("last game","was") if actual_games == 1 else (f"last {actual_games} games","is") 
            st.write(f"{selected_name} {was_is} {hits} for {at_bats} ({fmt_rate(avg)}) with a {fmt_rate(ops)} OPS and {home_runs} {hr_word} in his {games_phrase}.")

with tab2:
    st.header("Coming Soon")
    st.write("More features on the way.")

with tab3:
    st.header("About Me")
    st.write("This is the MVP.")