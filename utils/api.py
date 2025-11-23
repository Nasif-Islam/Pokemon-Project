import requests as req

API_URL = "https://pokeapi.co/api/v2/pokemon/"
fallback_img = "data/pokeball.png"


def fetch_pokemon_data(pokemon_name):
    response = req.get(f"{API_URL}{pokemon_name.lower()}")
    if response.status_code == 200:
        return response.json()
    else:
        # st.error("Failed to fetch data from PokéAPI.")
        return None


def fetch_front_sprite(pokemon_name):
    data = fetch_pokemon_data(pokemon_name)
    if data:
        return data["sprites"]["front_default"]
    else:
        return fallback_img


def fetch_back_sprite(pokemon_name):
    data = fetch_pokemon_data(pokemon_name)
    if data:
        return data["sprites"]["back_default"]
    else:
        return fallback_img


# prevent side effects on import; only run test code when executed directly
if __name__ == "__main__":
    pokemon_data = fetch_pokemon_data("Pikachu")
    if pokemon_data:
        print(pokemon_data["sprites"]["front_default"])
