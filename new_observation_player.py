from poke_env.player.random_player import RandomPlayer
from poke_env.environment.abstract_battle import AbstractBattle
from poke_env.player.battle_order import BattleOrder
from poke_env.environment.observation import Observation
from poke_env.environment.observed_pokemon import ObservedPokemon
from poke_env.player import cross_evaluate


import asyncio

class ObservingRandomPlayer(RandomPlayer):
    def choose_move(self, battle: AbstractBattle) -> BattleOrder:
        # Generate observation data
        observation = self.generate_observation(battle)

        # Optionally, you can print the observation to the console or use it in decision making
        print(observation.events)

        # Continue with the random move selection
        return self.choose_random_move(battle)

    def generate_observation(self, battle: AbstractBattle) -> Observation:
        # Extract relevant battle data to form an Observation
        side_conditions = {condition: count for condition, count in battle.side_conditions.items()}
        opponent_side_conditions = {condition: count for condition, count in battle.opponent_side_conditions.items()}
        weather = {battle.weather: 1} if battle.weather else {}


        # Assuming active_pokemon and opponent_active_pokemon are single ObservedPokemon instances for simplicity
        active_pokemon = ObservedPokemon.from_pokemon(battle.active_pokemon)
        opponent_active_pokemon = ObservedPokemon.from_pokemon(battle.opponent_active_pokemon)

        return Observation(
            side_conditions=side_conditions,
            opponent_side_conditions=opponent_side_conditions,
            weather=weather,
            active_pokemon=active_pokemon,
            opponent_active_pokemon=opponent_active_pokemon,
            opponent_team={},  # Similarly, convert opponent's team
            events=[]  # Populate with relevant event data from battle
        )


if __name__ == "__main__":
    random_player = RandomPlayer(battle_format="gen3randombattle")
    observation_player = ObservingRandomPlayer(battle_format="gen3randombattle")
    players = [observation_player, random_player]

    asyncio.get_event_loop().run_until_complete(cross_evaluate(players, n_challenges=1))
