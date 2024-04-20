# Shiny Applications for CDL Betting on PrizePicks

Two Shiny applications for betting on CDL player props on PrizePicks. Version 1 coded in R, Versions 2 & 3 coded in Python. Data from breakingpoint.gg using my [breakingpoint.gg web scraping project](https://github.com/dharlerjr/bp_web_scraping).

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

## Version 2

- Coded in Python (see below)
- **User no longer has to manually input player props!!!**
  - Uses undetected_chromedriver (only available in Python to my knowledge) to scrape player prop lines from PrizePicks website (documentation on undetected_chromedriver can be found [here](https://pypi.org/project/undetected-chromedriver/2.1.1/))
- Added team logos! Found here: [Call of Duty Esports Wiki](https://cod-esports.fandom.com/wiki/Call_of_Duty_Esports_Wiki)
- Accounted for CDL roster changes and map pool adjustments
- Kept files which were ultimately not implemented in version 3, namely:
  - ggplot_helpers
  - great_tables_helpers
  - pandas_stylers_helpers
- Completed April 2024

### Python Packages

- **selenium** to automate a chrome web browser to scrape the PrizePicks website
- **undetected_chromedriver** to scrape the PrizePicks website undetected
- **Psycopg** & **sqlio** to load the CDL dataset from the PostgreSQL database into a Python dataframe
  - **sqlalchemy** would have also been a fantastic options
- **Seaborn** & **Matplotlib** to create Data Visualizations
- **Shiny** to build the web app and display the reactive dashboard components
- **Faicons** to add icons to the displayed value boxes

## Version 3

- Still coded in Python
- Updated layout from version 2
- Learned how to plot a seaborn boxplot and a seaborn scatterplot on a single MatPlotLib figure
- Removed faceted plots
- Cleaned working directory

## Challenges
