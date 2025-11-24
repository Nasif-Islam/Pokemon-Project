import pandas as pd
import streamlit as st
import plotly.express as px
from utils.api import fetch_back_sprite, fetch_pokemon_data, fetch_front_sprite
from utils.type_utils import type_effectiveness

# TODO refactor into separate files

# import data
poke_data = pd.read_csv("data/cleaned_pokemon.csv")


# set up streamlit
# st.title("PokéBoard")
# st.subheader("An interactive Pokédex data explorer")
# st.set_page_config(page_title="PokéBoard", layout="centered")
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())


for col in ["hp", "attack", "defense", "sp_attack", "sp_defense", "speed"]:
    # add normalised columns
    poke_data[f"{col}_norm"] = normalize(poke_data[col])

normalise = False
fallback_img = "data/pokeball.png"

eng_pokemon_names = poke_data["name"].tolist()
ger_pokemon_names = poke_data["german_name"].tolist()
jpn_pokemon_names = poke_data["japanese_name"].tolist()

language_data = {
    "English": {"name_list": eng_pokemon_names, "column": "name"},
    "Deutsch": {"name_list": ger_pokemon_names, "column": "german_name"},
    "日本語": {"name_list": jpn_pokemon_names, "column": "japanese_name"},
}

type_list = poke_data["type_1"].unique().tolist()
type_list.extend(poke_data["type_2"].unique().tolist())
type_list = list(set(type_list))


stats_list = [
    "hp",
    "attack",
    "defense",
    "sp_attack",
    "sp_defense",
    "speed",
    "type_1",
    "type_2",
    "height_m",
    "weight_kg",
]


# sidebar
st.sidebar.title("Settings")
normalise = st.sidebar.checkbox("Normalise stats", value=False)
# language
language = st.sidebar.selectbox(
    "Select language", ["English", "Deutsch", "日本語"], index=0
)


# plotly radar
def radar_chart(df, selected_pokemon_name):
    pokemon = df[
        df[language_data[language]["column"]] == selected_pokemon_name
    ]
    categories = [
        f"hp{'' if not normalise else '_norm'}",
        f"attack{'' if not normalise else '_norm'}",
        f"defense{'' if not normalise else '_norm'}",
        f"sp_attack{'' if not normalise else '_norm'}",
        f"sp_defense{'' if not normalise else '_norm'}",
        f"speed{'' if not normalise else '_norm'}",
    ]
    values = [pokemon[cat].iloc[0] for cat in categories]

    fig = px.line_polar(
        r=values,
        theta=categories,
        line_close=True,
        color_discrete_sequence=["red"],
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=False,  # hide radial axis
                showline=False,
                # showticklabels=False,
                showgrid=False,
            ),
            angularaxis=dict(
                # visible=False,  # hide angular axis
                showline=False,
                # showticklabels=False,
                showgrid=False,
            ),
            bgcolor="white",  # background
        ),
        showlegend=False,
    )
    fig.update_traces(fill="toself", fillcolor="rgba(255,0,0,0.3)")
    return fig


# set default pokemon to pikachu
if st.session_state.get("first_run", True):
    st.session_state["first_run"] = False
    st.session_state["selected_pokemon_idx"] = 32

# stateful pokemon selector
stored_idx = st.session_state.get("selected_pokemon_idx", poke_data.index[0])
try:
    selectbox_pos = int(poke_data.index.get_loc(stored_idx))  # type: ignore
except Exception:
    # fallback to first position if stored index not found
    selectbox_pos = 0


selected_name = st.session_state.get("selected_pokemon_name_widget")

if selected_name is not None:
    matched = poke_data[
        poke_data[language_data[language]["column"]] == selected_name
    ]
    if not matched.empty:
        new_idx = matched.index[0]
        st.session_state["selected_pokemon_idx"] = new_idx
    else:
        # selected name not found, use old index
        new_idx = st.session_state.get(
            "selected_pokemon_idx", poke_data.index[0]
        )
else:
    new_idx = st.session_state.get("selected_pokemon_idx", poke_data.index[0])

st.session_state.selected_pokemon = poke_data.loc[[new_idx]]
selected_pokemon_index = new_idx
selected_pokemon_name = st.session_state.selected_pokemon[
    language_data[language]["column"]
].iloc[0]

chart = radar_chart(poke_data, selected_pokemon_name)
pokemon_api_data = fetch_pokemon_data(selected_pokemon_name)

tab1, tab2, tab3 = st.tabs(["Overview", "Match-up", "Statistics"])

