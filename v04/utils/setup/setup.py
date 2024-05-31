# Import pandas, numpy, and datetime
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np

# Import psycopg2 
import psycopg2

# Import db password from config
from utils.setup.config import db_password

# List of players that have been dropped
dropped_players = [
    "Afro", "Arcitys", "Purj", "Cammy", "Capsidal", "EriKBooM", 
    "GodRx", "iLLeY", "JurNii", "Owakening", "SlasheR", "Vivid", 
    "Assault", "Seany", "Asim"
]

# Dictionary of players who changed teams
changed_players = {
    "ReeaL": "CAR", 
    "Standy": "LV"
}

# Dictionary of team abbreviations by team name
team_abbrs = {
    "Atlanta FaZe": "ATL",
    "Boston Breach": "BOS",
    "Carolina Royal Ravens": "CAR", 
    "Las Vegas Legion": "LV",
    "Los Angeles Guerrillas": "LAG", 
    "Los Angeles Thieves": "LAT", 
    "Miami Heretics": "MIA", 
    "Minnesota ROKKR": "MIN", 
    "New York Subliners": "NYSL",
    "OpTic Texas": "TX", 
    "Seattle Surge": "SEA", 
    "Toronto Ultra": "TOR"
}

# Dictionary of team names by team abbreviation
team_names = {
    "ATL": "Atlanta FaZe",
    "BOS": "Boston Breach",
    "CAR": "Carolina Royal Ravens",
    "LV": "Las Vegas Legion", 
    "LAG": "Los Angeles Guerrillas", 
    "LAT": "Los Angeles Thieves", 
    "MIA": "Miami Heretics", 
    "MIN": "Minnesota ROKKR", 
    "NYSL": "New York Subliners", 
    "TX": "OpTic Texas", 
    "SEA": "Seattle Surge", 
    "TOR": "Toronto Ultra"
}

# Hardpoint Maps Excluded from Maps 1 - 3 Dataframe Computation
removed_hp_maps = ['Skidrow', 'Terminal']

