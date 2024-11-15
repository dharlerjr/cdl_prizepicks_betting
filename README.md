# Shiny Application for CDL Betting on PrizePicks

Multiple versions of the same Shiny application for betting on Call of Duty League (CDL) player props on PrizePicks. Version 1 coded in R, Versions 2 - 4 coded in Python. Data from breakingpoint.gg using my [breakingpoint.gg web scraping project](https://github.com/dharlerjr/bp_web_scraping).

## Version 1

- Coded in R
- User inputs (2) CDL teams in a given match, along with the current gamemode, map name, and a maximum of (8) player kill prop lines they'd like to bet on
- Displays...
  - gt Table of Team Summaries (Wins, Losses, Win %s by Map and Mode)
  - gt Table of Head-to-Head Summary
  - (1) box plot of each player's kills from all previous CDL matches, filtered by the selected map and mode
  - (1) line chart of each player's kills from all previous CDL matches, filtered by the selected map and mode; x-axis can be set to...
    - Time
    - Total Score, or...
    - Score Differential
  - Each team's distribution of score differentials for selected map and mode combination
  - (1) datatable for each team's previous map results for the selected map and mode combination
- Completed March 2024

### R Packages

- **tidyverse** for data manipulation, exploration, and visualization
- **RPostgres** to load the CDL dataset from the PostgreSQL database into an R dataframe
- **gt** & **gtExtras** for constructing tables to visualize data
- **RColorBrewer** & **Viridis** for coloring data visualizations
- **scales** for scaling data-colored columns in gt tables
- **shiny** to build the web app

## Version 2 (completed April 2024)

- Coded in Python (see below)
- **User no longer has to manually input player props!!!**
  - Uses undetected_chromedriver (only available in Python to my knowledge) to scrape player prop lines from PrizePicks website (documentation on undetected_chromedriver can be found [here](https://pypi.org/project/undetected-chromedriver/2.1.1/))
- Added team logos! Found here: [Call of Duty Esports Wiki](https://cod-esports.fandom.com/wiki/Call_of_Duty_Esports_Wiki)
- Accounted for CDL roster changes and map pool adjustments
- Kept files which were ultimately not implemented in version 3, namely:
  - ggplot_helpers
  - great_tables_helpers
  - pandas_stylers_helpers

### Python Packages

- **selenium** to automate a chrome web browser to scrape the PrizePicks website
- **undetected_chromedriver** to scrape the PrizePicks website undetected
- **Psycopg** & **sqlio** to load the CDL dataset from the PostgreSQL database into a pandas dataframe
  - **sqlalchemy** would have also been a fantastic options
- **Seaborn** & **Matplotlib** to create Data Visualizations
- **Shiny** to build the web app and display the reactive dashboard components
- **Faicons** to add icons to the displayed value boxes
- **os** for filepaths to team logos

## Version 3 (completed May 2024)

### Major Improvements

- Page 1
  - Refined layout
    - Condensed navsets of player cards into one
    - Combined boxplot and scatterplot into single matplotlib figure by using gridspecs
  - Added new visualizations
    - Donut chart to display each team's most-played maps
    - Replaced faceted plots with ridgeline plots
    - Added Value Box to display date of Last Head-to-Head Match
  - Added **app_helpers.py** to condense **app.py** code
- Added 2nd Page: Player Kills per Maps 1 - 3
  - Identical format as Page 1, with more user inputs, and visualizations focused on the Kills per Maps 1 - 3 statistic
- Added 3rd Page: Match Summaries
  - Users can select a CDL match from a DataFrame of matches, then view the match summary and scoreboards
- Added 4th Page: Vetoes
  - Built Excel sheet of map vetoes for each match and loaded into pandas dataframe
  - Created histograms to visualize pick and ban selections for each team
  - Loaded vetoes dataset into shiny datagrid

### Minor Improvements

- Styled webpage with Shiny's `ui.include_css` and color arguments of various ui functions (ie. `ui.page_navbar`)
- Standardized color scheme, fonts, and font sizes
- Added option to full screen Scoreboards
- Updated icons
- Adjusted figure axes to only display integer values
- Adjusted PrizePicks label to stay visible for all user-input cases
- Centered team logos within their respective containers
- Added Tooltips to further explain visualizations

## Version 4 (Completed June 2024)

- Organized project directory
- Updated PrizePicks webscraping algorithm
- Accounted for dropped players and players who switched teams

