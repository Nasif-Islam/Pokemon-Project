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

# 🎯 Initialize the board only once using session_state
if "board" not in st.session_state:
    grid_pokemon = df.sample(grid_size * grid_size)
    board = []
    for _, row in grid_pokemon.iterrows():
        type1 = str(row.get(type1_col, "")).lower()
        is_electric = (type1 == 'electric')
        
        voltorb_prob = (
            0.25 +
            (0.2 if is_electric else 0) +
            (0.2 if row.get('legendary', False) else 0) -
            (row['speed'] / 300)
        )

        is_voltorb = random.random() < voltorb_prob

        board.append({
            "name": row["name"],
            "score": int(row["attack"] / 30) if not is_voltorb else 0,
            "voltorb": is_voltorb,
            "revealed": False
        })

    st.session_state.board = np.array(board).reshape(grid_size, grid_size)

board = st.session_state.board

# 🟩 Display grid with buttons
for i in range(grid_size):
    cols = st.columns(grid_size)
    for j in range(grid_size):
        tile = board[i][j]
        if tile["revealed"]:
            if tile["voltorb"]:
                cols[j].button("💥 Voltorb!", key=f"{i}{j}")
            else:
                cols[j].button(f"{tile['score']} ⭐", key=f"{i}{j}")
        else:
            if cols[j].button("❓", key=f"{i}{j}"):
                st.session_state.board[i][j]["revealed"] = True
                st.rerun()

# 🧮 Score display
score = sum(tile["score"] for row in board for tile in row if tile["revealed"] and not tile["voltorb"])
st.subheader(f"Current Score: ⭐ {score}")

# 🔄 Restart game
if st.button("New Game 🔁"):
    del st.session_state.board
    st.rerun()
