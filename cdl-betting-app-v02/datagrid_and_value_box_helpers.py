
import pandas as pd

# Major 3 Qualifiers Start Date (String)
start_date = '2024-04-12' 

# Function to create dataframe of series results for user-selected team
def build_series_res_datagrid(series_score_diffs_input: pd.DataFrame, team_input: str):

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
def build_kills_datagrid(
        cdlDF_input: pd.DataFrame, team_input: str, gamemode_input: str
    ):
    cdlDF_input = \
        cdlDF_input[(cdlDF_input["team"] == team_input) & 
                    (cdlDF_input["gamemode"] == gamemode_input)] \
            [["player", "map_name", "kills", 
              "deaths", "score_diff", "opp_abbr"]] \
        .reset_index(drop=True) \
        .rename(columns = {
            "player": "Player", 
            "map_name": "Map", 
            "kills": "Kills", 
            "deaths": "Deaths",
            "score_diff": "Score Differential", 
            "opp_abbr": "Opponent"}
        )
    
    return cdlDF_input

# Function to compute Current Mode or Map/Mode Win Streak
# Function to compute Map H2H Win - Loss Record for Map H2H Value Box
# Function to compute Map H2H Win - Loss Record for Map H2H Value Box
def compute_win_streak(
          cdlDF_input: pd.DataFrame, team_input: str, 
          gamemode_input: str, map_input = "All"
):
    # Get relevant columns and drop duplicates
    queried_df = cdlDF_input[
        ["match_id", "match_date", "team", "gamemode", "map_name", "map_result"]
    ] \
     .drop_duplicates()
    # Filter queried df by team, map, and mode
    if map_input == "All":
        queried_df = queried_df[
            (queried_df["team"] == team_input) &
            (queried_df["gamemode"] == gamemode_input)
        ]
    else:
        queried_df = queried_df[
            (queried_df["team"] == team_input) &
            (queried_df["gamemode"] == gamemode_input) &
            (queried_df["map_name"] == map_input)
        ]
    
    # If dataframe is empty, return 0
    if queried_df.empty:
        return 0
    
    # Sort queried_df by date descending & reset index
    queried_df = queried_df.sort_values("match_date", ascending = False) \
        .reset_index(drop=True)
    
    # Replace all losses with a -1
    queried_df = queried_df.replace(0, -1)
    
    # Else if dataframe contains only one row, return the map result
    if len(queried_df) == 1:
        return queried_df.iloc[0, 5]
    
    # Get most recent result
    win_or_loss = queried_df.iloc[0, 5]

    # Initialize streak
    streak = queried_df.iloc[0, 5]

    # Initialize iterator
    i = 1

    # Loop through queried_df, continuing to update win streak until either
    # we loop through the whole dataframe, or the win streak ends
    while i < len(queried_df):
        if queried_df.iloc[i, 5] != win_or_loss:
            break
        else:
            streak += queried_df.iloc[i, 5]
        # print(f"Index: {i} Map Result: {queried_df.iloc[i, 5]} Updated Streak: {streak} Max Index: {len(queried_df)}")
        i += 1
    
    return streak

# Function to compute Map H2H Win - Loss Record for Map H2H Value Box
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
    
# Function to compute Series H2H Win - Loss Record for Series H2H Value Box
def compute_h2h_series_record(cdlDF_input: pd.DataFrame, team_x: str, team_y: str):
        queried_df = cdlDF_input[[
                "match_id", "match_date", "team", "opp", "series_result"
        ]] \
                [
                        (cdlDF_input["match_date"] >= start_date) &
                        (cdlDF_input["team"] == team_x) &
                        (cdlDF_input["opp"] == team_y)
                ] \
                .drop_duplicates()
        if queried_df.empty:
                return "0 - 0"
        else:
                wins = queried_df['series_result'].sum()
                losses = len(queried_df['series_result'])
                return f"{wins} - {losses}"
    