# Function to load and clean cdl data and return as pandas dataframe
def load_and_clean_cdl_data():

    # Connect to AWS Database
    conn = psycopg2.connect(
        database = "postgres", 
        user = "postgres", 
        password = db_password, 
        host = "cdl-data-mw-three.ct40oheubil2.us-west-1.rds.amazonaws.com",
        port = "5432"
    )

    # Load data into a pandas dataframe
    cdlDF = sqlio.read_sql_query("SELECT * FROM cdl_data", conn)
    cdlDF

    # Close the connection
    conn.close()

    # Drop unnecessary columns
    cdlDF.drop(["match_day", "deaths", "kd", "plus_minus", "dmg", "series_result"], axis=1)

    # Correct Minnesota ROKKR team name
    cdlDF = cdlDF.replace("Minnesota RØKKR", "Minnesota ROKKR")

    # Add Map Win/Loss column 
    cdlDF['map_wl'] = ["W" if x == 1 else "L" for x in cdlDF['map_result']]

    # Add team abbreviations, and icons

    # Teams
    teams = cdlDF.sort_values(by = ['team']).team.unique()

    # Team Abbreviations
    team_abbrs = [
        "ATL", "BOS", "CAR", "LV", "LAG", "LAT",
        "MIA", "MIN", "NYSL", "TX", "SEA", "TOR"
        ]

    # Team Icons
    team_icons = np.array([team.split()[-1] for team in teams])
    team_icons[9] = "OpTic"

    team_abbrs_icons_df = pd.DataFrame({
        "team": teams, 
        "team_abbr": team_abbrs, 
        "team_icon": team_icons
    })

    # Left join cdlDF & team_abbrs_icons_df
    cdlDF = pd.merge(cdlDF, team_abbrs_icons_df, on = 'team', how = 'left')

    # Get Opponents, Match Scores, and Score Differentials

    # Convert 'player' column to lowercase
    cdlDF['player_lower'] = cdlDF['player'].str.lower()

    # Sort DataFrame by specified columns
    cdlDF = cdlDF.sort_values(by=['match_date', 'match_id', 'map_num', 'team', 'player_lower'])
    cdlDF.reset_index(drop=True, inplace=True)

    # Create DataFrame containing opponent information
    opps = cdlDF.sort_values(by=['match_date', 'match_id', 'map_num', 'team', 'player_lower'], ascending=[True, True, True, False, True]) \
                [['team', 'team_abbr', 'team_score']] \
                .rename(columns={'team': 'opp', 'team_abbr': 'opp_abbr', 'team_score': 'opp_score'})
    opps.reset_index(drop=True, inplace=True)

    # Merge opponent DataFrame with original DataFrame
    cdlDF = pd.concat([cdlDF, opps], axis=1)

    # Calculate total score and score differential
    cdlDF['total_score'] = cdlDF['team_score'] + cdlDF['opp_score']
    cdlDF['score_diff'] = cdlDF['team_score'] - cdlDF['opp_score']

    # Drop the 'player_lower' column
    cdlDF = cdlDF.drop(columns=['player_lower'])
    
    # Create a dummy variable for x aesthetic (just an index)
    cdlDF['dummy_x'] = 0

    # Reorder map_wl factor levels
    cdlDF['map_wl'] = pd.Categorical(cdlDF['map_wl'], categories = ['W', 'L'])

    # Reorder gamemode factor levels
    cdlDF['gamemode'] = \
        pd.Categorical(cdlDF['gamemode'], categories = ['Hardpoint', 'Search & Destroy', 'Control'])
    
    # Convert match_date column to datetime
    cdlDF["match_date"] = pd.to_datetime(cdlDF['match_date'])

    # Change FeLo & Lynz player names to match PrizePicks
    cdlDF.loc[cdlDF['player'] == 'FelonY', 'player'] = 'FeLo'
    cdlDF.loc[cdlDF['player'] == 'Lyynnz', 'player'] = 'Lynz'
    
    return cdlDF

# Build dataframe of series scores & differentials
def build_series_summaries(cdlDF_input):
    series_score_diffs = \
        cdlDF_input[["match_id", "match_date", "team", "team_icon", "map_num", "gamemode", "map_result"]] \
        .drop_duplicates() \
        .groupby(["match_id", "team", "team_icon"], observed = True) \
        .agg(
            map_wins = ("map_result", lambda x: sum(x)), 
            map_losses = ("map_result", lambda x: len(x) - sum(x)), 
        ) \
        .reset_index().copy()

    # Get score differentials
    series_score_diffs["series_score_diff"] = \
        series_score_diffs["map_wins"] - series_score_diffs["map_losses"]
    
    # Add match_date column back in
    series_score_diffs = pd.merge(
        series_score_diffs, 
        cdlDF_input[["match_date", "match_id"]].drop_duplicates(),
        how = "left", 
        on = "match_id"
    )

    # Arrange by match_date, match_id, and team & reset index
    series_score_diffs = series_score_diffs.sort_values(
        by = ['match_date', 'match_id', 'team'], ascending = [True, True, True]
        ).reset_index(drop=True)
    
    # Get opponents
    opps = series_score_diffs.sort_values(by = ['match_date', 'match_id', 'team'], ascending = [True, True, False]) \
        [['team_icon']] \
        .rename(columns = {"team_icon": "opp"}) \
        .reset_index(drop=True) 

    opps

    # Bind series_score_diffs & opps
    series_score_diffs = pd.concat([series_score_diffs, opps], axis=1)

    # Return series_score_diffs
    return series_score_diffs

