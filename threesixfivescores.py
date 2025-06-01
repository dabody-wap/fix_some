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
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor

try:
    from .functions import get_possible_leagues_for_page
    from .exceptions import MatchDoesntHaveInfo
    from .config import headers
except ImportError:
    def get_possible_leagues_for_page(league, none, page): return {league: {'id': 'mock_id'}}
    class MatchDoesntHaveInfo(Exception): pass
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ar,en-US;q=0.9,en;q=0.8",
        "origin": "https://www.365scores.com",
        "referer": "https://www.365scores.com/",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 ...",
    }

    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_url = {executor.submit(fetch_url, url): url for url in urls}
        for future in as_completed(future_to_url):
            url, data = future.result()
            if data is not None:
                results.append(data)

    
class ThreeSixFiveScores:
    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.headers = headers
        self.headers.update({
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.365scores.com/',
            'Origin': 'https://www.365scores.com'
        })

    ##############################
    # Shared/utility/private methods
    ##############################

    def _fetch_match_data(self, game_id, competition_id=None, matchup_id=None):
        api_url = (
            f'https://webws.365scores.com/web/game/?appTypeId=5&langId=1'
            f'&timezoneName=America/Buenos_Aires&userCountryId=382&gameId={game_id}'
        )
        if competition_id:
            api_url += f'&competitions={competition_id}'
        if matchup_id:
            api_url += f'&matchupId={matchup_id}'
        api_url += '&topBookmaker=14'
        try:
            response = requests.get(api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(3)
            return response.json()
        except requests.RequestException:
            return {}
        except json.JSONDecodeError:
            return {}

    def _slugify_text(self, text):
        if text is None:
            return ""
        text = str(text).lower()
        text = re.sub(r'\s+', '-', text)
        text = re.sub(r'&', 'and', text)
        text = re.sub(r'[^\w\u0600-\u06FF-]+', '', text, flags=re.UNICODE)
        text = re.sub(r'--+', '-', text)
        text = text.strip('-')
        return text

    def _build_public_match_url_parts(self, sport_id, competition_name, competition_id, home_team_name, home_team_id, away_team_name, away_team_id, game_id):
        sport_name_slug = "unknown-sport"
        if sport_id == 1: sport_name_slug = "football"
        elif sport_id == 2: sport_name_slug = "basketball"
        elif sport_id == 3: sport_name_slug = "tennis"
        elif sport_id == 4: sport_name_slug = "hockey"
        comp_slug = self._slugify_text(competition_name)
        home_slug = self._slugify_text(home_team_name)
        away_slug = self._slugify_text(away_team_name)
        path_part_competition = f"{comp_slug}-{competition_id}"
        path_part_teams_matchup = f"{home_slug}-{away_slug}-{home_team_id}-{away_team_id}-{competition_id}"
        return f"https://www.365scores.com/{sport_name_slug}/match/{path_part_competition}/{path_part_teams_matchup}#id={game_id}"

    def _extract_members(self, game_or_match_data):
        members = []
        try:
            members += game_or_match_data.get("homeCompetitor", {}).get("lineups", {}).get("members", [])
        except Exception:
            pass
        try:
            members += game_or_match_data.get("awayCompetitor", {}).get("lineups", {}).get("members", [])
        except Exception:
            pass
        # fallback to global 'members'
        if "members" in game_or_match_data and isinstance(game_or_match_data["members"], list):
            members += game_or_match_data["members"]
        return members

    def _process_shotmap_dataframe(self, chart, game=None):
        events = chart.get('events', [])
        if not events:
            return pd.DataFrame()
        df = pd.DataFrame(events)
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
        if 'outcome' in df.columns:
            outcols = ['y', 'z', 'id', 'name', 'x']
            for col in outcols:
                df[f'outcome_{col}'] = df['outcome'].apply(lambda o: o.get(col) if isinstance(o, dict) else None)
            df = df.rename(columns={'outcome_name': 'shot_outcome'})
            df = df.drop(columns=['outcome'])
        else:
            df['shot_outcome'] = None
        if game is not None:
            members = self._extract_members(game)
            player_id_to_name = {m["id"]: m.get("name") for m in members if "id" in m and "name" in m}
            player_id_to_jersey = {m["id"]: m.get("jerseyNumber") for m in members if "id" in m and "jerseyNumber" in m}
            if "playerId" in df.columns:
                df["playerName"] = df["playerId"].map(player_id_to_name)
                df["jerseyNumber"] = df["playerId"].map(player_id_to_jersey)
        return df

    def _safe_int(self, value) -> int:
        try:
            return int(value) if value not in [None, ''] else 0
        except (TypeError, ValueError):
            return 0

    ##############################
    # Public methods (refactored)
    ##############################

    def parse_dataframe(self, objeto):
        if isinstance(objeto, dict) and 'rows' in objeto and 'name' in objeto:
            stat_category_name = objeto['name']
            df = pd.DataFrame(objeto['rows'])
            df['stat_category'] = stat_category_name
            return df
        return pd.DataFrame()

    def get_league_top_players_stats(self, league):
        leagues = get_possible_leagues_for_page(league, None, '365Scores')
        if league not in leagues or 'id' not in leagues[league]:
            return pd.DataFrame()
        league_id = leagues[league]['id']
        try:
            response = requests.get(f'https://webws.365scores.com/web/stats/?appTypeId=5&langId=1&timezoneName=America/Buenos_Aires&userCountryId=382&competitions={league_id}', headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(3)
            stats_data = response.json()
        except requests.RequestException:
            return pd.DataFrame()
        except json.JSONDecodeError:
            return pd.DataFrame()
        if 'stats' not in stats_data or not isinstance(stats_data['stats'], list):
            return pd.DataFrame()
        general_stats_list = stats_data['stats']
        total_df = pd.DataFrame()
        for stat_group_object in general_stats_list:
            stats_df = self.parse_dataframe(stat_group_object)
            if not stats_df.empty:
                total_df = pd.concat([total_df, stats_df], ignore_index=True)
        return total_df

    def get_ids(self, match_url):
        match_id1 = re.search(r'-(\d+-\d+-\d+)', match_url)
        id_1 = match_id1.group(1) if match_id1 else None
        match_id2 = re.search(r'[#/]id=(\d+)', match_url)
        if not match_id2:
            match_id2 = re.search(r'/(\d+)$', match_url.split('#')[0].split('?')[0])
        id_2 = match_id2.group(1) if match_id2 else None
        return id_1, id_2

    def get_match_data(self, match_url):
        matchup_id, game_id = self.get_ids(match_url)
        if not game_id:
            return {}
        data = self._fetch_match_data(game_id, matchup_id=matchup_id)
        return data.get('game', {}) if 'game' in data else {}

    def get_match_data_by_id(self, game_id, competition_id="any id"):
        data = self._fetch_match_data(game_id, competition_id=competition_id)
        return data

    def get_requests_stats(self, match_url):
        _, game_id = self.get_ids(match_url)
        if not game_id:
            return None
        try:
            response = requests.get(f'https://webws.365scores.com/web/game/stats/?appTypeId=5&langId=1&timezoneName=America/Buenos_Aires&userCountryId=382&games={game_id}', headers=self.headers, timeout=10)
            response.raise_for_status()
            time.sleep(3)
            return response
        except requests.RequestException:
            return None

    def get_match_general_stats(self, match_url):
        response_obj = self.get_requests_stats(match_url)
        if response_obj is None:
            return pd.DataFrame()
        try:
            response_data = response_obj.json()
        except json.JSONDecodeError:
            return pd.DataFrame()
        if 'statistics' not in response_data or not isinstance(response_data['statistics'], list) or \
           'competitors' not in response_data or not isinstance(response_data['competitors'], list) or \
           len(response_data['competitors']) < 2:
            return pd.DataFrame()
        match_stats_list = response_data['statistics']
        if not match_stats_list:
            return pd.DataFrame()
        match_stats_df = pd.DataFrame(match_stats_list)
        if match_stats_df.empty or 'competitorId' not in match_stats_df.columns:
            return match_stats_df
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
        response_obj = self.get_requests_stats(match_url)
        if response_obj is None:
            raise MatchDoesntHaveInfo(f"Failed to get response for time stats: {match_url}")
        try:
            response_data = response_obj.json()
        except json.JSONDecodeError:
            raise MatchDoesntHaveInfo(f"Failed to decode JSON for time stats: {match_url}")
        if 'actualGameStatistics' not in response_data:
            raise MatchDoesntHaveInfo(f"actualGameStatistics not found in response: {match_url}")
        return response_data['actualGameStatistics']

    def get_match_shotmap(self, match_url):
        match_data = self.get_match_data(match_url)
        if not match_data or 'chartEvents' not in match_data or 'events' not in match_data.get('chartEvents', {}):
            raise MatchDoesntHaveInfo(f"Shotmap data (chartEvents or events) not found: {match_url}")
        # Check for positive, non-zero result
        home_score = 0
        away_score = 0
        if "homeCompetitor" in match_data and isinstance(match_data["homeCompetitor"], dict):
            home_score = match_data["homeCompetitor"].get("score", 0)
            away_score = match_data.get("awayCompetitor", {}).get("score", 0)
        elif "game" in match_data:
            game = match_data["game"]
            home_score = game.get("homeCompetitor", {}).get("score", 0)
            away_score = game.get("awayCompetitor", {}).get("score", 0)
        if not (isinstance(home_score, (int, float)) and isinstance(away_score, (int, float))):
            return pd.DataFrame()
        if home_score <= 0 and away_score <= 0:
            return pd.DataFrame()
        chart = match_data['chartEvents']
        return self._process_shotmap_dataframe(chart, game=match_data)

    def get_shotmap_enriched(self, game_id, competition_id="552"):
        match_data = self.get_match_data_by_id(game_id, competition_id)
        if not (
            isinstance(match_data, dict)
            and 'game' in match_data
            and 'chartEvents' in match_data['game']
            and 'events' in match_data['game']['chartEvents']
        ):
            return pd.DataFrame()
        game = match_data['game']
        home_score = game.get('homeCompetitor', {}).get('score', 0)
        away_score = game.get('awayCompetitor', {}).get('score', 0)
        if not (isinstance(home_score, (int, float)) and isinstance(away_score, (int, float))):
            return pd.DataFrame()
        if home_score <= 0 and away_score <= 0:
            return pd.DataFrame()
        chart = game['chartEvents']
        return self._process_shotmap_dataframe(chart, game=game)

    def get_players_info(self, match_url):
        match_data = self.get_match_data(match_url)
        if not match_data or 'members' not in match_data or not isinstance(match_data['members'], list):
            return pd.DataFrame() 
        teams_json = match_data['members']
        if not teams_json: 
            return pd.DataFrame()
        teams_df = pd.DataFrame(teams_json)
        return teams_df

    def get_team_data(self, match_url):
        values = ['home', 'away']
        team_details = []
        match_data = self.get_match_data(match_url)
        default_home = {'name': 'Unknown Home', 'id': None, 'color': None}
        default_away = {'name': 'Unknown Away', 'id': None, 'color': None}
        if not match_data:
            return default_home, default_away
        for value_type in values:
            competitor_key = f'{value_type}Competitor'
            if competitor_key in match_data and isinstance(match_data[competitor_key], dict):
                competitor = match_data[competitor_key]
                team_details.append({
                    'name': competitor.get('name', f'Unknown {value_type.capitalize()}'),
                    'id': competitor.get('id'),
                    'color': competitor.get('color')
                })
            else:
                team_details.append({'name': f'Unknown {value_type.capitalize()}', 'id': None, 'color': None})
        home = team_details[0] if len(team_details) > 0 else default_home
        away = team_details[1] if len(team_details) > 1 else default_away
        return home, away

    def get_general_match_stats(self, match_url):
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
            if isinstance(competitor.get('status'), dict):
                stats = competitor['status']
            elif isinstance(competitor.get('statistics'), dict):
                stats = competitor['statistics']
            elif (isinstance(competitor.get('lineups'), dict) and
                  isinstance(competitor['lineups'].get('members'), list) and
                  competitor['lineups']['members']):
                member = competitor['lineups']['members'][0]
                raw_stats = member.get('stats')
                if isinstance(raw_stats, (dict, list)):
                    stats = raw_stats
            if not stats:
                continue
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
        print(df_total.to_string(index=False))
        return df_total

    def _use_detailed_stats(self, match_url):
        df = self.get_match_general_stats(match_url)
        if df.empty:
            return df
        df = df.rename(columns={'team_name':'team'})
        cols = ['name','categoryName','value','team']
        result = df[[c for c in cols if c in df.columns]]
        print(result.to_string(index=False))
        return result

    def get_player_heatmap_match(self, player_name_to_find, match_url):
        match_data = self.get_match_data(match_url)
        all_members = match_data.get('members', [])
        if not isinstance(all_members, list):
            raise MatchDoesntHaveInfo(f"No 'members' list in match_data for {match_url}")
        df_all = pd.DataFrame(all_members)
        if df_all.empty or 'name' not in df_all.columns:
            raise MatchDoesntHaveInfo(f"Members info missing 'name' for {match_url}")
        player_rows = df_all[df_all['name'] == player_name_to_find]
        if player_rows.empty:
            raise MatchDoesntHaveInfo(f"Player '{player_name_to_find}' not found in match members for {match_url}")
        player_info = player_rows.iloc[0]
        heatmap_url = player_info.get('heatMap')
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
        try:
            resp = requests.get(heatmap_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            time.sleep(3)
            return Image.open(BytesIO(resp.content))
        except Exception as e:
            raise MatchDoesntHaveInfo(f"Failed to fetch/open heatmap for '{player_name_to_find}': {e}")

    # --- All competition results and paging functions remain as in your original ---
    def _apply_status_filter(self, df: pd.DataFrame, status_filter: str) -> pd.DataFrame:
        status_map = {
            'finished': ['FT', 'Ended', 'AET', 'Pen'],
            'upcoming': ['NS', 'Not Started', 'Postp', 'Scheduled'],
            'live': ['1H', '2H', 'HT', 'LIVE', 'ET']
        }
        valid_statuses = status_map.get(status_filter, [])
        if valid_statuses:
            return df[df['status'].isin(valid_statuses)]
        return df

    def get_competition_results(
        self,
        competition_id: int,
        after_game: int = None,
        direction: int = 1,
        page_size: int = 20,
        fetch_all: bool = False,
        status_filter: str = None,
        max_pages: int = None,
        max_games: int = None
    ) -> dict:
        params = {
            'appTypeId': 5,
            'langId': 1,
            'timezoneName': 'Asia/Hebron',
            'userCountryId': 115,
            'competitions': competition_id,
            'showOdds': 'false',
            'games': page_size,
            'direction': direction
        }
        if after_game:
            params['aftergame'] = after_game
        games_data_from_api = []
        current_next_token = None
        current_prev_token = None
        total_games_from_api = 0
        try:
            response = self._365scores_request('games/results/', params=params)
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
                'start_time_raw': game.get('startTime'),
                'home_team': home.get('name'),
                'home_score': self._safe_int(home.get('score')),
                'away_team': away.get('name'),
                'away_score': self._safe_int(away.get('score')),
                'competition_id': game.get('competitionId'),
                'sport_id': game.get('sportId')
            }
            game_records.append(record)
        games_df = pd.DataFrame(game_records)
        if status_filter:
            games_df = self._apply_status_filter(games_df, status_filter)
        if 'start_time_raw' in games_df.columns and not games_df.empty:
            games_df['datetime_obj'] = pd.to_datetime(games_df['start_time_raw'], errors='coerce')
            if not games_df['datetime_obj'].isnull().all():
                games_df['start_date'] = games_df['datetime_obj'].dt.strftime('%Y-%m-%d')
                games_df['start_time'] = games_df['datetime_obj'].dt.strftime('%H:%M')
            else:
                games_df['start_date'] = None
                games_df['start_time'] = None
        else:
            games_df['start_date'] = None
            games_df['start_time'] = None
            if 'datetime_obj' not in games_df.columns:
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


    def get_full_competition_results(self, competition_id: int, page_size: int = 50, max_pages: int = 1000, max_games: int = None) -> pd.DataFrame:
        all_games_dfs = []
        processed_game_ids = set()
        seen_next_tokens = set()
        seen_prev_tokens = set()
        print(f"جاري جلب الصفحة الأولية للمسابقة {competition_id}...")
        initial_page_data = self.get_competition_results(
            competition_id=competition_id,
            page_size=page_size,
            direction=1,
            fetch_all=False
        )
        if initial_page_data and not initial_page_data['games'].empty:
            df_initial = initial_page_data['games']
            new_games = df_initial[~df_initial['game_id'].isin(processed_game_ids)]
            if not new_games.empty:
                all_games_dfs.append(new_games)
                processed_game_ids.update(new_games['game_id'])
            current_prev_token = initial_page_data['paging'].get('prev_token')
            current_next_token = initial_page_data['paging'].get('next_token')
        else:
            print(f"لم يتم العثور على مباريات في الصفحة الأولية للمسابقة {competition_id}.")
            return pd.DataFrame()

        # Older pages
        page_count_older = 0
        while current_prev_token:
            if page_count_older >= max_pages:
                print("تجاوز الحد الأقصى لعدد الصفحات (الأقدم). إيقاف الجلب.")
                break
            if current_prev_token in seen_prev_tokens:
                print("تم اكتشاف رمز صفحة مكرر (الأقدم). إيقاف الجلب لتجنب الحلقة اللانهائية.")
                break
            seen_prev_tokens.add(current_prev_token)
            page_count_older += 1
            page_data = self.get_competition_results(
                competition_id=competition_id,
                after_game=current_prev_token,
                direction=-1,
                page_size=page_size,
                fetch_all=False
            )
            if page_data and not page_data['games'].empty:
                df_page = page_data['games']
                new_games = df_page[~df_page['game_id'].isin(processed_game_ids)]
                if not new_games.empty:
                    all_games_dfs.append(new_games)
                    processed_game_ids.update(new_games['game_id'])
                if max_games and len(processed_game_ids) >= max_games:
                    print("تجاوز الحد الأقصى لعدد المباريات. إيقاف الجلب.")
                    break
                current_prev_token = page_data['paging'].get('prev_token')
                if not current_prev_token:
                    break
            else:
                break

        # Newer pages
        page_count_newer = 0
        while current_next_token:
            if page_count_newer >= max_pages:
                print("تجاوز الحد الأقصى لعدد الصفحات (الأحدث). إيقاف الجلب.")
                break
            if current_next_token in seen_next_tokens:
                print("تم اكتشاف رمز صفحة مكرر (الأحدث). إيقاف الجلب لتجنب الحلقة اللانهائية.")
                break
            seen_next_tokens.add(current_next_token)
            page_count_newer += 1
            page_data = self.get_competition_results(
                competition_id=competition_id,
                after_game=current_next_token,
                direction=1,
                page_size=page_size,
                fetch_all=False
            )
            if page_data and not page_data['games'].empty:
                df_page = page_data['games']
                new_games = df_page[~df_page['game_id'].isin(processed_game_ids)]
                if not new_games.empty:
                    all_games_dfs.append(new_games)
                    processed_game_ids.update(new_games['game_id'])
                if max_games and len(processed_game_ids) >= max_games:
                    print("تجاوز الحد الأقصى لعدد المباريات. إيقاف الجلب.")
                    break
                current_next_token = page_data['paging'].get('next_token')
                if not current_next_token:
                    break
            else:
                break

        if not all_games_dfs:
            print(f"لم يتم تجميع أي بيانات مباريات للمسابقة {competition_id}.")
            return pd.DataFrame()
        final_df = pd.concat(all_games_dfs, ignore_index=True)
        final_df.drop_duplicates(subset=['game_id'], keep='first', inplace=True)
        if 'datetime_obj' in final_df.columns and not final_df['datetime_obj'].isnull().all():
            final_df = final_df.sort_values('datetime_obj', ascending=True).reset_index(drop=True)
        else:
            if 'game_id' in final_df.columns:
                final_df = final_df.sort_values('game_id', ascending=True).reset_index(drop=True)
        print(f"تم جلب ما مجموعه {len(final_df)} مباراة فريدة بعد ترقيم الصفحات للمسابقة {competition_id}.")
        return final_df

    def get_competition_results_fast(
        self,
        competition_id: int,
        status_filter: str = None,
        max_workers: int = 8,
        page_size: int = 100,
        max_pages: int = 1000,
        max_games: int = None,
    ) -> dict:
        first_page = self.get_competition_results(
            competition_id=competition_id,
            page_size=page_size,
            fetch_all=False
        )
        games_df = first_page['games']
        next_token = first_page['paging'].get('next_token')
        total_games = first_page['paging'].get('total_games', 0)
        if not next_token or total_games <= page_size:
            if status_filter:
                games_df = self._apply_status_filter(games_df, status_filter)
            return {
                'games': games_df,
                'total_games': total_games
            }
        remaining_games = total_games - len(games_df)
        remaining_pages = (remaining_games + page_size - 1) // page_size
        all_additional_games = []
        tokens_queue = [next_token]
        seen_tokens = set(tokens_queue)
        page_counter = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for i, token in enumerate(tokens_queue):
                if token is None:
                    continue
                if max_pages and page_counter >= max_pages:
                    break
                if token in seen_tokens:
                    continue
                future = executor.submit(
                    self.get_competition_results,
                    competition_id=competition_id,
                    after_game=token,
                    page_size=page_size,
                    fetch_all=False
                )
                futures[future] = i
                seen_tokens.add(token)
                page_counter += 1
            for future in concurrent.futures.as_completed(futures):
                idx = futures[future]
                try:
                    page_result = future.result()
                    all_additional_games.extend(page_result['games'].to_dict('records'))
                    new_token = page_result['paging'].get('next_token')
                    if new_token and idx + 1 < len(tokens_queue):
                        tokens_queue[idx + 1] = new_token
                        if idx + 1 >= len(futures) and len(futures) < remaining_pages:
                            tokens_queue.append(new_token)
                            seen_tokens.add(new_token)
                except Exception as e:
                    print(f"خطأ في جلب الصفحة: {e}")
        if all_additional_games:
            additional_df = pd.DataFrame(all_additional_games)
            games_df = pd.concat([games_df, additional_df], ignore_index=True)
        if status_filter:
            games_df = self._apply_status_filter(games_df, status_filter)
        if max_games and len(games_df) > max_games:
            games_df = games_df.head(max_games)
        return {
            'games': games_df.reset_index(drop=True),
            'total_games': len(games_df)
        }
    