with tab1:
    st.selectbox(
        "Select a Pokémon",
        language_data[language]["name_list"],
        index=selectbox_pos,
        key="selected_pokemon_name_widget",
    )
    with st.container(horizontal=True):
        with st.container(key="radar"):
            st.plotly_chart(chart)
        with st.container(key="sprites-and-info"):
            with st.container(key="sprites", horizontal=True):
                front_sprite = fetch_front_sprite(
                    st.session_state.selected_pokemon[
                        language_data["English"]["column"]
                    ].iloc[0]
                )
                back_sprite = fetch_back_sprite(
                    st.session_state.selected_pokemon[
                        language_data["English"]["column"]
                    ].iloc[0]
                )
                st.image(
                    front_sprite,
                    width=150,
                    caption="Front Sprite",
                )
                st.image(
                    back_sprite,
                    width=150,
                    caption="Back Sprite",
                )
            with st.container(key="info", horizontal_alignment="center"):
                st.markdown(f"### {selected_pokemon_name} Info")
                info_cols = st.columns([1, 2])
                info_cols[0].markdown("**Height (m):**")
                info_cols[1].markdown(
                    f"{st.session_state.selected_pokemon['height_m'].iloc[0]}"
                )
                info_cols[0].markdown("**Weight (kg):**")
                info_cols[1].markdown(
                    f"{st.session_state.selected_pokemon['weight_kg'].iloc[0]}"
                )
                type1 = st.session_state.selected_pokemon["type_1"].iloc[0]
                type1 = "none" if pd.isna(type1) else type1
                type2 = st.session_state.selected_pokemon["type_2"].iloc[0]
                type2 = "none" if pd.isna(type2) else type2
                info_cols[0].markdown("**Type 1:**")
                info_cols[1].markdown(f"{type1}")
                info_cols[0].markdown("**Type 2:**")
                info_cols[1].markdown(f"{type2}")


with tab2:
    with st.container(key="match-up", horizontal=True):
        with st.container(key="dropdowns", horizontal=True):
            st.selectbox(
                "Select attacker",
                language_data[language]["name_list"],
                key="first_matchup_pokemon_name",
            )

            def swap_pokemon():
                first_name = st.session_state.get(
                    "first_matchup_pokemon_name", None
                )
                second_name = st.session_state.get(
                    "second_matchup_pokemon_name", None
                )
                st.session_state["first_matchup_pokemon_name"] = second_name
                st.session_state["second_matchup_pokemon_name"] = first_name

            st.button("Swap", on_click=swap_pokemon)
            st.selectbox(
                "Select defender",
                language_data[language]["name_list"],
                key="second_matchup_pokemon_name",
            )
            first_pokemon_name = st.session_state.get(
                "first_matchup_pokemon_name", None
            )
            first_pokemon = poke_data[
                poke_data[language_data[language]["column"]]
                == first_pokemon_name
            ]
            second_pokemon_name = st.session_state.get(
                "second_matchup_pokemon_name", None
            )
            second_pokemon = poke_data[
                poke_data[language_data[language]["column"]]
                == second_pokemon_name
            ]

        # when both pokemon are selected show a coloured stat comparison
    with st.container(key="stat-selector"):
        stats = [
            "hp",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "speed",
        ]
        stats = st.multiselect(
            "select stats to compare", stats_list, default=stats_list
        )
    with st.container(key="stat-comparison"):
        if not first_pokemon.empty and not second_pokemon.empty:
            # TODO add images
            st.markdown(
                f"### Match-up: {first_pokemon_name} attacking {second_pokemon_name}"
            )

            header_cols = st.columns([1, 1, 1])
            header_cols[0].markdown("**Stat**")
            header_cols[1].markdown(f"**{first_pokemon_name}**")
            header_cols[2].markdown(f"**{second_pokemon_name}**")

            for stat in stats:
                stat1 = first_pokemon.iloc[0][stat]
                stat2 = second_pokemon.iloc[0][stat]

                try:
                    # attempt numeric comparison
                    num_stat1 = float(stat1)
                    num_stat2 = float(stat2)
                except Exception:
                    num_stat1 = stat1
                    num_stat2 = stat2

                if isinstance(num_stat1, (int, float)) and isinstance(
                    num_stat2, (int, float)
                ):
                    if num_stat1 > num_stat2:
                        c1, c2 = "green", "red"
                    elif num_stat1 < num_stat2:
                        c1, c2 = "red", "green"
                    else:
                        c1, c2 = "goldenrod", "goldenrod"
                elif stat in ("type_1", "type_2"):
                    stat1 = first_pokemon.iloc[0][stat]
                    stat2 = second_pokemon.iloc[0][stat]
                    stat1 = "none" if pd.isna(stat1) else stat1
                    stat2 = "none" if pd.isna(stat2) else stat2
                    if stat1 in type_list and stat2 in type_list:
                        multiplier = type_effectiveness(stat1, stat2)
                    else:
                        multiplier = 1
                    if multiplier > 1:
                        c1, c2 = "green", "red"
                    elif multiplier < 1:
                        c1, c2 = "red", "green"
                    else:
                        c1, c2 = "goldenrod", "goldenrod"
                else:
                    # fallback: equal is yellow, else black
                    if num_stat1 == num_stat2:
                        c1 = c2 = "goldenrod"
                    else:
                        c1 = c2 = "black"

                row_cols = st.columns([1, 1, 1])
                row_cols[0].markdown(f"`{stat}`")
                row_cols[1].markdown(
                    f"<span style='color:{c1}; font-weight:600'>{stat1}</span>",
                    unsafe_allow_html=True,
                )
                row_cols[2].markdown(
                    f"<span style='color:{c2}; font-weight:600'>{stat2}</span>",
                    unsafe_allow_html=True,
                )

with tab3:
    st.markdown("### Statistics")
