
# Import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

# Import undetected chromedriver
import undetected_chromedriver as uc

# Import time & pandas
import time
import pandas as pd

def scrape_prizepicks():

    # Set Chrome Options, specifically to allow location tracking on PrizePicks
    capabilities = DesiredCapabilities().CHROME

    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")

    prefs = {
        'profile.default_content_setting_values':
        {
            'notifications': 1,
            'geolocation': 1
        },

        'profile.managed_default_content_settings':
        {
            'geolocation': 1
        },
    }

    chrome_options.add_experimental_option('prefs', prefs)
    capabilities.update(chrome_options.to_capabilities())

    # Try to scrape props
    try:

        # Open browser
        driver = uc.Chrome(options = chrome_options)

        # Visit PrizePicks Website
        driver.get("https://app.prizepicks.com/")
        time.sleep(5)

        # Close initial pop-up
        WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "close")))
        time.sleep(5)
        driver.find_element(By.XPATH, "/html/body/div[3]/div[3]/div/div/button").click()
        time.sleep(5)

        # Find all league buttons 
        league_buttons = driver.find_element(By.ID, "scrollable-area").text.split('\n')

        # Get index of the COD tab in the league_buttons list
        cod_index = league_buttons.index("COD") + 1
        
        # Navigate to COD tab using COD index, clicking right arrow if necessary
        if cod_index <= 12:
            driver.find_element(By.XPATH, "//*[@id='scrollable-area']/button[" + str(cod_index) + "]").click()
        elif cod_index <= 15:
            driver.find_element(By.XPATH, "//*[@id='board']/nav[1]/button[2]").click() # Right arrow
            time.sleep(5)
            driver.find_element(By.XPATH, "//*[@id='scrollable-area']/button[" + str(cod_index) + "]").click()
        elif cod_index <= 18:
            driver.find_element(By.XPATH, "//*[@id='board']/nav[1]/button[2]").click() # Right arrow
            time.sleep(5)
            driver.find_element(By.XPATH, "//*[@id='board']/nav[1]/button[2]").click() # Right arrow
            time.sleep(5)
            driver.find_element(By.XPATH, "//*[@id='scrollable-area']/button[" + str(cod_index) + "]").click()
        time.sleep(5)

        # Initilize an empty list to hold the player props
        player_props = []

        # Find categories
        stat_container = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "stat-container")))
        categories = driver.find_element(By.CSS_SELECTOR, ".stat-container").text.split('\n')

        # Remove Maps 1 - 3 Kills (Combo) & Popular Picks
        if "MAPS 1-3 Kills (Combo)" in categories:
            categories.remove("MAPS 1-3 Kills (Combo)")
        if "Popular 🔥" in categories:
            categories.remove("Popular 🔥")

        # Get player projections

        # Loop through categories
        for category in categories:
            driver.find_element(By.XPATH, f"//div[text()='{category}']").click()
            time.sleep(10)

            # Print category for testing
            print(f"{category}")
            
            # Get list of all projections for current category
            projectionsPP = driver.find_elements(By.ID, "test-projection-li")

            # Loop through current list of projections
            for i in range(len(projectionsPP)):

                # Get line info for each player prop
                player = projectionsPP[i].find_element(By.ID, "test-player-name").text
                team_abbr = projectionsPP[i].find_element(By.ID, "test-team-position").text.split(" - ")[0]
                try: 
                    player_line = float(driver.find_element(
                        By.XPATH, 
                        '/html/body/div[1]/div/div[3]/div[1]/div/main/div/div/div[1]/div[3]/ul/li[' + str(i + 1) + ']/div[3]/div/div/div/div[1]'
                    ).text)
                except NoSuchElementException: # try a different XPath when timer is next to player's name
                    player_line = float(driver.find_element(
                        By.XPATH, 
                        '/html/body/div[1]/div/div[3]/div[1]/div/main/div/div/div[1]/div[3]/ul/li[' + str(i + 1) + ']/div[4]/div/div/div/div[1]'
                    ).text)


                # Append prop to our list
                player_props.append({
                    "player": player, 
                    "team_abbr": team_abbr, 
                    "prop": category.split(" ")[1] if category != "MAPS 1-3 Kills" else "0", 
                    "line": player_line
                })

        # Convert our list of player props to a dataframe
        player_props_df =  pd.DataFrame(player_props)

        # Set proptype column to int
        player_props_df['prop'] = player_props_df['prop'].astype(int)

        # Set player and team_abbr columns to str
        player_props_df['player'] = player_props_df['player'].astype(str)
        player_props_df['team_abbr'] = player_props_df['team_abbr'].astype(str)

        # Drop duplicates before sorting
        player_props_df.drop_duplicates(subset = ['player', 'prop'], inplace = True)

        # Add player_lower column for sorting
        player_props_df["player_lower"] = player_props_df['player'].str.lower()

        # Sort player_props_df by prop, team, and player_lower
        player_props_df = player_props_df.sort_values(by = ["prop", "team_abbr", "player_lower"])

        # Drop the player_lower column
        player_props_df = player_props_df.drop("player_lower", axis = 1)

        # Reset index & return
        player_props_df = player_props_df.reset_index(drop=True)

        # Return player props
        return player_props_df
    
    # Catch value error if COD is not visible
    except ValueError:
        print("At this time, COD player props are not up on the PrizePicks website")
