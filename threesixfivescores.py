import pandas as pd
import requests
import json
from PIL import Image 
import re
from io import BytesIO
import time
import numpy as np
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures
import pandas as pd
import re
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor


# Assuming .functions and .exceptions are structured correctly relative to this file's location
# For the purpose of this standalone example, these imports might cause issues if files are not present.
# We will assume they exist as per the original file for the context of the class methods.
# Placeholder for missing imports if not in the same directory or for testing
try:
    from .functions import get_possible_leagues_for_page
    from .exceptions import MatchDoesntHaveInfo
    from .config import headers
except ImportError:
    # Mocking these for the sake of the example if they are not found
    # print("Warning: Using mock imports for functions, exceptions, config. Ensure these modules are correctly placed for full functionality.")
    def get_possible_leagues_for_page(league, none, page): return {league: {'id': 'mock_id'}}
    class MatchDoesntHaveInfo(Exception): pass
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ar,en-US;q=0.9,en;q=0.8",
        "origin": "https://www.365scores.com",
        "referer": "https://www.365scores.com/",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 ...",
        # ... other headers as needed
    }# Basic header for requests


class ThreeSixFiveScores:

    def parse_dataframe(self, objeto):
        # This was a placeholder in the original code. df_concat is not defined here.
        # For the class to be fully functional, this method needs a proper implementation.
        # Example: if objeto is a list of dicts for a stat category
        if isinstance(objeto, dict) and 'rows' in objeto and 'name' in objeto:
            stat_category_name = objeto['name']
            df = pd.DataFrame(objeto['rows'])
            df['stat_category'] = stat_category_name
            # Further processing might be needed depending on 'rows' structure
            return df
        # print(f"Debug: parse_dataframe received an object of type {type(objeto)}, not processing.")
        return pd.DataFrame() # Return empty DataFrame if structure is not as expected


    def get_league_top_players_stats(self, league):
        """Get top performers of certain statistics for a league and a season

        Args:
            league (str): Possible leagues in get_available_leagues("365Scores").
                          The page don't show stats from previous seasons.

        Returns:
            total_df: DataFrame with all the stats, values and players.
        """
        leagues = get_possible_leagues_for_page(league, None, '365Scores')
        if league not in leagues or 'id' not in leagues[league]:
            # print(f"Error: League '{league}' not found or missing ID in get_league_top_players_stats.")
            return pd.DataFrame()
            
        league_id = leagues[league]['id']
        try:
            response = requests.get(f'https://webws.365scores.com/web/stats/?appTypeId=5&langId=1&timezoneName=America/Buenos_Aires&userCountryId=382&competitions={league_id}&competitors=&withSeasons=true', headers=headers, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors
            time.sleep(3) # Keep the delay as in original code
            stats_data = response.json()
        except requests.RequestException as e:
            # print(f"Error fetching league top players stats for league_id {league_id}: {e}")
            return pd.DataFrame()
        except json.JSONDecodeError as e:
            # print(f"Error decoding JSON for league top players stats (league_id {league_id}): {e}")
            return pd.DataFrame()

        if 'stats' not in stats_data or not isinstance(stats_data['stats'], list):
            # print(f"Error: 'stats' key missing or not a list in API response for league_id {league_id}.")
            return pd.DataFrame()
            
        general_stats_list = stats_data['stats']
        total_df = pd.DataFrame()
        for stat_group_object in general_stats_list:
            # Assuming parse_dataframe is meant to process each object in the general_stats_list
            stats_df = self.parse_dataframe(stat_group_object)
            if not stats_df.empty:
                total_df = pd.concat([total_df, stats_df], ignore_index=True)
        return total_df
    
    def get_ids(self, match_url):
        """Extracts ids from a 365Scores match URL.

        Args:
            match_url (str): 365Scores match URL

        Returns:
            id_1, id_2: matchup id and game id.
        """
        # For matchupId (e.g., format like 869-7206-7214)
        match_id1 = re.search(r'-(\d+-\d+-\d+)', match_url)
        id_1 = match_id1.group(1) if match_id1 else None
    
        # For gameId (e.g., from #id=4033824 or ?id=4033824 or /4033824 at end of path)
        match_id2 = re.search(r'[#/]id=(\d+)', match_url)
        if not match_id2: # Try other patterns if not found
             match_id2 = re.search(r'/(\d+)$', match_url.split('#')[0].split('?')[0]) # gameId as last part of path

        id_2 = match_id2.group(1) if match_id2 else None

        return id_1, id_2
    
    def get_match_data(self, match_url):
        """Get data from a match and scrape it.

        Args:
            match_url (url): 365Scores match URL.

        Returns:
            match_data: Json with game data, or an empty dict if an error occurs.
        """
        
        matchup_id, game_id = self.get_ids(match_url)
        
        if not game_id:
            # print(f"Error: Could not extract game_id from URL: {match_url}")
            return {} # Return empty dict if game_id is essential and not found

        api_url = f'https://webws.365scores.com/web/game/?appTypeId=5&langId=1&timezoneName=America/Buenos_Aires&userCountryId=382&gameId={game_id}'
        if matchup_id:
            api_url += f'&matchupId={matchup_id}'
        api_url += '&topBookmaker=14' # Assuming topBookmaker is always needed

        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status() # Raise an exception for HTTP errors
            time.sleep(3) # Keep delay
            response_json = response.json()
        except requests.RequestException as e:
            # print(f"Error fetching match data for gameId {game_id}: {e}")
            return {}
        except json.JSONDecodeError as e:
            # print(f"Error decoding JSON for match data (gameId {game_id}): {e}")
            return {}

        if 'game' not in response_json:
            # print(f"Error: 'game' key not found in API response for URL: {match_url}. Response: {response_json}")
            return {}
        return response_json['game']
    
    def get_requests_stats(self, match_url):
        """Request to stats of a match. Used by get_match_general_stats.

        Args:
            match_url (str): 365Scores match URL.

        Returns:
            response: requests.Response object or None if an error occurs.
        """
        _, game_id = self.get_ids(match_url) # matchup_id not used in this specific endpoint
        if not game_id:
            # print(f"Error: Could not extract game_id from URL for stats request: {match_url}")
            return None

        try:
            response = requests.get(f'https://webws.365scores.com/web/game/stats/?appTypeId=5&langId=1&timezoneName=America/Buenos_Aires&userCountryId=382&games={game_id}', headers=headers, timeout=10)
            response.raise_for_status()
            time.sleep(3) # Keep delay
            return response
        except requests.RequestException as e:
            # print(f"Error fetching request_stats for game_id {game_id}: {e}")
            return None
    
    def get_match_general_stats(self, match_url): # Note: This is the function that processes /web/game/stats/
        """Get detailed general stats for a match (e.g., Possession, Shots) with categories.

        Args:
            match_url (url): 365Scores match URL.

        Returns:
            match_stats_df: DataFrame with game stats, including team names.
        """
        
        response_obj = self.get_requests_stats(match_url) # This uses /web/game/stats/ endpoint
        if response_obj is None:
            return pd.DataFrame()

        try:
            response_data = response_obj.json()
        except json.JSONDecodeError as e:
            # print(f"Error decoding JSON for get_match_general_stats: {e}")
            return pd.DataFrame()

        if 'statistics' not in response_data or not isinstance(response_data['statistics'], list) or \
           'competitors' not in response_data or not isinstance(response_data['competitors'], list) or \
           len(response_data['competitors']) < 2:
            # print(f"Warning: 'statistics' or 'competitors' data is missing or incomplete in API response for {match_url}.")
            return pd.DataFrame()

        match_stats_list = response_data['statistics']
        if not match_stats_list: # If statistics list is empty
             return pd.DataFrame()

        match_stats_df = pd.DataFrame(match_stats_list)
        
        if match_stats_df.empty or 'competitorId' not in match_stats_df.columns:
            # print(f"Warning: No statistics found or 'competitorId' column missing for {match_url}.")
            return match_stats_df # Return what we have, or empty if it is.

        team1_data = response_data['competitors'][0]
        team2_data = response_data['competitors'][1]

        team1_id = team1_data.get('id')
        team1_name = team1_data.get('name', 'Team 1')
        
        team2_id = team2_data.get('id')
        team2_name = team2_data.get('name', 'Team 2')
        
        if team1_id is not None and team2_id is not None:
             match_stats_df['team_name'] = np.where(match_stats_df['competitorId'] == team1_id, team1_name, 
                                               np.where(match_stats_df['competitorId'] == team2_id, team2_name, 'Unknown'))
        else:
             match_stats_df['team_name'] = 'Unknown' 

        return match_stats_df
    
    def get_match_time_stats(self, match_url):
        """Get time match stats (e.g., actual playing time).

        Args:
            match_url (str): 365Scores match URL.

        Returns:
            game_statistics: Dict with time stats or raises MatchDoesntHaveInfo.
        """
        
        response_obj = self.get_requests_stats(match_url) # Uses /web/game/stats/
        if response_obj is None:
            raise MatchDoesntHaveInfo(f"Failed to get response for time stats: {match_url}")
        
        try:
            response_data = response_obj.json()
        except json.JSONDecodeError:
             raise MatchDoesntHaveInfo(f"Failed to decode JSON for time stats: {match_url}")

        if 'actualGameStatistics' not in response_data:
            raise MatchDoesntHaveInfo(f"actualGameStatistics not found in response: {match_url}")
        
        return response_data['actualGameStatistics']
    
    def get_match_data_by_id(self, game_id, competition_id="552"):
        """
        Fetch match data from 365Scores API for a given game and competition.
        """
        url = (
            f"https://webws.365scores.com/web/game/?gameId={game_id}"
            f"&competitions={competition_id}&langId=1&sportType=1"
            f"&timezoneName=Asia/Hebron&userCountryId=115"
        )
        headers = {  # Add correct headers if needed by the API
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        if response.ok:
            return response.json()
        return None

    def get_match_shotmap(self, match_url):
        """Scrape shotmap from the page as a DataFrame, if the match has it.

        Args:
            match_url (url): 365Scores match URL.

        Returns:
            df: DataFrame with shot details or raises MatchDoesntHaveInfo.
        """
        match_data = self.get_match_data(match_url) # Uses /web/game/
        if not match_data or 'chartEvents' not in match_data or 'events' not in match_data.get('chartEvents', {}):
            raise MatchDoesntHaveInfo(f"Shotmap data (chartEvents or events) not found: {match_url}")

        # --- New: check for positive, non-zero results ---
        # Try both possible locations for home/away score
        home_score = 0
        away_score = 0
        # Sometimes match_data['homeCompetitor']['score'], sometimes nested in match_data['game']
        if "homeCompetitor" in match_data and isinstance(match_data["homeCompetitor"], dict):
            home_score = match_data["homeCompetitor"].get("score", 0)
            away_score = match_data.get("awayCompetitor", {}).get("score", 0)
        elif "game" in match_data:
            game = match_data["game"]
            home_score = game.get("homeCompetitor", {}).get("score", 0)
            away_score = game.get("awayCompetitor", {}).get("score", 0)
        # If not played or both teams have zero/negative, skip
        if not (isinstance(home_score, (int, float)) and isinstance(away_score, (int, float))):
            return pd.DataFrame()
        if home_score <= 0 and away_score <= 0:
            return pd.DataFrame()

        chart = match_data['chartEvents']
        json_tiros = chart['events']
        if not json_tiros: # If events list is empty
            return pd.DataFrame()

        df = pd.DataFrame(json_tiros)

        # Enrich with readable eventType, subType, status if available
        event_types = {e["value"]: e["name"] for e in chart.get("eventTypes", [])}
        statuses = {s["id"]: s["name"] for s in chart.get("statuses", [])}
        subtypes = {s["value"]: s["name"] for s in chart.get("eventSubTypes", [])}

        if "type" in df.columns:
            df["eventTypeName"] = df["type"].map(event_types)
        if "status" in df.columns:
            df["statusName"] = df["status"].map(statuses)
        if "subType" in df.columns:
            df["subTypeName"] = df["subType"].map(subtypes)

        if 'xgot' in df.columns:
            df['xgot'] = df['xgot'].apply(lambda x: str(x).replace('-', '0') if pd.notnull(x) and isinstance(x, str) else ('0' if pd.notnull(x) else '0'))
        else:
            df['xgot'] = '0'

        if 'xg' not in df.columns:
            df['xg'] = 0.0
        else:
            df['xg'] = pd.to_numeric(df['xg'], errors='coerce').fillna(0.0)

        df['xgot'] = pd.to_numeric(df['xgot'], errors='coerce').fillna(0.0)

        # Flatten the outcome dict if present
        if 'outcome' in df.columns:
            outcols = ['y', 'z', 'id', 'name', 'x']
            for col in outcols:
                df[f'outcome_{col}'] = df['outcome'].apply(lambda o: o.get(col) if isinstance(o, dict) else None)
            df = df.rename(columns={'outcome_name': 'shot_outcome'})
            df = df.drop(columns=['outcome'])
        else:
            df['shot_outcome'] = None

        # --- Map playerId to playerName and jerseyNumber ---
        members = []
        for side in ['homeCompetitor', 'awayCompetitor']:
            try:
                members += match_data.get(side, {}).get('lineups', {}).get('members', [])
            except Exception:
                pass
        # Fallback: add match_data['members'] if present (sometimes used for bench/etc)
        if "members" in match_data and isinstance(match_data["members"], list):
            members += match_data["members"]

        player_id_to_name = {m["id"]: m.get("name") for m in members if "id" in m and "name" in m}
        player_id_to_jersey = {m["id"]: m.get("jerseyNumber") for m in members if "id" in m and "jerseyNumber" in m}

        if "playerId" in df.columns:
            df["playerName"] = df["playerId"].map(player_id_to_name)
            df["jerseyNumber"] = df["playerId"].map(player_id_to_jersey)
        else:
            df["playerName"] = None
            df["jerseyNumber"] = None

        return df
        
    def get_shotmap_enriched(self, game_id, competition_id=552):
        """
        Returns a DataFrame of events with readable eventType, status, subType, and player name columns,
        only if the match has been played (at least one team's score > 0).
        """
        match_data = self.get_match_data_by_id(game_id, competition_id)

        # Check for the correct structure
        if not (
            isinstance(match_data, dict)
            and 'game' in match_data
            and 'chartEvents' in match_data['game']
            and 'events' in match_data['game']['chartEvents']
        ):
            # Optionally: return None or empty DataFrame instead of raising
            return pd.DataFrame()
            # raise ValueError("match_data does not contain expected chartEvents/events structure.")

        game = match_data['game']

        # --- New: check that at least one score is positive and not zero ---
        home_score = game.get('homeCompetitor', {}).get('score', 0)
        away_score = game.get('awayCompetitor', {}).get('score', 0)
        if not (isinstance(home_score, (int, float)) and isinstance(away_score, (int, float))):
            # In case of missing or bad score data, treat as not played
            return pd.DataFrame()
        if home_score <= 0 and away_score <= 0:
            # Not played or both scores are zero/negative
            return pd.DataFrame()

        chart = game['chartEvents']
        chart_events = chart['events']

        df = pd.DataFrame(chart_events)

        # Build lookup dicts for event types/subtypes/statuses
        event_types = {e["value"]: e["name"] for e in chart.get("eventTypes", [])}
        statuses = {s["id"]: s["name"] for s in chart.get("statuses", [])}
        subtypes = {s["value"]: s["name"] for s in chart.get("eventSubTypes", [])}

        if "type" in df.columns:
            df["eventTypeName"] = df["type"].map(event_types)
        if "status" in df.columns:
            df["statusName"] = df["status"].map(statuses)
        if "subType" in df.columns:
            df["subTypeName"] = df["subType"].map(subtypes)

        # --- PLAYER INFO LOOKUP ---
        members = []
        try:
            members += game["homeCompetitor"]["lineups"]["members"]
        except Exception:
            pass
        try:
            members += game["awayCompetitor"]["lineups"]["members"]
        except Exception:
            pass
        if "members" in game and isinstance(game["members"], list):
            members += game["members"]

        player_id_to_name = {m["id"]: m.get("name") for m in members if "id" in m and "name" in m}
        player_id_to_jersey = {m["id"]: m.get("jerseyNumber") for m in members if "id" in m and "jerseyNumber" in m}

        if "playerId" in df.columns:
            df["playerName"] = df["playerId"].map(player_id_to_name)
            df["jerseyNumber"] = df["playerId"].map(player_id_to_jersey)

        # Handle xg/xgot columns
        if 'xgot' in df.columns:
            df['xgot'] = df['xgot'].apply(lambda x: str(x).replace('-', '0') if pd.notnull(x) and isinstance(x, str) else ('0' if pd.notnull(x) else '0'))
        else:
            df['xgot'] = '0'

        if 'xg' not in df.columns:
            df['xg'] = 0.0
        else:
            df['xg'] = pd.to_numeric(df['xg'], errors='coerce').fillna(0.0)

        df['xgot'] = pd.to_numeric(df['xgot'], errors='coerce').fillna(0.0)

        # Flatten the outcome dict if present
        if 'outcome' in df.columns:
            outcols = ['y', 'z', 'id', 'name', 'x']
            for col in outcols:
                df[f'outcome_{col}'] = df['outcome'].apply(lambda o: o.get(col) if isinstance(o, dict) else None)
            df = df.rename(columns={'outcome_name': 'shot_outcome'})
            df = df.drop(columns=['outcome'])
        else:
            df['shot_outcome'] = None

        return df
    def get_players_info(self, match_url):
        """Get players info (from match_data.members) for a certain match.

        Args:
            match_url (url): 365Scores match URL.

        Returns:
            teams_df: Player data (all members in the match) as a DataFrame.
        """
        match_data = self.get_match_data(match_url) # Uses /web/game/
        if not match_data or 'members' not in match_data or not isinstance(match_data['members'], list):
            # print(f"Warning: 'members' key not found or not a list in match_data for {match_url}")
            return pd.DataFrame() 

        teams_json = match_data['members']
        if not teams_json: 
            return pd.DataFrame()

        teams_df = pd.DataFrame(teams_json)
        return teams_df
    
    def get_team_data(self, match_url):
        """Gets basic data (name, id, color) for home and away teams.

        Args:
            match_url (str): 365Scores match URL.

        Returns:
            tuple: (home_team_dict, away_team_dict)
        """
        values = ['home', 'away']
        team_details = []
        match_data = self.get_match_data(match_url) # Uses /web/game/

        default_home = {'name': 'Unknown Home', 'id': None, 'color': None}
        default_away = {'name': 'Unknown Away', 'id': None, 'color': None}

        if not match_data:
            # print(f"Warning: match_data is empty for {match_url}. Cannot retrieve team data.")
            return default_home, default_away

        for value_type in values: # 'home' or 'away'
            competitor_key = f'{value_type}Competitor'
            if competitor_key in match_data and isinstance(match_data[competitor_key], dict):
                competitor = match_data[competitor_key]
                team_details.append({
                    'name': competitor.get('name', f'Unknown {value_type.capitalize()}'),
                    'id': competitor.get('id'),
                    'color': competitor.get('color')
                })
            else:
                # print(f"Warning: {competitor_key} data not found or not a dict in match_data for {match_url}")
                team_details.append({'name': f'Unknown {value_type.capitalize()}', 'id': None, 'color': None})
        
        home = team_details[0] if len(team_details) > 0 else default_home
        away = team_details[1] if len(team_details) > 1 else default_away
        
        return home, away
    
    def get_general_match_stats(self, match_url):  # This is the function the user was calling, uses /web/game/
        """Get general statistics for teams from a match (e.g. possession, total shots).
           This version parses the 'status' object within each competitor from the /web/game/ endpoint,
           with fallbacks to 'statistics', lineup member stats if needed, and finally to /web/game/stats/ endpoint via get_match_general_stats.

        Args:
            match_url (url): 365Scores match URL.

        Returns:
            DataFrame: Combined general stats or detailed stats if fallback.
        """
        match_data = self.get_match_data(match_url)
        sides = ['home', 'away']
        all_stats_records = []

        if not match_data:
            print(f"Warning: No match data retrieved for URL: {match_url}. Falling back to detailed stats endpoint.")
            return self._use_detailed_stats(match_url)

        for side in sides:
            competitor = match_data.get(side) or match_data.get(f"{side}Competitor")
            if not isinstance(competitor, dict):
                continue

            team_name = competitor.get('name', f"Unknown {side.capitalize()}")
            stats = None

            # Primary source: 'status'
            if isinstance(competitor.get('status'), dict):
                stats = competitor['status']
            # Secondary source: 'statistics'
            elif isinstance(competitor.get('statistics'), dict):
                stats = competitor['statistics']
            # Tertiary source: first lineup member stats
            elif (isinstance(competitor.get('lineups'), dict) and
                  isinstance(competitor['lineups'].get('members'), list) and
                  competitor['lineups']['members']):
                member = competitor['lineups']['members'][0]
                raw_stats = member.get('stats')
                if isinstance(raw_stats, (dict, list)):
                    stats = raw_stats

            if not stats:
                continue

            # Normalize stats
            if isinstance(stats, dict):
                items = stats.items()
            elif isinstance(stats, list):
                items = [(d.get('name'), d.get('value')) for d in stats if isinstance(d, dict)]
            else:
                continue

            for name, value in items:
                all_stats_records.append({
                    'name': name,
                    'value': value,
                    'team': team_name,
                    'categoryName': 'General'
                })

        if not all_stats_records:
            print(f"Warning: No stats from game endpoint. Falling back to detailed stats endpoint.")
            return self._use_detailed_stats(match_url)

        df_total = pd.DataFrame(all_stats_records)
        # Display all rows
        print(df_total.to_string(index=False))
        return df_total

    def _use_detailed_stats(self, match_url):
        # Fallback to detailed stats endpoint
        df = self.get_match_general_stats(match_url)
        if df.empty:
            return df
        df = df.rename(columns={'team_name':'team'})
        cols = ['name','categoryName','value','team']
        result = df[[c for c in cols if c in df.columns]]
        # Display all rows for detailed stats
        print(result.to_string(index=False))
        return result


    def get_player_heatmap_match(self, player_name_to_find, match_url):
        """Get player heatmap for a certain match.

        Args:
            player_name_to_find (str): Player name, must match the 'name' in match members.
            match_url (url): 365Scores match URL.

        Returns:
            PIL.Image: Heatmap image for the player, or raises MatchDoesntHaveInfo.
        """
        match_data = self.get_match_data(match_url)  # Uses /web/game/

        # 1) Retrieve all players
        all_members = match_data.get('members', [])
        if not isinstance(all_members, list):
            raise MatchDoesntHaveInfo(f"No 'members' list in match_data for {match_url}")

        df_all = pd.DataFrame(all_members)
        if df_all.empty or 'name' not in df_all.columns:
            raise MatchDoesntHaveInfo(f"Members info missing 'name' for {match_url}")

        # Find player row
        player_rows = df_all[df_all['name'] == player_name_to_find]
        if player_rows.empty:
            raise MatchDoesntHaveInfo(f"Player '{player_name_to_find}' not found in match members for {match_url}")
        player_info = player_rows.iloc[0]

        # Attempt direct heatMap
        heatmap_url = player_info.get('heatMap')

        # 2) Fallback: search in lineup members
        if not heatmap_url:
            for key in ('homeCompetitor','awayCompetitor'):
                comp = match_data.get(key, {})
                members = comp.get('lineups', {}).get('members', []) if isinstance(comp.get('lineups'), dict) else []
                for m in members:
                    if m.get('id') == player_info.get('id') and m.get('heatMap'):
                        heatmap_url = m['heatMap']
                        break
                if heatmap_url:
                    break

        if not heatmap_url:
            raise MatchDoesntHaveInfo(f"No heatmap URL available for player '{player_name_to_find}' in match {match_url}")

        # 3) Fetch and return image
        try:
            resp = requests.get(heatmap_url, headers=headers, timeout=10)
            resp.raise_for_status()
            time.sleep(3)
            return Image.open(BytesIO(resp.content))
        except Exception as e:
            raise MatchDoesntHaveInfo(f"Failed to fetch/open heatmap for '{player_name_to_find}': {e}")
        
    
    def get_game_details(self, game_id: int) -> dict:

        """
        جلب تفاصيل مباراة محددة بواسطة معرف المباراة
        
        Args:
            game_id: معرف المباراة (رقم صحيح)
            
        Returns:
            قاموس يحتوي على تفاصيل المباراة الكاملة
        """
        # معلمات الطلب الأساسية
        params = {
            'appTypeId': 5,
            'langId': 1,
            'timezoneName': 'Asia/Hebron',
            'userCountryId': 115,
            'gameId': game_id

        }
        
        # URL لتفاصيل المباراة
        base_url = 'https://webws.365scores.com/web/game/'
        
        try:
            # إرسال الطلب
            response = self.session.get(base_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            # تحويل الاستجابة إلى JSON
            game_data = response.json()
            
            # إرجاع البيانات
            return game_data
            
        except requests.exceptions.RequestException as e:
            print(f"خطأ في جلب تفاصيل المباراة: {e}")
            return {}
        
    
    def _slugify_text(self, text):
        """
        Helper function to convert text to a URL-friendly slug.
        Example: "Premier League" -> "premier-league"
        """
        if text is None:
            return ""
        text = str(text).lower()
        text = re.sub(r'\s+', '-', text)  # Replace spaces with hyphens
        text = re.sub(r'&', 'and', text) # Replace & with 'and'
        # تحافظ هذه العبارة العادية على الأحرف العربية
        text = re.sub(r'[^\w\u0600-\u06FF-]+', '', text, flags=re.UNICODE)  # Remove non-alphanumeric (incl. Arabic) characters except hyphens
        text = re.sub(r'--+', '-', text)  # Replace multiple hyphens with a single one
        text = text.strip('-') # Remove leading/trailing hyphens
        return text


    def get_public_match_url_from_game_id(self, game_id, lang_id=1, timezone_name="Asia/Hebron", user_country_id=115):
        """
        Constructs the public 365Scores match URL from a gameId.
        تقوم ببناء رابط URL العام لمباراة 365Scores من gameId.

        Args:
            game_id (int): The ID of the game. معرّف اللعبة.
            lang_id (int): Language ID for the API request. معرّف اللغة لطلب الواجهة البرمجية.
            timezone_name (str): Timezone name for the API request. اسم المنطقة الزمنية لطلب الواجهة البرمجية.
            user_country_id (int): User country ID for the API request. معرّف بلد المستخدم لطلب الواجهة البرمجية.

        Returns:
            str: The public match URL, or None if an error occurs. رابط URL العام للمباراة، أو None في حالة حدوث خطأ.
        """
        if not isinstance(game_id, int):
            try:
                game_id = int(game_id)
            except (ValueError, TypeError):
                # print(f"Error: game_id must be an integer or convertible to an integer. Received: {game_id}")
                return None

        api_url = f'https://webws.365scores.com/web/game/?appTypeId=5&langId={lang_id}&timezoneName={timezone_name}&userCountryId={user_country_id}&gameId={game_id}&topBookmaker=14'

        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            time.sleep(3)
            data = response.json()
        except requests.RequestException as e:
            # print(f"API request failed for gameId {game_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            # print(f"Failed to decode JSON for gameId {game_id}: {e}")
            return None

        if 'game' not in data:
            # print(f"No 'game' data found in API response for gameId {game_id}")
            return None
        
        game_data = data['game']

        try:
            sport_id = game_data['sportId']
            competition_name = game_data['competitionDisplayName'] # Or competitionName
            competition_id = game_data['competitionId']
            
            home_competitor = game_data['homeCompetitor']
            away_competitor = game_data['awayCompetitor']
            
            home_team_name = home_competitor['name']
            home_team_id = home_competitor['id']
            
            away_team_name = away_competitor['name']
            away_team_id = away_competitor['id']

        except KeyError as e:
            # print(f"Missing critical data in API response for gameId {game_id}: {e}")
            return None

        sport_name_slug = "unknown-sport"
        if sport_id == 1:
            sport_name_slug = "football" # كرة القدم
        elif sport_id == 2:
            sport_name_slug = "basketball" # كرة السلة
        elif sport_id == 3:
            sport_name_slug = "tennis" # التنس
        elif sport_id == 4:
            sport_name_slug = "hockey" # الهوكي (عادة هوكي الجليد)
        # Add more sport ID mappings as needed أضف المزيد من تعيينات معرّفات الرياضة حسب الحاجة
        else:
            # print(f"Warning: Sport ID {sport_id} not explicitly mapped, using '{sport_name_slug}'.")
            return None 

        comp_slug = self._slugify_text(competition_name)
        home_slug = self._slugify_text(home_team_name)
        away_slug = self._slugify_text(away_team_name)
        
        path_part_competition = f"{comp_slug}-{competition_id}"
        path_part_teams_matchup = f"{home_slug}-{away_slug}-{home_team_id}-{away_team_id}-{competition_id}"
        
        public_url = f"https://www.365scores.com/{sport_name_slug}/match/{path_part_competition}/{path_part_teams_matchup}#id={game_id}"
        
        return public_url

    def get_public_match_url_from_ids(self, matchup_ids_str, game_id, lang_id=1, timezone_name="Asia/Hebron", user_country_id=115):
        """
        Constructs the public 365Scores match URL using a pre-parsed matchup IDs string and a gameId.
        تقوم ببناء رابط URL العام لمباراة 365Scores باستخدام سلسلة معرّفات المباراة المحللة مسبقًا و gameId.

        Args:
            matchup_ids_str (str): A string containing home_id, away_id, and competition_id, separated by hyphens.
                                   (e.g., "8312-50877-552").
                                   سلسلة تحتوي على معرّف الفريق المضيف، معرّف الفريق الضيف، ومعرّف البطولة، مفصولة بشرطات.
            game_id (int or str): The ID of the game. معرّف اللعبة.
            lang_id (int): Language ID for the API request. معرّف اللغة لطلب الواجهة البرمجية.
            timezone_name (str): Timezone name for the API request. اسم المنطقة الزمنية.
            user_country_id (int): User country ID for the API request. معرّف بلد المستخدم.

        Returns:
            str: The public match URL, or None if an error occurs. رابط URL العام للمباراة، أو None في حالة حدوث خطأ.
        """
        try:
            game_id = int(game_id)
        except (ValueError, TypeError):
            # print(f"Error: game_id must be an integer or convertible to an integer. Received: {game_id}")
            return None

        if not isinstance(matchup_ids_str, str):
            # print(f"Error: matchup_ids_str must be a string. Received type: {type(matchup_ids_str)}")
            return None
            
        id_parts = matchup_ids_str.split('-')
        if len(id_parts) != 3:
            # print(f"Error: matchup_ids_str '{matchup_ids_str}' is not in the expected 'homeId-awayId-compId' format.")
            return None
        
        try:
            path_home_id = int(id_parts[0])
            path_away_id = int(id_parts[1])
            path_comp_id = int(id_parts[2])
        except ValueError:
            # print(f"Error: Could not convert parts of matchup_ids_str '{matchup_ids_str}' to integers.")
            return None

        # Fetch game data to get names and sportId
        api_url = f'https://webws.365scores.com/web/game/?appTypeId=5&langId={lang_id}&timezoneName={timezone_name}&userCountryId={user_country_id}&gameId={game_id}&topBookmaker=14'
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            time.sleep(3)
            data = response.json()
        except requests.RequestException as e:
            # print(f"API request failed for gameId {game_id} in get_public_match_url_from_ids: {e}")
            return None
        except json.JSONDecodeError as e:
            # print(f"Failed to decode JSON for gameId {game_id} in get_public_match_url_from_ids: {e}")
            return None

        if 'game' not in data:
            # print(f"No 'game' data found in API response for gameId {game_id} (get_public_match_url_from_ids)")
            return None
        
        game_data = data['game']

        try:
            sport_id = game_data['sportId']
            # Use names from API corresponding to the game_id
            competition_name_api = game_data['competitionDisplayName']
            home_team_name_api = game_data['homeCompetitor']['name']
            away_team_name_api = game_data['awayCompetitor']['name']
            
            # Optional: Verify if IDs from API match path_xxx_ids. For now, we trust path_xxx_ids for path construction
            # and API names for slugs.
            # api_comp_id = game_data['competitionId']
            # api_home_id = game_data['homeCompetitor']['id']
            # api_away_id = game_data['awayCompetitor']['id']
            # if not (api_comp_id == path_comp_id and api_home_id == path_home_id and api_away_id == path_away_id):
            # print(f"Warning: ID mismatch between provided matchup_ids_str and API data for game_id {game_id}.")
            # Decide on handling: either use API IDs for path too, or proceed with path_xxx_ids.
            # Current approach uses path_xxx_ids for the numeric parts of the URL path.

        except KeyError as e:
            # print(f"Missing critical name/sport data in API response for gameId {game_id}: {e}")
            return None

        sport_name_slug = "unknown-sport"
        if sport_id == 1:
            sport_name_slug = "football"
        elif sport_id == 2:
            sport_name_slug = "basketball"
        elif sport_id == 3:
            sport_name_slug = "tennis"
        elif sport_id == 4:
            sport_name_slug = "hockey"
        else:
            # print(f"Warning: Sport ID {sport_id} not explicitly mapped for game_id {game_id}.")
            return None 

        comp_slug = self._slugify_text(competition_name_api)
        home_slug = self._slugify_text(home_team_name_api)
        away_slug = self._slugify_text(away_team_name_api)
        
        # Construct URL using path_xxx_ids from input for the numeric ID parts in the path
        path_part_competition = f"{comp_slug}-{path_comp_id}"
        path_part_teams_matchup = f"{home_slug}-{away_slug}-{path_home_id}-{path_away_id}-{path_comp_id}"
        
        public_url = f"https://www.365scores.com/{sport_name_slug}/match/{path_part_competition}/{path_part_teams_matchup}#id={game_id}"
        
        return public_url


    def __init__(self):
        """تهيئة الجلسة وإعدادات HTTP"""
        # 1. إنشاء جلسة Requests
        self.session = requests.Session()
        
        # 2. إعداد سياسة إعادة المحاولة
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        # 3. استخدام الرؤوس من config أو البديل
        self.headers = headers
        
        # 4. إضافة رؤوس إضافية مطلوبة
        self.headers.update({
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.365scores.com/',
            'Origin': 'https://www.365scores.com'
        })
    
    def _safe_int(self, value) -> int:
        """تحويل آمن إلى عدد صحيح"""
        try:
            return int(value) if value not in [None, ''] else 0
        except (TypeError, ValueError):
            return 0
            
    def _apply_status_filter(self, df: pd.DataFrame, status_filter: str) -> pd.DataFrame:
        """تطبيق تصفية الحالة على DataFrame"""
        status_map = {
            'finished': ['FT', 'Ended', 'AET', 'Pen'],
            'upcoming': ['NS', 'Not Started', 'Postp', 'Scheduled'],
            'live': ['1H', '2H', 'HT', 'LIVE', 'ET']
        }
        valid_statuses = status_map.get(status_filter, [])
        if valid_statuses:
            return df[df['status'].isin(valid_statuses)]
        return df


    def get_competition_results_fast(
        self,
        competition_id: int,
        status_filter: str = None,
        max_workers: int = 8,
        page_size: int = 100
    ) -> dict:
        """
        جلب سريع لجميع بيانات المسابقة باستخدام التوازي
        
        Args:
            competition_id: ID المسابقة
            status_filter: نوع المباريات ('finished', 'upcoming', 'live')
            max_workers: عدد العمليات المتوازية
            page_size: عدد المباريات في كل صفحة
            
        Returns:
            قاموس يحتوي على DataFrame بالمباريات والعدد الإجمالي
        """
        # جلب الصفحة الأولى
        first_page = self.get_competition_results(
            competition_id=competition_id,
            page_size=page_size,
            fetch_all=False
        )
        
        games_df = first_page['games']
        next_token = first_page['paging'].get('next_token')
        total_games = first_page['paging'].get('total_games', 0)
        
        # حالة عدم وجود صفحات إضافية
        if not next_token or total_games <= page_size:
            if status_filter:
                games_df = self._apply_status_filter(games_df, status_filter)
            return {
                'games': games_df,
                'total_games': total_games
            }
        
        # حساب الصفحات المتبقية
        remaining_games = total_games - len(games_df)
        remaining_pages = (remaining_games + page_size - 1) // page_size
        print(f"جلب {remaining_pages} صفحة إضافية باستخدام {max_workers} عملية...")
        
        # جلب الصفحات المتبقية بشكل متوازي
        all_additional_games = []
        tokens_queue = [next_token]  # بدء بقائمة الرموز
        
        # تعبئة الرموز الأولية
        for _ in range(1, min(remaining_pages, max_workers * 2)):
            tokens_queue.append(None)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            # إرسال المهام الأولية
            for i, token in enumerate(tokens_queue):
                if token is None:
                    continue
                    
                future = executor.submit(
                    self.get_competition_results,
                    competition_id=competition_id,
                    after_game=token,
                    page_size=page_size,
                    fetch_all=False
                )
                futures[future] = i  # حفظ مؤشر الصفحة

            # معالجة النتائج عند اكتمالها
            for future in concurrent.futures.as_completed(futures):
                idx = futures[future]
                try:
                    page_result = future.result()
                    all_additional_games.extend(page_result['games'].to_dict('records'))
                    
                    # تحديث الرمز التالي إذا وجد
                    new_token = page_result['paging'].get('next_token')
                    if new_token and idx + 1 < len(tokens_queue):
                        tokens_queue[idx + 1] = new_token
                        
                        # إرسال مهمة جديدة إذا كانت متاحة
                        if idx + 1 >= len(futures) and len(futures) < remaining_pages:
                            new_future = executor.submit(
                                self.get_competition_results,
                                competition_id=competition_id,
                                after_game=new_token,
                                page_size=page_size,
                                fetch_all=False
                            )
                            futures[new_future] = idx + 1
                            
                except Exception as e:
                    print(f"خطأ في جلب الصفحة: {e}")

        # دمج جميع النتائج
        if all_additional_games:
            additional_df = pd.DataFrame(all_additional_games)
            games_df = pd.concat([games_df, additional_df], ignore_index=True)
        
        # التصفية النهائية
        if status_filter:
            games_df = self._apply_status_filter(games_df, status_filter)
        
        return {
            'games': games_df.reset_index(drop=True),
            'total_games': len(games_df)
        }


    def get_competition_results(
        self,
        competition_id: int,
        after_game: int = None,
        direction: int = 1,
        page_size: int = 20,
        fetch_all: bool = False, # سيتم تجاهل هذا إذا تم استدعاؤه من get_full_competition_results
        status_filter: str = None,
        max_pages: int = None, # سيتم تجاهل هذا إذا تم استدعاؤه من get_full_competition_results
        max_games: int = None  # سيتم تجاهل هذا إذا تم استدعاؤه من get_full_competition_results
    ) -> dict:
        params = {
            'appTypeId': 5,
            'langId': 1, # يمكن تغييره للغة العربية إذا دعت الحاجة (مثلاً 29 للغة العربية في بعض الأنظمة)
            'timezoneName': 'Asia/Hebron', # يمكن تغييره حسب الحاجة
            'userCountryId': 115, # يمكن تغييره حسب الحاجة
            'competitions': competition_id,
            'showOdds': 'false',
            #'includeTopBettingOpportunity': 0, # تعطيل إذا لم تكن هناك حاجة للرهانات
            'games': page_size,
            'direction': direction
        }
        
        if after_game:
            params['aftergame'] = after_game

        # متغيرات لتخزين النتائج والرموز
        games_data_from_api = []
        current_next_token = None
        current_prev_token = None
        total_games_from_api = 0
        
        # جلب صفحة واحدة فقط (fetch_all=False عند الاستدعاء من get_full_competition_results)
        try:
            response = self._365scores_request('games/results/', params=params)
            # response.raise_for_status() # يتم التعامل معه داخل _365scores_request
            data = response.json()
            
            games_data_from_api = data.get('games', [])
            paging_data = data.get('paging', {})
            total_games_from_api = paging_data.get('totalGames', len(games_data_from_api))

            next_page_url = paging_data.get('nextPage')
            if next_page_url:
                next_token_match = re.search(r'aftergame=(\d+)', next_page_url)
                if next_token_match:
                    current_next_token = int(next_token_match.group(1))

            prev_page_url = paging_data.get('prevPage')
            if prev_page_url:
                prev_token_match = re.search(r'aftergame=(\d+)', prev_page_url)
                if prev_token_match:
                    current_prev_token = int(prev_token_match.group(1))
        
        except (ConnectionError, json.JSONDecodeError, requests.exceptions.RequestException) as e:
            print(f"خطأ أثناء جلب صفحة نتائج المسابقة: {e}")
            # إرجاع هيكل فارغ في حالة الخطأ لضمان استمرار get_full_competition_results
            return {
                'games': pd.DataFrame(),
                'paging': {
                    'next_token': None,
                    'prev_token': None,
                    'total_games': 0
                }
            }

        game_records = []
        for game in games_data_from_api:
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            record = {
                'game_id': game.get('id'),
                'season': game.get('seasonNum'),
                'round': game.get('roundName'),
                'status': game.get('shortStatusText'),
                'start_time_raw': game.get('startTime'), # وقت المباراة الأصلي للفرز
                'home_team': home.get('name'),
                'home_score': self._safe_int(home.get('score')),
                'away_team': away.get('name'),
                'away_score': self._safe_int(away.get('score')),
                'competition_id': game.get('competitionId'), # إضافة معرف المسابقة
                'sport_id': game.get('sportId') # إضافة معرف الرياضة
            }
            game_records.append(record)
        
        games_df = pd.DataFrame(game_records)
        
        if status_filter:
            games_df = self._apply_status_filter(games_df, status_filter)
        
        # إضافة أعمدة التاريخ والوقت المنسقة مع الاحتفاظ بالوقت الأصلي
        if 'start_time_raw' in games_df.columns and not games_df.empty:
            games_df['datetime_obj'] = pd.to_datetime(games_df['start_time_raw'], errors='coerce')
            # التعامل مع الحالات التي قد يكون فيها datetime_obj فارغًا تمامًا
            if not games_df['datetime_obj'].isnull().all():
                games_df['start_date'] = games_df['datetime_obj'].dt.strftime('%Y-%m-%d')
                games_df['start_time'] = games_df['datetime_obj'].dt.strftime('%H:%M')
            else:
                games_df['start_date'] = None
                games_df['start_time'] = None
        else: # إذا لم يكن العمود موجودًا أو كان فارغًا
            games_df['start_date'] = None
            games_df['start_time'] = None
            if 'datetime_obj' not in games_df.columns: # تأكد من وجوده للفرز لاحقًا حتى لو كان فارغًا
                 games_df['datetime_obj'] = pd.NaT


        return {
            'games': games_df,
            'paging': {
                'next_token': current_next_token,
                'prev_token': current_prev_token,
                'total_games': total_games_from_api
            }
        }
    
    def _365scores_request(self, path: str, params: dict = None) -> requests.Response:
        """
        إرسال طلب إلى واجهة برمجة تطبيقات 365Scores باستخدام المسار المحدد
        
        Args:
            path (str): مسار API النسبي (مثال: 'games/results/')
            params (dict): معلمات اختيارية للطلب
            
        Returns:
            requests.Response: كائن الاستجابة
        """
        base_url = f'https://webws.365scores.com/web/{path}'
        
        try:
            response = self.session.get(
                base_url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            time.sleep(0.3)
            return response
            
        except requests.RequestException as e:
            raise ConnectionError(f"فشل في الاتصال بواجهة برمجة التطبيقات: {e}")

    def get_full_competition_results(self, competition_id: int, page_size: int = 50) -> pd.DataFrame:
        """
        جلب جميع مباريات المسابقة من أول مباراة إلى آخر مباراة.
        تم تعديل هذه الدالة لتكون أكثر قوة في جلب جميع الصفحات.
        
        Args:
            competition_id: معرف المسابقة
            page_size: عدد المباريات في الصفحة (تم تقليله قليلاً لتجنب أخطاء المهلة المحتملة مع عدد كبير)
            
        Returns:
            DataFrame: يحتوي على جميع مباريات المسابقة مرتبة من الأقدم إلى الأحدث
        """
        all_games_dfs = []
        processed_game_ids = set()

        # 1. جلب الصفحة الأولية (أحدث المباريات)
        print(f"جاري جلب الصفحة الأولية للمسابقة {competition_id}...")
        initial_page_data = self.get_competition_results(
            competition_id=competition_id,
            page_size=page_size,
            direction=1, # أحدث المباريات
            fetch_all=False # صفحة واحدة فقط
        )

        if initial_page_data and not initial_page_data['games'].empty:
            df_initial = initial_page_data['games']
            new_games = df_initial[~df_initial['game_id'].isin(processed_game_ids)]
            if not new_games.empty:
                all_games_dfs.append(new_games)
                processed_game_ids.update(new_games['game_id'])
            current_prev_token = initial_page_data['paging'].get('prev_token')
            current_next_token = initial_page_data['paging'].get('next_token') # للاحتياط إذا كانت هناك مباريات أحدث
        else:
            print(f"لم يتم العثور على مباريات في الصفحة الأولية للمسابقة {competition_id}.")
            return pd.DataFrame()

        # 2. جلب المباريات الأقدم (بالسير للخلف)
        print("جاري جلب المباريات الأقدم...")
        page_count_older = 0
        while current_prev_token:
            page_count_older += 1
            print(f"  جلب صفحة المباريات الأقدم رقم {page_count_older} (الرمز: {current_prev_token})...")
            page_data = self.get_competition_results(
                competition_id=competition_id,
                after_game=current_prev_token,
                direction=-1, # الاتجاه للخلف (أقدم)
                page_size=page_size,
                fetch_all=False
            )
            if page_data and not page_data['games'].empty:
                df_page = page_data['games']
                new_games = df_page[~df_page['game_id'].isin(processed_game_ids)]
                if not new_games.empty:
                    all_games_dfs.append(new_games)
                    processed_game_ids.update(new_games['game_id'])
                
                current_prev_token = page_data['paging'].get('prev_token')
                if not current_prev_token:
                    print("    لا يوجد المزيد من المباريات الأقدم.")
                    break # لا يوجد رمز تالي للصفحات الأقدم
                if len(new_games) < page_size and page_data['paging'].get('total_games', 0) > 0: 
                    # إذا كانت الصفحة غير ممتلئة، قد يكون هذا هو آخر رمز سابق صالح
                    # أو قد يكون هناك خطأ في API، لذا نتحقق بحذر
                    print(f"    تم جلب {len(new_games)} مباراة، قد تكون هذه آخر صفحة أقدم.")
            else:
                print("    لم يتم العثور على مباريات في هذه الصفحة الأقدم أو حدث خطأ.")
                break # خطأ أو لا توجد بيانات

        # 3. جلب المباريات الأحدث (إذا كانت الصفحة الأولية ليست الأحدث تمامًا - نادرًا ما يحدث للنتائج)
        # هذا الجزء للاحتياط
        print("جاري جلب المباريات الأحدث (إذا وجدت)...")
        page_count_newer = 0
        while current_next_token:
            page_count_newer +=1
            print(f"  جلب صفحة المباريات الأحدث رقم {page_count_newer} (الرمز: {current_next_token})...")
            page_data = self.get_competition_results(
                competition_id=competition_id,
                after_game=current_next_token,
                direction=1, # الاتجاه للأمام (أحدث)
                page_size=page_size,
                fetch_all=False
            )
            if page_data and not page_data['games'].empty:
                df_page = page_data['games']
                new_games = df_page[~df_page['game_id'].isin(processed_game_ids)]
                if not new_games.empty:
                    all_games_dfs.append(new_games)
                    processed_game_ids.update(new_games['game_id'])

                current_next_token = page_data['paging'].get('next_token')
                if not current_next_token:
                    print("    لا يوجد المزيد من المباريات الأحدث.")
                    break
            else:
                print("    لم يتم العثور على مباريات في هذه الصفحة الأحدث أو حدث خطأ.")
                break
        
        if not all_games_dfs:
            print(f"لم يتم تجميع أي بيانات مباريات للمسابقة {competition_id}.")
            return pd.DataFrame()

        final_df = pd.concat(all_games_dfs, ignore_index=True)
        
        # إزالة التكرارات النهائية (احتياطي إضافي)
        final_df.drop_duplicates(subset=['game_id'], keep='first', inplace=True)

        # الفرز النهائي حسب وقت المباراة
        # تأكد من أن عمود 'datetime_obj' موجود ويحتوي على كائنات datetime للفرز
        if 'datetime_obj' in final_df.columns and not final_df['datetime_obj'].isnull().all():
            final_df = final_df.sort_values('datetime_obj', ascending=True).reset_index(drop=True)
        else:
            print("تحذير: لا يمكن الفرز حسب وقت المباراة، عمود 'datetime_obj' مفقود أو فارغ.")
            # محاولة الفرز بـ game_id كحل بديل إذا فشل الفرز بالوقت
            if 'game_id' in final_df.columns:
                final_df = final_df.sort_values('game_id', ascending=True).reset_index(drop=True)


        print(f"تم جلب ما مجموعه {len(final_df)} مباراة فريدة بعد ترقيم الصفحات للمسابقة {competition_id}.")
        return final_df
