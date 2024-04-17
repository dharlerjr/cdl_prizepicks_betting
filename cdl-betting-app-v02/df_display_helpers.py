
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
def build_kills_scoreboards(
        cdlDF_input: pd.DataFrame, team_input: str, gamemode_input: str
    ):
    cdlDF_input = \
        cdlDF_input[(cdlDF_input["team"] == team_input) & 
                    (cdlDF_input["gamemode"] == gamemode_input)] \
            [["player", "map_name", "kills", 
              "deaths", "team_score", "opp_score", "opp_abbr"]] \
        .reset_index(drop=True) \
        .rename(columns = {
            "player": "Player", 
            "map_name": "Map", 
            "kills": "Kills", 
            "team_score": "Team Score", 
            "opp_score": "Opponent Score", 
            "opp_abbr": "Opponent"}
        )
    
    return cdlDF_input


# Function to compute H2H Win - Loss Record for H2H Value Box
def compute_h2h_map_record(
        cdlDF_input: pd.DataFrame, team_x: str, team_y: str, 
        gamemode_input: str, map_input = "All"
):
    if map_input == "All":
        queried_df = cdlDF_input \
            [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
            [(cdlDF_input["team"] == team_x) & \
                (cdlDF_input["opp"] == team_y) &
                (cdlDF_input["gamemode"] == gamemode_input)] \
            .drop_duplicates() \
            .groupby("gamemode", observed = True) \
            .agg(
                wins = ("map_result", lambda x: sum(x)), 
                losses = ("map_result", lambda x: len(x) - sum(x))
                ) \
            .reset_index()
    else:
        queried_df = cdlDF_input \
            [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
            [(cdlDF_input["team"] == team_x) & \
                (cdlDF_input["opp"] == team_y) & 
                (cdlDF_input["gamemode"] == gamemode_input) & 
                (cdlDF_input["map_name"] == map_input)] \
            .drop_duplicates() \
            .groupby(["gamemode", "map_name"], observed = True) \
            .agg(
                wins = ("map_result", lambda x: sum(x)), 
                losses = ("map_result", lambda x: len(x) - sum(x))
            ) \
            .reset_index()
    if queried_df.empty:
        return "0 - 0"
    else:
        wins = queried_df.loc[0, "wins"]
        losses = queried_df.loc[0, "losses"]
        return f"{wins} - {losses}"