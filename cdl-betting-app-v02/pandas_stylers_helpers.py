
# Import pandas and ListedColormap from matplotllib
import pandas as pd
from matplotlib.colors import ListedColormap

# Import filter_maps from setup
from setup.setup import filter_maps

# Function to build team summary
def team_summaries_fn(team_summaries_input: pd.DataFrame, team_x: str, team_y: str):
    summary_df = \
        pd.merge(
            team_summaries_input[team_summaries_input["team"] == team_x], 
            team_summaries_input[team_summaries_input["team"] == team_y], 
            how = "outer", 
            on = ["gamemode", "map_name"]
            ) \
            .drop(columns = ["team_x", "team_y"], inplace = False, axis = 1) \
            .sort_values(by = ["gamemode", "map_name"])
    
    # Fill NA's in wins & losses columns
    columns_to_fill = ['wins_x', 'losses_x', 'wins_y', 'losses_y']
    summary_df[columns_to_fill] = summary_df[columns_to_fill].fillna(0)

    # Correct datatypes
    summary_df['wins_x'] = summary_df['wins_x'].astype('int64')
    summary_df['losses_x'] = summary_df['losses_x'].astype('int64')
    summary_df['wins_y'] = summary_df['wins_y'].astype('int64')
    summary_df['losses_y'] = summary_df['losses_y'].astype('int64')
    #summary_df['win_percentage_x'] = summary_df['win_percentage_x'].astype('float64')
    #summary_df['win_percentage_y'] = summary_df['win_percentage_y'].astype('float64')

    # Rename gamemode and map_name columns
    summary_df = summary_df.rename(columns = {"gamemode": "Gamemode", "map_name": "Map"})

    # Add MultiIndex to Rows
    summary_df = summary_df.set_index(["Gamemode", "Map"])

    # Add MultiIndex to Columns
    columns = pd.MultiIndex.from_tuples([
        (team_x, 'Wins'), (team_x, 'Losses'), (team_x, 'Win %'),
        (team_y, 'Wins'), (team_y, 'Losses'), (team_y, 'Win %')
    ])
    summary_df.columns = columns
    
    # Style dataframe
    summary_df_styler = summary_df.style \
        .format(precision = 2) \
        .background_gradient(
            vmin = 0, vmax = 1, axis = 0, 
            cmap = ListedColormap(["#cb181d", "#cb181d", "#fcae91", "#ffffff", 
                                   "#bdd7e7", "#2171b5", "#2171b5"]),
            subset = [(team_x, 'Win %'), (team_y, 'Win %')]) \
        .highlight_null(color = 'grey')

    return summary_df_styler

def h2h_summary_fn(cdlDF_input, team_x: str, team_y: str):
  
  # H2H Summary by Mode Only
  h2h_summary_df_bottom = cdlDF_input \
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
  h2h_summary_df_bottom["map_name"] = "Overall"
  position = 1
  h2h_summary_df_bottom.insert(position, "map_name", h2h_summary_df_bottom.pop("map_name"))

  # H2H Summary by Map & Mode
  h2h_summary_df_top = filter_maps(cdlDF_input) \
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
  h2h_summary_df = pd.concat([h2h_summary_df_bottom, h2h_summary_df_top])

  # Reorder gamemode factor levels
  h2h_summary_df['gamemode'] = \
    pd.Categorical(h2h_summary_df['gamemode'], categories = ['Hardpoint', 'Search & Destroy', 'Control'])

  # Reorder map_name factor levels
  h2h_summary_df['map_name'] = \
    pd.Categorical(
      h2h_summary_df['map_name'], 
      categories = ['6 Star', 'Highrise', 'Invasion', 'Karachi',
                    'Rio', 'Sub Base', 'Vista', 'Overall']
      )

  # Sort h2h_summary_df
  h2h_summary_df = h2h_summary_df.sort_values(by = ["gamemode", "map_name"])

  # Rename gamemode and map_name columns
  h2h_summary_df = h2h_summary_df.rename(columns = {"gamemode": "Gamemode", "map_name": "Map"})

  # Add MultiIndex to Rows
  h2h_summary_df = h2h_summary_df.set_index(["Gamemode", "Map"])

  # Add MultiIndex to Columns
  columns = pd.MultiIndex.from_tuples([
      (team_x, 'Wins'), (team_x, 'Losses'), (team_x, 'Win %'),
      (team_y, 'Wins'), (team_y, 'Losses'), (team_y, 'Win %')
  ])
  h2h_summary_df.columns = columns
  
  # Style dataframe
  h2h_summary_df_styler = h2h_summary_df.style \
    .format(precision = 2) \
    .background_gradient(
      vmin = 0, vmax = 1, axis = 0, 
      cmap = ListedColormap(["#cb181d", "#cb181d", "#fcae91", "#ffffff", 
                             "#bdd7e7", "#2171b5", "#2171b5"]),
      subset = [(team_x, 'Win %'), (team_y, 'Win %')]) \
    .highlight_null(color = 'grey')
  
  return h2h_summary_df_styler