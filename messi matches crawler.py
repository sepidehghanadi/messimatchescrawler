import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import lxml.html

driver= r'msedgedriver.exe'

url = 'https://www.messivsronaldo.app/match-histories/messi-match-history/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

data = []

# Initialize lists to store data
data = []

# Find all match divs
match_divs = soup.find_all('div', class_='mb-4 md:mb-5 text-sm text-gray-300 md:flex md:flex-wrap relative')

# Iterate over each match div
for match_div in match_divs:
    match_data = {}
    
    # Meta details
    meta_wrap = match_div.find('div', class_='MatchHistory-module--metaWrap--saOAJ')
    if meta_wrap:
        spans = meta_wrap.find_all('span')
        match_data['Number'] = spans[0].text.strip('#') if spans and len(spans) > 0 else np.nan
        match_data['Date'] = spans[1].text.strip() if spans and len(spans) > 1 else np.nan
        match_data['Season'] = spans[2].text.strip() if spans and len(spans) > 2 else np.nan
        match_data['Competition'] = spans[3].text.strip() if spans and len(spans) > 3 else np.nan
        match_data['Round'] = spans[4].text.strip() if spans and len(spans) > 4 else np.nan
    
    team_div = match_div.find('div', class_='flex bg-noir-lighten10 border border-gray-700 md:flex-1')
    if team_div:
        home_away = team_div.find('span', class_='flex flex-col p-2 justify-center items-center bg-noir-lighten5 text-gray-500 text-sm border-r border-gray-700')
        if home_away:
            match_data['Home/Away'] = home_away.find('span').text.strip() if home_away.find('span') else np.nan
        
        team_names = team_div.find_all('span', class_='block w-full whitespace-no-wrap truncate')
        team_scores = team_div.find_all('span', class_='flex items-center justify-center bg-noir-lighten5 w-1/5 p-1 font-semibold border-r border-gray-700')
        if len(team_names) == 2 and len(team_scores) == 2:
            match_data['Home Team'] = team_names[0].text.strip()
            match_data['Home Score'] = team_scores[0].text.strip()
            match_data['Away Team'] = team_names[1].text.strip()
            match_data['Away Score'] = team_scores[1].text.strip()
        else:
            match_data['Home Team'] = np.nan
            match_data['Home Score'] = np.nan
            match_data['Away Team'] = np.nan
            match_data['Away Score'] = np.nan
    
        match_html = lxml.html.fromstring(str(match_div))  # Convert match_div to string
        goals_xpath = './/div[2]/div[2]/div[1]/span[1]'
        assists_xpath = './/div[2]/div[2]/div[2]/span[1]'

        goals_element = match_html.xpath(goals_xpath)
        assists_element = match_html.xpath(assists_xpath)

        # Check if elements exist and extract text
        if goals_element:
            match_data['Goals'] = goals_element[0].text.strip()
        else:
            match_data['Goals'] = np.nan

        if assists_element:
            match_data['Assists'] = assists_element[0].text.strip()
        else:
            match_data['Assists'] = np.nan

        # Fetching minutes played and match rating
        minutes_text = match_html.xpath('.//*[@class="flex flex-1 justify-center items-center px-2 py-1"]/text()')
        rating_text = match_html.xpath('.//*[@class="MatchHistory-module--rating--1XxjB"]/text()')

        if minutes_text:
            match_data['Minutes Played'] = minutes_text[0].split()[0]
        else:
            match_data['Minutes Played'] = np.nan

        if rating_text:
            match_data['Match Rating'] = rating_text[0].split()[0]
        else:
            match_data['Match Rating'] = np.nan
    
    # Additional performance stats
    perf_stats_div = match_div.find('div', class_='flex flex-wrap border-l border-t border-gray-700 bg-noir-lighten10')
    if perf_stats_div:
        perf_stats = perf_stats_div.find_all('div', class_='MatchHistory-module--perfStat--3x7Zu')
        for stat in perf_stats:
            key = stat.find('span', class_='MatchHistory-module--perfStatKey--38ffo').text.strip()
            val = stat.find('strong', class_='MatchHistory-module--perfStatVal--7MTGG').text.strip()
            match_data[key] = val
    else:
        match_data['Shots'] = np.nan
        match_data['Shots on Target'] = np.nan
        match_data['Free Kick Attempts'] = np.nan
        match_data['Successful Dribbles'] = np.nan
        match_data['Key Passes'] = np.nan
        match_data['Big Chances Created'] = np.nan
        match_data['Accurate Throughballs'] = np.nan
        match_data['Aerial Duels Won'] = np.nan
        match_data['xG'] = np.nan
        match_data['xA'] = np.nan
        match_data['MOTM'] = np.nan
        match_data['Match Rating'] = np.nan
    
    # Append the match data to the list
    data.append(match_data)
df = pd.DataFrame(data)
df.to_csv('leomessi_matches.csv')
