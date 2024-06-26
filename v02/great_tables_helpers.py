
# Import pandas & numpy
import pandas as pd
import numpy as np

# Import great_tables 
from great_tables import *

# ---------------------------------------
# Complete, but not implemented in app.py
# ---------------------------------------

# Function to build team summary gtTable
def team_summaries_gt_fn(
        team_summaries_input: pd.DataFrame, team_x: str, team_y: str
    ):

    # In build_team_summaries from setup, we replaced all NA values with 0s. 
    # Here, we will put those NA values back in for styling purposes

    # Identify rows where both 'win' and 'loss' are 0
    mask = (team_summaries_input['wins'] == 0) & (team_summaries_input['losses'] == 0)

    # Replace win_percentage with NaN where the condition is true
    team_summaries_input.loc[mask, 'win_percentage'] = np.nan

    gt_df = \
        pd.merge(
            team_summaries_input[team_summaries_input["team"] == team_x], 
            team_summaries_input[team_summaries_input["team"] == team_y], 
            how = "left", 
            on = ["gamemode", "map_name"]
            ) \
            .drop(columns = ["team_x", "team_y"], inplace = False, axis = 1) \
            .sort_values(by = ["gamemode", "map_name"])
    
    # Get numerical columns
    numerical_columns = gt_df.select_dtypes(include='number').columns

    # Replace NaN values in numerical columns with 0
    gt_df[numerical_columns] = gt_df[numerical_columns].fillna(0)
    
    team_summary_gt_tbl = \
        GT(
            gt_df, 
            rowname_col =  "map_name",
            groupname_col = "gamemode"
        ) \
        .cols_label(
            wins_x = "Wins", losses_x = "Losses", 
            wins_y = "Wins", losses_y = "Losses", 
            win_percentage_x = "Win %", win_percentage_y = "Win %"
        ) \
        .cols_align("center") \
        .data_color(
            columns = ["win_percentage_x", "win_percentage_y"], 
            palette =  ["#cb181d", "#cb181d", "#fcae91", "#ffffff", 
            "#bdd7e7", "#2171b5", "#2171b5"], 
            domain = [0, 1]
        ) \
        .fmt_percent(
            columns = ["win_percentage_x", "win_percentage_y"], 
            decimals = 0
        ) \
        .fmt_number(
            columns = ["wins_x", "losses_x", "wins_y", "losses_y"], 
            decimals = 0
        ) \
        .opt_align_table_header("center") \
        .tab_spanner(label = team_x, 
                     columns = ["wins_x", "losses_x", "win_percentage_x"]) \
        .tab_spanner(label = team_y, 
                     columns = ["wins_y", "losses_y", "win_percentage_y"]) \
        .tab_stubhead(label = "Map & Mode") \
        .tab_options(
            container_width = "600", 
            table_width = "560px"
        )
    return team_summary_gt_tbl

# ---------------------------------------
# Complete, but not implemented in app.py
# ---------------------------------------

# Function to build head-to-head summary gtTable
def h2h_summary_gt_fn(cdlDF_input, team_x: str, team_y: str):

    # H2H Summary by Mode Only
    h2h_summary_DF_bottom = cdlDF_input \
        [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
        [(cdlDF_input["team"] == team_x) & \
         (cdlDF_input["opp"] == team_y)] \
         .drop_duplicates() \
         .groupby("gamemode", observed = True) \
         .agg(
            wins_x = ("map_result", lambda x: sum(x)), 
            losses_x = ("map_result", lambda x: len(x) - sum(x)), 
            win_percentage_x = ("map_result", lambda x: round(sum(x) / len(x), 2)),
            wins_y = ("map_result", lambda x: len(x) - sum(x)), 
            losses_y = ("map_result", lambda x: sum(x)), 
            win_percentage_y = ("map_result", lambda x: round((len(x) - sum(x)) / len(x), 2))
         ) \
         .reset_index()
    
    # Insert map_name column into h2h_summary_DF_bottom
    # for stacking
    h2h_summary_DF_bottom["map_name"] = "Overall"
    position = 1
    h2h_summary_DF_bottom.insert(position, "map_name", h2h_summary_DF_bottom.pop("map_name"))

    # H2H Summary by Map & Mode
    h2h_summary_DF_top = cdlDF_input \
        [["match_id", "team", "map_name", "gamemode", "map_result", "opp"]] \
        [(cdlDF_input["team"] == team_x) & \
         (cdlDF_input["opp"] == team_y)] \
         .drop_duplicates() \
         .groupby(["gamemode", "map_name"], observed = True) \
         .agg(
            wins_x = ("map_result", lambda x: sum(x)), 
            losses_x = ("map_result", lambda x: len(x) - sum(x)), 
            win_percentage_x = ("map_result", lambda x: round(sum(x) / len(x), 2)),
            wins_y = ("map_result", lambda x: len(x) - sum(x)), 
            losses_y = ("map_result", lambda x: sum(x)), 
            win_percentage_y = ("map_result", lambda x: round((len(x) - sum(x)) / len(x), 2))
         ) \
         .reset_index()
    
    # Concatenate the two DataFrames vertically
    gt_df = pd.concat([h2h_summary_DF_top, h2h_summary_DF_bottom])

    # Get numerical columns
    numerical_columns = gt_df.select_dtypes(include='number').columns

    # Replace NaN values in numerical columns with 0
    gt_df[numerical_columns] = gt_df[numerical_columns].fillna(0)

    # Reset the index of the stacked DataFrame
    gt_df.reset_index(drop = True, inplace = True)

    # Reorder gamemode factor levels
    gt_df['gamemode'] = \
        pd.Categorical(gt_df['gamemode'], categories = ['Hardpoint', 'Search & Destroy', 'Control'])

    # Reorder map_name factor levels
    gt_df['map_name'] = \
        pd.Categorical(
            gt_df['map_name'], 
            categories = ['6 Star', 'Highrise', 'Invasion', 'Karachi', \
                          'Rio', 'Sub Base', 'Vista', 'Overall'])

    # Sort gt_df
    gt_df = gt_df.sort_values(by = ["gamemode", "map_name"])

    # Create H2H Summary gtTable
    h2h_summary_gt_tbl = \
        GT(
            gt_df, 
            rowname_col =  "map_name",
            groupname_col = "gamemode"
        ) \
        .cols_label(
            wins_x = "Wins", losses_x = "Losses", 
            wins_y = "Wins", losses_y = "Losses", 
            win_percentage_x = "Win %", win_percentage_y = "Win %"
        ) \
        .cols_align("center") \
        .data_color(
            columns = ["win_percentage_x", "win_percentage_y"], 
            palette =  ["#cb181d", "#cb181d", "#fcae91", "#ffffff", 
            "#bdd7e7", "#2171b5", "#2171b5"], 
            domain = [0, 1]
        ) \
        .fmt_percent(
            columns = ["win_percentage_x", "win_percentage_y"], 
            decimals = 0
        ) \
        .opt_align_table_header("center") \
        .tab_spanner(label = team_x, 
                     columns = ["wins_x", "losses_x", "win_percentage_x"]) \
        .tab_spanner(label = team_y, 
                     columns = ["wins_y", "losses_y", "win_percentage_y"]) \
        .tab_stubhead(label = "Map & Mode") \
        .tab_options(
            container_width = "600", 
            table_width = "560px"
        )

    return h2h_summary_gt_tbl