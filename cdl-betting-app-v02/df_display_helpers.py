
import pandas as pd

# Function to create dataframe of series results for user-selected team
def build_series_results(series_score_diffs_input: pd.DataFrame, team_input: str):

    series_score_diffs_input = series_score_diffs_input \
        [series_score_diffs_input["team"] == "Atlanta FaZe"] \
        [["match_date", "map_wins", "map_losses", "opp"]].reset_index(drop=True)

    series_score_diffs_input = series_score_diffs_input.rename(
        columns = {"match_date": "Date",
                    "map_wins": "Map Wins", 
                    "map_losses": "Map Losses", 
                    "opp": "Opponent"}
        )

    return series_score_diffs_input