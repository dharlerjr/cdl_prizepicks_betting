
import pandas as pd

# Function to compute date of last match
def compute_last_match(cdlDF_input: pd.DataFrame, team_x: str, team_y: str):
    return cdlDF_input[
        (cdlDF_input['team'] == team_x) & 
        (cdlDF_input['opp'] == team_y)
    ].iloc[-1, 1].strftime("%b %d %Y")

# Function to create dataframe of kills for user-selected team & gamemode
def build_scoreboards(
        cdlDF_input: pd.DataFrame, team_x: str, team_y: str, gamemode_input = "All", map_input = "All"
    ):

    # Get maps to include based on user input
    selected_maps = []
    if map_input == "All":
        selected_maps = sorted(cdlDF_input['map_name'].unique())
    else:
        selected_maps.append(map_input)

    # Create a copy of cdlDF_input
    cdlDF_copy = cdlDF_input.copy()

    # Create a boolean Series indicating rows containing maps within selected_maps
    mask = cdlDF_copy['map_name'].isin(selected_maps)

    # Reindex the boolean Series to match the DataFrame's index
    mask = mask.reindex(cdlDF_copy.index)

    # Filter cdlDF for maps in selected_maps
    cdlDF_copy = cdlDF_copy[mask]

    # Filter for gamemode
    if gamemode_input != "All":
        cdlDF_copy = cdlDF_copy[cdlDF_copy['gamemode'] == gamemode_input]
    
    # Get team_x scoreboards
    team_x_scoreboard = \
        cdlDF_copy[cdlDF_copy["team"] == team_x] \
            [["match_date", "match_id", "gamemode", "map_name", "map_num", 
              "team_abbr", "player", "kills", "deaths", "score_diff", "opp_abbr"]]

    # Get team_y scoreboards
    team_y_scoreboard = \
        cdlDF_copy[(cdlDF_copy["team"] == team_y) & 
                    (cdlDF_copy["opp"] != team_x)] \
            [["match_date", "match_id", "gamemode", "map_name", "map_num", 
              "team_abbr", "player", "kills", "deaths", "score_diff", "opp_abbr"]]
    
    # Combine scoreboards
    scoreboards = pd.concat([team_x_scoreboard, team_y_scoreboard], axis=0)

    # Arrange by match_date, match_id, and map_num for later concatenation
    scoreboards = scoreboards.sort_values(by = ["match_date", "match_id", "map_num"], ascending = [False, False, True]).reset_index(drop=True)

    # Add player data for opposing teams

    # Build dataframe of unique match_ids and opponents
    matches = scoreboards[["match_id", "opp_abbr"]].drop_duplicates().reset_index(drop=True).copy()

    # Initialize opponents dataframe
    opponents = pd.DataFrame()

    # Loop through matches and append player data  
    if gamemode_input != "All":
        for index, row in matches.iterrows():
            opponents = pd.concat([
                opponents, 
                cdlDF_copy[
                    (cdlDF_copy["match_id"] == row["match_id"]) &
                    (cdlDF_copy["team_abbr"] == row["opp_abbr"]) &
                    (cdlDF_copy["gamemode"] == gamemode_input)
                ] \
                    [["match_date", "match_id", "map_num", "player", "kills", 
                    "deaths"]]
            ], 
            axis=0)
    else:
        for index, row in matches.iterrows():
            opponents = pd.concat([
                opponents, 
                cdlDF_copy[
                    (cdlDF_copy["match_id"] == row["match_id"]) &
                    (cdlDF_copy["team_abbr"] == row["opp_abbr"])
                ] \
                    [["match_date", "match_id", "map_num", "player", "kills", 
                    "deaths"]]
            ], 
            axis=0)

    # Arrange by match_date, match_id, and map_num for later concatenation
    opponents = opponents.sort_values(by = ["match_date", "match_id", "map_num"], ascending = [False, False, True]).reset_index(drop=True)

    # Rename opponent columns
    opponents = opponents.rename(columns = {
        "player": "Player ",
        "kills": "Kills ", 
        "deaths": "Deaths ", 
    })

    # # Concatenate scoreboards & opponents 
    scoreboards = pd.concat(
        [
            scoreboards, 
            opponents.drop(["match_date", "match_id", "map_num"], axis = 1).reset_index(drop=True)
        ], 
        axis=1)

    # Drop map_num & match_id
    scoreboards = scoreboards.drop(["map_num", "match_id"], axis = 1)

    # Rename columns 
    scoreboards = scoreboards.rename(columns = {
        "match_date": "Date", 
        "map_name": "Map", 
        "gamemode": "Gamemode",
        "team_abbr": "Team", 
        "player": "Player",
        "kills": "Kills", 
        "deaths": "Deaths", 
        "score_diff": "Margin",
        "opp_abbr": "Opponent"
    })

    # Drop Map column if only one map
    if map_input != "All":
        scoreboards = scoreboards.drop("Map", axis = 1)

    # Drop Gamemode Column if gamemode_input == "All"
    if gamemode_input != "All":
        scoreboards = scoreboards.drop("Gamemode", axis = 1)

    # Convert the 'Date' column to string for display purposes
    scoreboards['Date'] = scoreboards['Date'].astype(str)
    
    return scoreboards

