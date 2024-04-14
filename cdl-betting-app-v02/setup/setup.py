# Import pandas, numpy, and datetime
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np

# Import psycopg2 
import psycopg2

# Import db password from config
from setup.config import db_password

# List of players that have been dropped
dropped_players = [
    "Afro", "Arcitys", "Asim", "Cammy", "Capsidal", "EriKBooM", 
    "GodRx", "iLLeY", "JurNii", "Owakening", "SlasheR", "Vivid"
]

# Function to load and clean cdl data and return as pandas dataframe
def load_and_clean_cdl_data():

    #establishing the connection
    conn = psycopg2.connect(
    database = "cdl_db", 
    user = 'postgres', 
    password = db_password,
    host = '127.0.0.1', 
    port= '5432'
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

    # Add team colors, abbreviations, and icons

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

    # Left join cdlDF & team_abbrs_colors_df
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
    
    return cdlDF

# Build dataframe of series score differentials
def build_series_summaries(cdlDF_input):
    series_score_diffs = \
        cdlDF_input[["match_id", "team", "map_num", "gamemode", "map_result"]] \
        .drop_duplicates() \
        .groupby(["match_id", "team"], observed = True) \
        .agg(
            map_wins = ("map_result", lambda x: sum(x)), 
            map_losses = ("map_result", lambda x: len(x) - sum(x)), 
        ) \
        .reset_index()

    series_score_diffs["series_score_diff"] = \
        series_score_diffs["map_wins"] - series_score_diffs["map_losses"]

    return series_score_diffs

# Function to remove all removed map & mode combos from cdlDF, 
# after building series summaries

def filter_cdldf(cdlDF_input):
    
    # Remove map & mode combos
    cdlDF_input = \
        cdlDF_input[
            ~((cdlDF_input['gamemode'] == 'Hardpoint') & (cdlDF_input['map_name'] == 'Invasion')) &
            ~((cdlDF_input['gamemode'] == 'Hardpoint') & (cdlDF_input['map_name'] == 'Skidrow')) &
            ~((cdlDF_input['gamemode'] == 'Hardpoint') & (cdlDF_input['map_name'] == 'Terminal')) &
            ~((cdlDF_input['gamemode'] == 'Search & Destroy') & (cdlDF_input['map_name'] == 'Skidrow')) &
            ~((cdlDF_input['gamemode'] == 'Search & Destroy') & (cdlDF_input['map_name'] == 'Terminal')) 
        ]
    
    # Remove dropped players, excluding players who switched teams
    cdlDF_input = cdlDF_input[~cdlDF_input['player'].isin(dropped_players)]

    # Update team for "Standy"
    cdlDF_input.loc[cdlDF_input['player'] == 'Standy', 'team'] = 'Minnesota ROKKR'

    # Update team for "ReeaL"
    cdlDF_input.loc[cdlDF_input['player'] == 'ReeaL', 'team'] = 'Miami Heretics'

    return cdlDF_input

# Funciton to build rosters
def build_rosters(cdlDF_input: pd.DataFrame):
    rostersDF = cdlDF_input[["player", "team"]].drop_duplicates().sort_values(by = ["team", "player"], key = lambda x: x.str.lower())
    return rostersDF

# Function to create a pandas dataframe of team summaries
def build_team_summaries(cdlDF_input: pd.DataFrame): 

    # Team Summaries by Map & Mode
    team_summaries_DF_top = \
        cdlDF_input[["match_id", "team", "map_name", "gamemode", "map_result"]] \
        .drop_duplicates() \
        .groupby(["team", "gamemode", "map_name"], observed = True) \
        .agg(
            wins = ("map_result", lambda x: sum(x)), 
            losses = ("map_result", lambda x: len(x) - sum(x)), 
            win_percentage = ("map_result", lambda x: round(sum(x) / len(x), 2))
        ) \
        .reset_index()
    
    # Team Summaries by Mode only
    team_summaries_DF_bottom = \
        cdlDF_input[["match_id", "team", "map_name", "gamemode", "map_result"]] \
        .drop_duplicates() \
        .groupby(["team", "gamemode"], observed = True) \
        .agg(
            wins = ("map_result", lambda x: sum(x)), 
            losses = ("map_result", lambda x: len(x) - sum(x)), 
            win_percentage = ("map_result", lambda x: round(sum(x) / len(x), 2))
        ) \
        .reset_index()
    
    # Insert map_name column into team_summaries_DF_bottom
    # for stacking
    team_summaries_DF_bottom["map_name"] = "Overall"
    position = 2
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