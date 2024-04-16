
import pandas as pd

# Function to create dataframe of series results for user-selected team
def build_series_scoreboards(series_score_diffs_input: pd.DataFrame, team_input: str):

    series_score_diffs_input = series_score_diffs_input \
        [series_score_diffs_input["team"] == team_input] \
        [["map_wins", "map_losses", "opp"]].reset_index(drop=True)

    series_score_diffs_input = series_score_diffs_input.rename(
        columns = {"map_wins": "Map Wins", 
                   "map_losses": "Map Losses", 
                    "opp": "Opponent"}
        )
    return series_score_diffs_input

# Function to create dataframe of kills for user-selected team & gamemode
def build_map_scoreboards(
        cdlDF_input: pd.DataFrame, team_input: str, gamemode_input: str
    ):
    cdlDF_input = \
        cdlDF_input[(cdlDF_input["team"] == team_input) & 
                    (cdlDF_input["gamemode"] == gamemode_input)] \
            [["player", "map_name", "kills", 
              "deaths", "team_score", "opp_score", "opp"]] \
        .reset_index(drop=True) \
        .rename(columns = {
            "player": "Player", 
            "map_name": "Map", 
            "kills": "Kills", 
            "team_score": "Team Score", 
            "opp_score": "Opponent Score", 
            "opp": "Opponent"}
        )
    
    return cdlDF_input