# Function to compute Current Mode or Map/Mode Win Streak
def compute_win_streak(
          cdlDF_input: pd.DataFrame, team_input: str, 
          gamemode_input: str, map_input = "All"
):
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # Get relevant columns and drop duplicates
    queried_df = queried_df[
        ["match_id", "match_date", "team", "gamemode", "map_name", "map_result", "map_num"]
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
    queried_df = queried_df.sort_values(by = ["match_date", "match_id", "map_num"], ascending = [False, False, False] ) \
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
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

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
        
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()
        
    queried_df = queried_df \
        [["match_id", "match_date", "team", "opp", "series_result"]] \
        [(queried_df["team"] == team_x) & (queried_df["opp"] == team_y)] \
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
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # Filter by given inputs
    if map_input == "All":
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input)
        ]
    else:
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input) &
            (queried_df["map_name"] == map_input)
        ]
    
    # Get relevant columns and drop duplicates
    queried_df = queried_df[
        ["match_id", "kills", "gamemode", "map_name"]
    ]

    # If the dataframe is empty, return "Never Played"
    if queried_df.empty:
        return "Never Played", "", "", "", ""
    
    # Compute overs, unders, and hooks
    overs = len(queried_df[queried_df['kills'] > cur_line])
    unders = len(queried_df[queried_df['kills'] < cur_line])
    hooks = len(queried_df[queried_df['kills'] == cur_line])

    # Compute over & under percentages
    over_percentage = int(round((overs / len(queried_df) * 100), 0))
    under_percentage = int(round((unders / len(queried_df) * 100), 0))
    
    # Return recommended bet based on percentages
    if over_percentage >= under_percentage:
        return "Over", str(over_percentage), str(overs), str(unders), str(hooks)
    else:
        return "Under", str(under_percentage), str(overs), str(unders), str(hooks)

# Function to compete O/U streak
def player_over_under_streak(
        cdlDF_input: pd.DataFrame, player_input: str, 
        gamemode_input: str, cur_line: float, map_input = "All"
):
    
    # Create a copy of cdlDF_input
    queried_df = cdlDF_input.copy()

    # Filter by given inputs
    if map_input == "All":
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input)
        ]
    else:
        queried_df = queried_df[
            (queried_df["player"] == player_input) &
            (queried_df["gamemode"] == gamemode_input) &
            (queried_df["map_name"] == map_input)
        ]
    
    # Get relevant columns and drop duplicates
    queried_df = queried_df[
        ["match_date", "kills", "map_num", "match_id"]
    ]

    # If the dataframe is empty, return "Never Played"
    if queried_df.empty:
        return "Never Played", " "
    
    # Sort queried_df by date descending & reset index
    queried_df = queried_df.sort_values(by = ["match_date", "match_id", "map_num"], ascending = [False, False, False] ) \
        .reset_index(drop=True)
    
    # Initialize streak and iterator
    streak = 1
    i = 1

    # Compute starting over_under
    start = queried_df.iloc[0, 1] - cur_line
    if start >= 0:
        start = "Over"
    else:
        start = "Under"

    while i < len(queried_df):
        if start == "Under":
            if queried_df.iloc[i, 1] - cur_line > 0:
                break
            else:
                streak += 1
        else:
            if queried_df.iloc[i, 1] - cur_line < 0:
                break
            else:
                streak +=1
        i += 1

    return start, str(streak)
