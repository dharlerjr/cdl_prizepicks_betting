
# Import pandas and ListedColormap from matplotllib
import pandas as pd

# Function to compute H2H Win - Loss Record 
def compute_h2h_map_record(
        filtered_cdlDF_input: pd.DataFrame, team_x: str, team_y: str, 
        gamemode_input: str, map_input = "All"
):
    if map_input == "All":
        queried_df = filtered_cdlDF_input \
            [["match_id", "team", "gamemode", "map_result", "opp"]] \
            [(filtered_cdlDF_input["team"] == team_x) & \
                (filtered_cdlDF_input["opp"] == team_y) &
                (filtered_cdlDF_input["gamemode"] == gamemode_input)] \
            .drop_duplicates() \
            .groupby("gamemode", observed = True) \
            .agg(
                wins = ("map_result", lambda x: sum(x)), 
                losses = ("map_result", lambda x: len(x) - sum(x))
                ) \
            .reset_index()
    else:
        queried_df = filtered_cdlDF_input \
            [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
            [(filtered_cdlDF_input["team"] == team_x) & \
                (filtered_cdlDF_input["opp"] == team_y) & 
                (filtered_cdlDF_input["gamemode"] == gamemode_input) & 
                (filtered_cdlDF_input["map_name"] == map_input)] \
            .drop_duplicates() \
            .groupby(["gamemode", "map_name"], observed = True) \
            .agg(
                wins = ("map_result", lambda x: sum(x)), 
                losses = ("map_result", lambda x: len(x) - sum(x))
            ) \
            .reset_index()
        wins = queried_df.loc[0, "wins"]
        losses = queried_df.loc[0, "losses"]
        return f"{wins} - {losses}"