# Function to filter maps from cdlDF
def filter_maps(cdlDF_input):
        
    # Remove map & mode combos
    cdlDF_input = \
        cdlDF_input[
            ~((cdlDF_input['gamemode'] == 'Hardpoint') & (cdlDF_input['map_name'] == 'Invasion')) &
            ~((cdlDF_input['gamemode'] == 'Hardpoint') & (cdlDF_input['map_name'] == 'Skidrow')) &
            ~((cdlDF_input['gamemode'] == 'Hardpoint') & (cdlDF_input['map_name'] == 'Terminal')) &
            ~((cdlDF_input['gamemode'] == 'Search & Destroy') & (cdlDF_input['map_name'] == 'Skidrow')) &
            ~((cdlDF_input['gamemode'] == 'Search & Destroy') & (cdlDF_input['map_name'] == 'Terminal')) 
        ].reset_index(drop = True)
    
    return cdlDF_input

# Function to create a pandas dataframe of team summaries
def build_team_summaries(cdlDF_input: pd.DataFrame): 

    # Create a copy of cdlDF_input to avoid mutating the original
    queried_df = cdlDF_input.copy()

    # Team Summaries by Map & Mode
    team_summaries_DF_top = queried_df \
        [["match_id", "team", "team_icon", "map_name", "gamemode", "map_result"]] \
        .drop_duplicates() \
        .groupby(["team", "team_icon", "gamemode", "map_name"], observed = True) \
        .agg(
            wins = ("map_result", lambda x: sum(x)), 
            losses = ("map_result", lambda x: len(x) - sum(x)), 
            total = ("map_result", lambda x: len(x)), 
            win_percentage = ("map_result", lambda x: round(sum(x) / len(x), 2))
        ) \
        .reset_index()

    # Some teams have not played every map & mode combination 
    # So, we will add those combinations back in manually
    map_and_mode_combos = queried_df[["gamemode", "map_name"]].drop_duplicates().sort_values(["gamemode", "map_name"]).reset_index(drop = True)
    all_combinations = pd.DataFrame(
        [(team, gamemode, map_name) for team in sorted(queried_df['team'].unique()) for _, (gamemode, map_name) in map_and_mode_combos.iterrows()], 
        columns = ['team', 'gamemode', 'map_name']
    )
    team_summaries_DF_top = pd.merge(
        team_summaries_DF_top, 
        all_combinations, 
        on = ['team', 'gamemode', 'map_name'], 
        how = "right"
    ).fillna(0)

    # Set datatypes
    team_summaries_DF_top['wins'] = team_summaries_DF_top['wins'].astype('int64')
    team_summaries_DF_top['losses'] = team_summaries_DF_top['losses'].astype('int64')
    team_summaries_DF_top['total'] = team_summaries_DF_top['total'].astype('int64')
    team_summaries_DF_top['win_percentage'] = team_summaries_DF_top['win_percentage'].astype('float64')
    
    # Team Summaries by Mode only
    team_summaries_DF_bottom = \
        queried_df[["match_id", "team", "team_icon", "map_name", "gamemode", "map_result"]] \
        .drop_duplicates() \
        .groupby(["team", "team_icon", "gamemode"], observed = True) \
        .agg(
            wins = ("map_result", lambda x: sum(x)), 
            losses = ("map_result", lambda x: len(x) - sum(x)), 
            total = ("map_result", lambda x: len(x)), 
            win_percentage = ("map_result", lambda x: round(sum(x) / len(x), 2))
        ) \
        .reset_index()
    
    # Insert map_name column into team_summaries_DF_bottom
    # for stacking
    team_summaries_DF_bottom["map_name"] = "Overall"
    position = 3
    team_summaries_DF_bottom.insert(position, "map_name", team_summaries_DF_bottom.pop("map_name"))

    # Concatenate the two DataFrames vertically
    team_summaries_DF = pd.concat([team_summaries_DF_top, team_summaries_DF_bottom])

    # Reset the index of the stacked DataFrame
    team_summaries_DF.reset_index(drop = True, inplace = True)

    # Reorder gamemode factor levels
    team_summaries_DF['gamemode'] = \
        pd.Categorical(team_summaries_DF['gamemode'], categories = ['Hardpoint', 'Search & Destroy', 'Control'])

    # Reorder map_name factor levels
    team_summaries_DF['map_name'] = \
        pd.Categorical(
            team_summaries_DF['map_name'], 
            categories = ['6 Star', 'Highrise', 'Invasion', 'Karachi', \
                          'Rio', 'Sub Base', 'Vista', 'Overall'])
    
    return team_summaries_DF

