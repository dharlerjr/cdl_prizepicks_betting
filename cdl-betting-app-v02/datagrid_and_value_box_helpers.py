
import pandas as pd

from setup.setup import changed_players

# Function to create dataframe of series results for user-selected team
def build_series_res_datagrid(series_score_diffs_input: pd.DataFrame, team_x: str, team_y: str):

    team_x_series = series_score_diffs_input \
        [series_score_diffs_input["team"] == team_x] \
        [["match_date", "match_id", "team_abbr", "map_wins", "map_losses", "opp"]]
    
    team_y_series = series_score_diffs_input \
        [series_score_diffs_input["team"] == team_y] \
        [["match_date", "match_id", "team_abbr", "map_wins", "map_losses", "opp"]]
    
    series_score_diffs_input = pd.concat([team_x_series, team_y_series], axis = 0) \
        .rename(
            columns = {"match_date": "Date",
                       "match_id": "Match ID",
                       "team_abbr": "Team",
                       "map_wins": "Map Wins", 
                       "map_losses": "Map Losses", 
                       "opp": "Opponent"} \
        ) \
        .sort_values(["match_date", "team_abbr"]) \
        .reset_index(drop = True)
    
    return series_score_diffs_input

# Function to create dataframe of kills for user-selected team & gamemode
def build_scoreboards(
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
def compute_win_streak(
          cdlDF_input: pd.DataFrame, team_input: str, 
          gamemode_input: str, map_input = "All"
):
    
    # Create a boolean Series indicating rows containing players from the changed_players list
    mask = cdlDF_input['player'].isin(changed_players)

    # Reindex the boolean Series to match the DataFrame's index
    mask = mask.reindex(cdlDF_input.index)

    # Create a DataFrame without rows containing players from the changed_players list
    queried_df = cdlDF_input[~mask]

    # Get relevant columns and drop duplicates
    queried_df = queried_df[
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
    
    # Create a boolean Series indicating rows containing players from the changed_players list
    mask = cdlDF_input['player'].isin(changed_players)

    # Reindex the boolean Series to match the DataFrame's index
    mask = mask.reindex(cdlDF_input.index)

    # Create a DataFrame without rows containing players from the changed_players list
    queried_df = cdlDF_input[~mask]

    if map_input == "All":
        queried_df = queried_df \
            [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
            [(queried_df["team"] == team_x) & \
                (queried_df["opp"] == team_y) &
                (queried_df["gamemode"] == gamemode_input)] \
            .drop_duplicates() \
            .groupby("gamemode", observed = True) \
            .agg(
                wins = ("map_result", lambda x: sum(x)), 
                losses = ("map_result", lambda x: len(x) - sum(x))
                ) \
            .reset_index()
    else:
        queried_df = queried_df \
            [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
            [(queried_df["team"] == team_x) & \
                (queried_df["opp"] == team_y) & 
                (queried_df["gamemode"] == gamemode_input) & 
                (queried_df["map_name"] == map_input)] \
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
        
        # Create a boolean Series indicating rows containing players from the changed_players list
        mask = cdlDF_input['player'].isin(changed_players)

        # Reindex the boolean Series to match the DataFrame's index
        mask = mask.reindex(cdlDF_input.index)

        # Create a DataFrame without rows containing players from the changed_players list
        queried_df = cdlDF_input[~mask]
        
        queried_df = queried_df[[
                "match_id", "match_date", "team", "opp", "series_result"
        ]] \
                [
                    (queried_df["team"] == team_x) &
                    (queried_df["opp"] == team_y)
                ] \
                .drop_duplicates()
        if queried_df.empty:
                return "0 - 0"
        else:
                wins = queried_df['series_result'].sum()
                losses = len(queried_df['series_result']) - wins
                return f"{wins} - {losses}"
        
# Function to compute player over/under %
def player_over_under_percentage(
        cdlDF_input: pd.DataFrame, player_input: str, 
        gamemode_input: str, cur_line: float, map_input = "All"
):
    # Filter by given inputs
    if map_input == "All":
        queried_df = cdlDF_input[
            (cdlDF_input["player"] == player_input) &
            (cdlDF_input["gamemode"] == gamemode_input)
        ]
    else:
        queried_df = cdlDF_input[
            (cdlDF_input["player"] == player_input) &
            (cdlDF_input["gamemode"] == gamemode_input) &
            (cdlDF_input["map_name"] == map_input)
        ]
    # Get relevant columns and drop duplicates
    queried_df = queried_df[
        ["match_id", "kills", "gamemode", "map_name"]
    ]

    # If the dataframe is empty, return "Never Played"
    if queried_df.empty:
        return "Never Played", "Never Played"

    # Compute over & under percentages
    under_percentage = int(round(((len(queried_df[queried_df['kills'] <= cur_line]) / len(queried_df)) * 100), 0))
    over_percentage = int(round(((len(queried_df[queried_df['kills'] >= cur_line]) / len(queried_df)) * 100), 0))
    
    # Return recommended bet based on percentages
    if over_percentage >= under_percentage:
        return "Over", str(over_percentage)
    else:
        return "Under", str(under_percentage)
    