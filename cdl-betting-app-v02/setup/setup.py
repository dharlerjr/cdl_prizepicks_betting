# Import pandas, numpy, and datetime
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
import datetime as dt

# Import psycopg2 
import psycopg2

# Import db password from config
from config import db_password

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
    cdlDF.replace("Minnesota RØKKR", "Minnesota ROKKR")

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

    # Get rosters
    rostersDF = cdlDF[['player', 'team']].drop_duplicates()
    rostersDF = rostersDF.sort_values(by='team')
    rostersDF.reset_index(drop=True, inplace=True)

    # Get dropped players
    dropped_players = [
        "GodRx", "Cammy", "JurNii", "Capsidal", "Afro", "Asim", 
        "Slasher", "Arcitys", "Vivid", "Owakening", "EriKBooM", "iLLey"
        ]
    
    return cdlDF
