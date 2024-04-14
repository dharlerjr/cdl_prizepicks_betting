# Shiny Applications for CDL Betting on PrizePicks

Two Shiny applications for betting on CDL player props, primarily on PrizePicks. Version 1 coded in R, Version 2 coded in Python. Data from breakingpoint.gg using my [breakingpoint.gg web scraping project](https://github.com/dharlerjr/bp_web_scraping).

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
- Completed April 2024

### Python Packages

- **selenium** to automate a chrome web browser to scrape the PrizePicks website
- **undetected_chromedriver** to scrape the PrizePicks website undetected
- **Psycopg** & **sqlio** to load the CDL dataset from the PostgreSQL database into a Python dataframe
- **Seaborn** to create Data Visualizations
- **Shiny** to build the web app

## Notes

- Team logos not used due to lack of quality and accessiblity
- Version 2 accounts for changes between CDL Seasons 2 & 3 (ie. roster and map pool changes)
