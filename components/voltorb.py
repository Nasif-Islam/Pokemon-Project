import streamlit as st
import pandas as pd
import random
import numpy as np

st.title("Pokémon Voltorb Flip Game")

# Load data
df = pd.read_csv("data/cleaned_pokemon.csv")

with st.expander("How to Play"):
    st.write("""
    - Click tiles to flip them.
    - If you reveal a Voltorb 💥, you lose :(
    - Try to collect as many points ⭐ as possible.
    - Legendary and Electric Pokémon have higher Voltorb risk.
    - The score will be totalled below!
    - Good luck!
    """)

type1_col = [col for col in df.columns if 'type' in col.lower() and '1' in col.lower()][0]
type2_col = [col for col in df.columns if 'type' in col.lower() and '2' in col.lower()][0]

grid_size = 5

grid_pokemon = df.sample(grid_size * grid_size)
# gets 25 pokemons randomly

# make the game
board = []
for _, row in grid_pokemon.iterrows():
    type1 = str(row.get(type1_col, "").lower())
