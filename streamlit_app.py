import streamlit as st
from src.queries.pitcher_stats import get_pitcher_list, get_last_x_outings_by_id

st.set_page_config(page_title="PromptedBaseball")
import unicodedata

def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

@st.cache_data
def load_pitchers():
    df = get_pitcher_list()
    df['display_name'] = df.apply(
        lambda r: strip_accents(r['player_name'].split(", ")[1] + " " + r['player_name'].split(", ")[0]) + " (" + r['team'] + ")",
        axis=1
    )
    return df

pitchers = load_pitchers()

tab1, tab2, tab3 = st.tabs(["Prompt", "Coming Soon", "About Me"])

with tab1:
    st.header("How has a pitcher performed recently?")

    selected_name = st.selectbox("Pitcher", sorted(pitchers['display_name']))
    num_outings = st.number_input("Number of Outings", min_value=1, value=10)

    if st.button("Get stats"):
        player_id = pitchers[pitchers['display_name'] == selected_name]['pitcher'].iloc[0]
        wins, losses, era, actual_outings = get_last_x_outings_by_id(player_id, num_outings)
        st.write(f"{selected_name} is {wins}-{losses} with a {era} ERA in his last {actual_outings} outings.")

with tab2:
    st.header("Coming Soon")
    st.write("More features on the way.")

with tab3:
    st.header("About Me")
    st.write("This is the MVP.")
