import streamlit as st
from src.queries.pitcher_stats import get_pitcher_list, get_last_x_outings_by_id
from src.queries.batter_stats import get_batter_list, get_last_x_games_by_id

st.set_page_config(page_title="PromptedBaseball", layout="wide")
import unicodedata

def strip_accents(text): #Takes accents off of names
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

def fmt_rate(x): #Formats Stats
    return f"{x:.3f}".lstrip("0")

HITTER_STATS = ["AVG", "OPS", "HR", "H/AB"]
ARM_SLOTS = ["any", "over the top", "high three-quarters", "three-quarters", "sidearm", "submarine"]
PITCH_MIX = ["any", "fastball", "sinker", "changeup", "splitter"]
PITCHER_STYLES = ["any", "ground ball", "strikeout", "fly ball"]
HANDS = ["any", "right", "left"]
OUTS_OPTIONS = ["any outs", "0 outs", "1 out", "2 outs"]
INNING_OPTIONS = ["any inning"] + [str(i) for i in range(1, 10)] + ["extra innings"]
COUNT_OPTIONS = ["any count"] + [f"{b}-{s}" for b in range(4) for s in range(3)]
BASE_ORDER = ["1B", "2B", "3B"]
BASE_NAMES = {"1B": "1st", "2B": "2nd", "3B": "3rd"}
DEFAULT_HITTER = "Nico Hoerner (CHC)"
HARDCODED_SENTENCE = "Nico Hoerner (CHC) has a .318 AVG, .861 OPS in his last 40 plate appearances against right-handed sidearm sinkerball ground ball pitchers with runners in scoring position and 2 outs."

if "stat_ids" not in st.session_state:
    st.session_state.stat_ids = [0, 1]
    st.session_state.next_stat_id = 2
    st.session_state["stat_0"] = "AVG"
    st.session_state["stat_1"] = "OPS"

if "base_combos" not in st.session_state:
    st.session_state.base_pending = []
    st.session_state.base_combos = [("2B",), ("3B",), ("1B", "2B"), ("1B", "3B"), ("2B", "3B"), ("1B", "2B", "3B")]

def add_stat():
    st.session_state.stat_ids.append(st.session_state.next_stat_id)
    st.session_state.next_stat_id += 1

def remove_stat(stat_id):
    st.session_state.stat_ids.remove(stat_id)

def toggle_base(base):
    if base in st.session_state.base_pending:
        st.session_state.base_pending.remove(base)
    else:
        st.session_state.base_pending.append(base)

def add_combo():
    combo = tuple(sorted(st.session_state.base_pending, key=BASE_ORDER.index))
    if combo not in st.session_state.base_combos:
        st.session_state.base_combos.append(combo)
    st.session_state.base_pending = []

def remove_combo(index):
    st.session_state.base_combos.pop(index)