# Funciton to build rosters AFTER players have been filtered
def build_rosters(cdlDF_input: pd.DataFrame):
    
    # Create a copy of cdlDF_input to avoid mutating the original
    queried_df = cdlDF_input.copy()

    # Build rosters
    rostersDF = queried_df[["player", "team", "team_abbr"]].drop_duplicates().sort_values(by = ["team", "player"], key = lambda x: x.str.lower())

    # Remove dropped players, excluding players who switched teams
    rostersDF = rostersDF[~rostersDF['player'].isin(dropped_players)]

    # Filter for players who changed teams
    for player, old_team in changed_players.items():
        rostersDF = rostersDF[~((rostersDF['player'] == player) & (rostersDF['team_abbr'] == old_team))]

    # Reset index & return
    rostersDF = rostersDF.reset_index(drop=True)
    return rostersDF

# Build initial player props for app.py
def build_intial_props(rostersDF_input):

    # Create a copy of rostersDF_input to avoid mutating the original
    queried_df = rostersDF_input.copy()

    # Initialize dataframe and build columns
    initial_player_props = pd.DataFrame()
    initial_player_props["player"] = queried_df["player"]
    initial_player_props["team"] = queried_df["team"]
    initial_player_props["team_abbr"] = queried_df["team_abbr"]
    initial_player_props["prop"] = 1
    initial_player_props["line"] = 22.0

    # Add more rows for props 2, 3, & 0
    initial_player_props = pd.concat([initial_player_props, initial_player_props, 
                                      initial_player_props, initial_player_props])
    initial_player_props = initial_player_props.reset_index(drop = True)

    # Add props 2, 3 & 0 and arbitrary lines
    initial_player_props.iloc[48:96, 3] = 2
    initial_player_props.iloc[48:96, 4] = 6.5
    initial_player_props.iloc[96:144, 3] = 3
    initial_player_props.iloc[144:192, 3] = 0
    initial_player_props.iloc[144:192, 4] = 50.5

    # Set type in to int
    initial_player_props["prop"] = initial_player_props["prop"].astype(int)

    # Sort
    initial_player_props["player_lower"] = initial_player_props['player'].str.lower()
    initial_player_props = initial_player_props.sort_values(by = ["prop", "team_abbr", "player_lower"])
    initial_player_props = initial_player_props.drop("player_lower", axis = 1)

    # Drop index & return
    initial_player_props = initial_player_props.reset_index(drop=True)
    return initial_player_props

# Merge player_props_df for app.py 
def merge_player_props(old_props: pd.DataFrame, new_props: pd.DataFrame, rosters: pd.DataFrame):
    
    # Merge old props with new props
    new_props = pd.merge(
        old_props,
        new_props.drop("team_abbr", axis=1), 
        on=['player', 'prop'], 
        how = "outer", 
        suffixes=('_initial', '_updated')
    )

    # Merge with rosters to get teams and team_abbrs
    new_props = pd.merge(
        new_props.drop(["team", "team_abbr"], axis = 1), 
        rosters,
        on = "player", 
        how = "left"
    )  

    # Fill in missing values from new_props with corresponding values from old_props
    new_props['line'] = new_props['line_updated'].fillna(new_props['line_initial'])

    # Drop the redundant columns
    new_props = new_props.drop(['line_initial', 'line_updated'], axis=1)

    # Add player_lower column for sorting
    new_props["player_lower"] = new_props['player'].str.lower()

    # Sort new_props by prop, team, and player_lower
    new_props = new_props.sort_values(by = ["prop", "team_abbr", "player_lower"])

    # Drop the player_lower column
    new_props = new_props.drop("player_lower", axis = 1)

    # Reset index & return
    new_props = new_props.reset_index(drop=True)
    return new_props
    
