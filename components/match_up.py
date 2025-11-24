import streamlit as st
import pandas as pd


st.title("Pokemon Project!")

df = pd.read_csv("data/cleaned_pokemon.csv")

poke1 = st.selectbox("Choose Pokémon 1:", df['name'])
poke2 = st.selectbox("Choose Pokémon 2:", df['name'])
# selecting both pokemons up here^

p1 = df[df['name'] == poke1].iloc[0]
p2 = df[df['name'] == poke2].iloc[0]
# filter the df to get the full row of the pokemon we selected

st.subheader("Pokémon Stats Comparison")
stats = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### {p1['name']}")
    st.write(p1[stats])

with col2:
    st.markdown(f"### {p2['name']}")
    st.write(p2[stats])

# displays both pokemons side by side in the write stats^


def calculate_total_stats(pokemon):
    return sum([pokemon[stat] for stat in stats])
# this calculates the total stats of the pokemon by adding them up
# i.e  HP + Attack + Defense + sp_attack + sp_defense + Speed.

p1_total = calculate_total_stats(p1)
p2_total = calculate_total_stats(p2)
# gets both calculations of the pokemons^

type1_col = [col for col in df.columns if 'type' in col.lower() and '1' in col][-1]
type2_col = [col for col in df.columns if 'type' in col.lower() and '2' in col][-1]

type1 = str(p1[type1_col]).lower()

type2_value = p2[type2_col]
type2 = str(type2_value).lower() if pd.notna(type2_value) else None # if no type then we standardise the type

# extracts and converts the pokemon's to lowercase for easier transforming

p1_eff = p2.get(f"against_{type1}", 1)
p2_eff = p1.get(f"against_{type2}", 1)

p1_score = p1_total * p2_eff
p2_score = p2_total * p1_eff

# then it calculates the overall effectiveness by the total stats

st.subheader("Battle Prediction")

if p1_score > p2_score:
    st.success(f"{p1['name']} is more likely to win")
elif p2_score > p1_score:
    st.success(f"{p2['name']} is more likely to win")
else:
    st.info("It's a tie! ⚔️")

# showcase the winner in an if statement

st.write(f"**{p1['name']} Score:** {round(p1_score,2)}")
st.write(f"**{p2['name']} Score:** {round(p2_score,2)}")

with st.expander("Show Calculation Details"):
    st.write(f"{p1['name']} Total Stats = {p1_total}, Type Effectiveness = {round(p2_eff,2)}")
    st.write(f"{p2['name']} Total Stats = {p2_total}, Type Effectiveness = {round(p1_eff,2)}")