def combo_label(combo):
    if len(combo) == 0:
        return "bases empty"
    if len(combo) == 3:
        return "bases loaded"
    return " & ".join(BASE_NAMES[b] for b in combo)

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
        result_box = st.container(border=True)
        left, right = st.columns(2)

        with left:
            with st.container(border=True):
                st.subheader("1. Who")
                selected_name = st.selectbox("Pitcher", sorted(pitchers['display_name']), label_visibility="collapsed")

        with right:
            with st.container(border=True):
                st.subheader("2. Window")
                num_outings = st.number_input("Number of Outings", min_value=1, value=10)

        with result_box:
            st.caption("RESULT")
            if st.button("Get stats", type="primary", key="pitcher_get_stats"):
                player_id = pitchers[pitchers['display_name'] == selected_name]['pitcher'].iloc[0] # first it checks weather every row is equal to Logan Webb (SFG)
                #Pitchers[] keeps only true rows, ['pitcher'] narrows it to just the player id, and iloc[0] unwraps it
                wins, losses, era, actual_outings = get_last_x_outings_by_id(player_id, num_outings)
                if actual_outings == 1:
                    st.markdown(f"### {selected_name} is {wins}-{losses} with a {era} ERA in his last outing.")
                else:
                    st.markdown(f"### {selected_name} is {wins}-{losses} with a {era} ERA in his last {actual_outings} outings.")
    else:
        with st.container(border=True):
            st.caption("RESULT")
            st.markdown(f"### {HARDCODED_SENTENCE}")
            st.caption("Sample sentence. The numbers are placeholders until the backend is built.")
            st.button("Get stats", type="primary", key="hitter_get_stats")

        row1_left, row1_right = st.columns(2)
        row2_left, row2_right = st.columns(2)

        with row1_left:
            with st.container(border=True):
                st.subheader("1. Who")
                batter_side = st.radio("Batter side", ["Hitter", "Hitting team"], horizontal=True, label_visibility="collapsed")
                if batter_side == "Hitter":
                    hitter_names = sorted(batters['display_name'])
                    default_index = hitter_names.index(DEFAULT_HITTER) if DEFAULT_HITTER in hitter_names else 0
                    selected_name = st.selectbox("Hitter", hitter_names, index=default_index, label_visibility="collapsed")
                else:
                    selected_name = st.selectbox("Hitting team", sorted(batters['team'].unique()), label_visibility="collapsed")
                batter_hand = st.selectbox("Batter handedness", HANDS)

        with row1_right:
            with st.container(border=True):
                st.subheader("2. What to show")
                st.markdown("**Stats**")
                stat_cols = st.columns([1.6, 0.6] * len(st.session_state.stat_ids) + [1.2, 1], vertical_alignment="center")
                for i, stat_id in enumerate(st.session_state.stat_ids):
                    stat_cols[2 * i].selectbox("Stat", HITTER_STATS, key=f"stat_{stat_id}", label_visibility="collapsed")
                    stat_cols[2 * i + 1].button("✕", key=f"remove_{stat_id}", on_click=remove_stat, args=(stat_id,))
                stat_cols[-2].button("+ Add", on_click=add_stat)
                num_pa = st.number_input("Last plate appearances", min_value=1, value=40)

        with row2_left:
            with st.container(border=True):
                st.subheader("3. Game situation")
                s1, s2, s3 = st.columns(3)
                outs = s1.selectbox("Outs", OUTS_OPTIONS, index=OUTS_OPTIONS.index("2 outs"))
                inning = s2.selectbox("Inning", INNING_OPTIONS)
                count = s3.selectbox("Count", COUNT_OPTIONS)

                st.markdown("**Runners on base**")
                diamond_col, combo_col = st.columns([1.2, 1.5])
                with diamond_col:
                    top = st.columns(3)
                    mid = st.columns(3)
                    bot = st.columns(3)
                    for col, base in ((top[1], "2B"), (mid[0], "3B"), (mid[2], "1B")):
                        col.button(
                            BASE_NAMES[base],
                            key=f"base_{base}",
                            type="primary" if base in st.session_state.base_pending else "secondary",
                            on_click=toggle_base,
                            args=(base,),
                            use_container_width=True
                        )
                    bot[1].button("Home", key="base_home", disabled=True, use_container_width=True)
                    st.button("Add combination", on_click=add_combo)
                with combo_col:
                    combo_cols = st.columns(2)
                    for i, combo in enumerate(st.session_state.base_combos):
                        combo_cols[i % 2].button(f"{combo_label(combo)} ✕", key=f"combo_{i}", on_click=remove_combo, args=(i,), use_container_width=True)

        with row2_right:
            with st.container(border=True):
                st.subheader("4. Pitcher faced")
                pitcher_side = st.radio("Pitcher side", ["Pitcher", "Pitching team"], horizontal=True, label_visibility="collapsed")
                if pitcher_side == "Pitcher":
                    opponent = st.selectbox("Opposing pitcher", ["Any pitcher"] + sorted(pitchers['display_name']), label_visibility="collapsed")
                else:
                    opponent = st.selectbox("Opposing team", ["Any team"] + sorted(pitchers['team'].unique()), label_visibility="collapsed")
                q1, q2 = st.columns(2)
                arm_slot = q1.selectbox("Arm slot", ARM_SLOTS, index=ARM_SLOTS.index("sidearm"))
                pitch_mix = q2.selectbox("Pitch mix", PITCH_MIX, index=PITCH_MIX.index("sinker"))
                pitcher_style = q1.selectbox("Style", PITCHER_STYLES, index=PITCHER_STYLES.index("ground ball"))
                pitcher_hand = q2.selectbox("Pitcher handedness", HANDS, index=HANDS.index("right"))

with tab2:
    st.header("Coming Soon")
    st.write("More features on the way.")

with tab3:
    st.header("About Me")
    st.write("This is the MVP.")