# Function to build dataframe of previous player Maps 1 - 3 Kill totals based
# on analysis performed in testing_maps_1_thru_3_kills.ipynb 
def build_1_thru_3_totals(cdlDF_input: pd.DataFrame):
    
    # 1. List of match_ids with replaceable map 1, 
    # computed in testing_maps_1_thru_3_kills.ipynb 
    replaceable_ids = [27200, 27237, 53372, 27219, 52845, 27245, 27255, 27266,
                       27250, 52933, 27270, 35645, 27223, 27241, 53281, 27249, 
                       27231, 27197, 52842, 27264, 27207]

    # 2. If replaceable, replace all old Map 1s with corresponding Map 4
    adj_cdlDF = cdlDF_input[
        ~((cdlDF_input['match_id'].isin(replaceable_ids)) & 
        (cdlDF_input['map_num'] == 1))
        ]
    adj_cdlDF.loc[((adj_cdlDF['match_id'].isin(replaceable_ids)) & (adj_cdlDF['map_num'] == 4)), 'map_num'] = 1
    adj_cdlDF

    # 3. List of match_ids with irreplaceable Map 1 Skidrow or Terminal
    # computed in testing_maps_1_thru_3_kills.ipynb 
    irr_old_maps = [27208, 35635, 27211, 27265, 27243, 35633, 35634, 35648,
                    27220, 27230, 27206, 27221, 27229, 27213]

    # 4. Drop all matches with irreplaceable Map 1 Skidrows or Terminals
    adj_cdlDF = adj_cdlDF[~adj_cdlDF['match_id'].isin(irr_old_maps)]

    # 5. Remove All Map 4s & Map 5s from adj_cdl
    adj_cdlDF = adj_cdlDF[adj_cdlDF['map_num'] < 4].reset_index(drop = True)

    # 6. Compute adjusted Maps 1 - 3 Kills for every Player & Series
    adj_1_thru_3_totals_df = adj_cdlDF \
        .groupby(['match_id', 'player', 'match_date', 'team_abbr'])['kills'].sum() \
        .reset_index()
    
    # 7. Sort values & return
    adj_1_thru_3_totals_df = adj_1_thru_3_totals_df.sort_values(['match_id', 'team_abbr', "player"], ignore_index = True)

    # 8. Convert match_date column to datetime
    adj_1_thru_3_totals_df["match_date"] = pd.to_datetime(adj_1_thru_3_totals_df['match_date'])
    
    return adj_1_thru_3_totals_df

# Function to load vetoes
def load_vetoes(filepath: str):

    # Read in vetoes
    vetoes_wide = pd.read_excel(filepath)
    # Left join with team_abbrs
    vetoes_wide['team_abbr'] = vetoes_wide['team'].map(team_abbrs)
    # Return
    return vetoes_wide

# Function to pivot vetoes
def pivot_vetoes(vetoes_input: pd.DataFrame):

    # Pivot and sort
    vetoes = pd.melt(
        vetoes_input.copy(), 
        id_vars = ['match_id', 'match_date', 'stage', 'team'], 
        value_vars = ['hp_ban', 'hp_pick', 'snd_ban', 'snd_pick', 'ctrl_ban', 'ctrl_pick'], 
        var_name = "select", 
        value_name = "map_name"
    ).sort_values(["match_id", "team"], ignore_index = True)

    # Split var_name column into gamemode and select columns
    vetoes[['gamemode', 'select']] = vetoes['select'].str.split('_', expand=True)

    # Reorder columns
    vetoes = vetoes[[
        'match_id', 'match_date', 'stage', 'team', 
        'gamemode', 'select', 'map_name'
    ]]

    # Expand gamemode names in gamemode column
    gamemode_mapping = {
        'hp': 'Hardpoint',
        'snd': 'Search & Destroy',
        'ctrl': 'Control'
    }
    vetoes['gamemode'] = vetoes['gamemode'].replace(gamemode_mapping)

    # Return
    return vetoes
