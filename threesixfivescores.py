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
from urllib.parse import urlparse, parse_qs, urljoin, urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from tqdm import tqdm
from typing import Any, Optional, Dict, List, Union
from IPython.display import display


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# في ملف threesixfivescores.py
# في ملف threesixfivescores.py
try:
    from .functions import get_possible_leagues_for_page
    from .exceptions import MatchDoesntHaveInfo   # الاستيراد من المصدر الأساسي
    from .config import headers
    _FALLBACK_MODE = False
except ImportError:
    # FALLBACK IMPLEMENTATIONS
    from .exceptions import MatchDoesntHaveInfo   # ✅ الاستيراد يتكرر هنا كمان
    _FALLBACK_MODE = True
 
    def get_possible_leagues_for_page(league, season, page):
        """
        Fallback implementation for get_possible_leagues_for_page function
        Returns comprehensive league data that matches the expected format from functions.py
        """
        # Full league database from functions.py
        all_leagues = {
            '365Scores': {
                'Argentina Copa de la Liga': {'id': 7214, 'seasons': None},
                'Primera Division Argentina': {'id': 72, 'seasons': None},
                'Primera Nacional Argentina': {'id': 419, 'seasons': None},
                'Brasileirao': {'id': 113, 'seasons': None},
                'Champions League': {'id': 572, 'seasons': None},
                'Primera Division Colombia': {'id': 620, 'seasons': None},
                'Copa America': {'id': 595, 'seasons': None},
                'Egyptian Premier League': {'id': 552, 'seasons': None},
                'Euros': {'id': 6316, 'seasons': None}
            },
            'Fbref': {
                'Copa de la Liga': {'id': 905, 'slug': 'Copa-de-la-Liga-Profesional'},
                'Primera Division Argentina': {'id': 21, 'slug': 'Primera-Division'},
                'Primera Division Uruguay': {'id': 45, 'slug': 'Primera-Division'},
                'Brasileirao': {'id': 24, 'slug': 'Serie-A'},
                'Brasileirao B': {'id': 38, 'slug': 'Serie-B'},
                'Primera Division Colombia': {'id': 41, 'slug': 'Primera-A'},
                'Primera Division Chile': {'id': 35, 'slug': 'Primera-Division'},
                'Primera Division Peru': {'id': 44, 'slug': 'Liga-1'},
                'Primera Division Venezuela': {'id': 105, 'slug': 'Liga-FUTVE'},
                'Primera Division Ecuador': {'id': 58, 'slug': 'Serie-A'},
                'Primera Division Bolivia': {'id': 74, 'slug': 'Bolivian-Primera-Division'},
                'Primera Division Paraguay': {'id': 61, 'slug': 'Primera-Division'},
                'MLS': {'id': 22, 'slug': 'Major-League-Soccer'},
                'USL Championship': {'id': 73, 'slug': 'USL-Championship'},
                'Premier League': {'id': 9, 'slug': 'Premier-League'},
                'La Liga': {'id': 12, 'slug': 'La-Liga'},
                'Ligue 1': {'id': 13, 'slug': 'Ligue-1'},
                'Bundesliga': {'id': 20, 'slug': 'Bundesliga'},
                'Serie A': {'id': 11, 'slug': 'Serie-A'},
                'Eredivise': {'id': 23, 'slug': 'Eredivise'},
                'Primeira Liga Portugal': {'id': 32, 'slug': 'Primeira-Liga'},
                'Saudi League': {'id': 70, 'slug': 'Saudi-Professional-League'},
                'EFL Championship': {'id': 10, 'slug': 'Championship'},
                'La Liga 2': {'id': 17, 'slug': 'Segunda-Division'},
                'J1 League': {'id': 25, 'slug': 'J1-League'},
                'Europa League': {'id': 19, 'slug': 'Europa-League'},
                'Conference League': {'id': 882, 'slug': 'Conference-League'},
                'Copa Libertadores': {'id': 14, 'slug': 'Copa-Libertadores'},
                'Liga MX': {'id': 31, 'slug': 'Liga-MX'}
            },
            'Sofascore': {
                'Argentina Liga Profesional': {'id': 155},
                'Argentina Copa de la Liga Profesional': {'id': 13475},
                'Argentina Primera Nacional': {'id': 703},
                'Brasileirao Serie A': {'id': 325},
                'Bolivia Division Profesional': {'id': 16736},
                'Chile Primera Division': {'id': 11653},
                'Colombia Primera A Apertura': {'id': 11539},
                'Colombia Primera A Clausura': {'id': 11536},
                'Ecuador LigaPro': {'id': 240},
                'Mexico LigaMX Apertura': {'id': 11621},
                'Mexico LigaMX Clausura': {'id': 11620},
                'Peru Liga 1': {'id': 406},
                'Uruguay Primera Division': {'id': 278},
                'Venezuela Primera Division': {'id': 231},
                'World Cup': {'id': 16},
                'Euros': {'id': 1},
                'Copa America': {'id': 133},
                'Premier League': {'id': 17},
                'La Liga': {'id': 8},
                'Bundesliga': {'id': 35},
                'Serie A': {'id': 23},
                'Ligue 1': {'id': 34},
                'Copa Libertadores': {'id': 384},
                'Copa Sudamericana': {'id': 480},
                'MLS': {'id': 242},
                'Saudi Pro League': {'id': 955},
                'J1 League': {'id': 196},
                'NSWL': {'id': 1690},
                'USL Championship': {'id': 13363},
                'La Liga 2': {'id': 54}
            },
            'Fotmob': {
                'Premier League': {'id': 47},
                'Bundesliga': {'id': 54},
                'La Liga': {'id': 87},
                'Serie A': {'id': 55},
                'Ligue 1': {'id': 53},
                'Argentina Copa de la Liga': {'id': 10007},
                'Argentina Primera Division': {'id': 112},
                'Primera Division Colombia': {'id': 274},
                'Primera Division Chile': {'id': 273},
                'Brasileirao': {'id': 268},
                'Primera Division Peru': {'id': 131},
                'Copa America': {'id': 44},
                'Euros': {'id': 50}
            }
        }
        
        # Get leagues for the specified page
        page_leagues = all_leagues.get(page, {})
        
        # If league exists, return all leagues for that page
        # If league doesn't exist, create a generic entry to prevent errors
        if league in page_leagues:
            return page_leagues
        else:
            # Create a fallback entry for unknown leagues
            logger.warning(f"League '{league}' not found in {page} fallback data. Using generic ID.")
            fallback_leagues = page_leagues.copy()
            fallback_leagues[league] = {'id': f'unknown_{hash(league) % 10000}', 'seasons': None}
            return fallback_leagues

    # Default headers configuration
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ar,en-US;q=0.9,en;q=0.8",
        "origin": "https://www.365scores.com",
        "referer": "https://www.365scores.com/",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36",
    }

class ThreeSixFiveScores:
    """
    Main class for interacting with 365Scores API
    Provides methods for fetching match data, statistics, and competition results
    """
    
    def __init__(self, timeout: int = 10, delay: float = 0.3):
        """
        Initialize the ThreeSixFiveScores client
        
        Args:
            timeout: Request timeout in seconds
            delay: Default delay between requests in seconds
        """
        self.timeout = timeout
        self.delay = delay
        self.session = self._setup_session()
        self.headers = self._setup_headers()

    def _setup_session(self) -> requests.Session:
        """Setup requests session with retry strategy"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        return session

    def _setup_headers(self) -> Dict[str, str]:
        """Setup request headers"""
        request_headers = headers.copy()
        request_headers.update({
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.365scores.com/',
            'Origin': 'https://www.365scores.com'
        })
        return request_headers

    ##############################
    # Utility/Private Methods
    ##############################

    def _fetch_match_data(self, game_id: Union[str, int], competition_id: Optional[Union[str, int]] = None, 
                      matchup_id: Optional[Union[str, int]] = None) -> Dict:
        """Fetch match data robustly from 365Scores API"""
        if not game_id:
            logger.warning("No game_id provided")
            return {}

        base_url = "https://webws.365scores.com/web/game/"
        params = {
            "appTypeId": 5,
            "langId": 1,
            "timezoneName": "Europe/London",
            "userCountryId": 21,
            "gameId": str(game_id),
            "topBookmaker": 14
        }
        if competition_id:
            params["competitions"] = str(competition_id)
        if matchup_id:
            params["matchupId"] = str(matchup_id)

        try:
            response = self.session.get(base_url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.delay)
            data = response.json()
            if not isinstance(data, dict):
                logger.warning(f"Unexpected JSON structure for game_id {game_id}")
                return {}
            return data
        except (requests.RequestException, json.JSONDecodeError) as e:
            logger.error(f"Failed to fetch match data for game_id {game_id}: {e}")
            return {}


    def _slugify_text(self, text: Optional[str]) -> str:
        """Convert text to URL-friendly slug"""
        if text is None:
            return ""
        text = str(text).lower()
        text = re.sub(r'\s+', '-', text)
        text = re.sub(r'&', 'and', text)
        text = re.sub(r'[^\w\u0600-\u06FF-]+', '', text, flags=re.UNICODE)
        text = re.sub(r'--+', '-', text)
        text = text.strip('-')
        return text

    def _extract_members(self, game_or_match_data: Dict) -> List[Dict]:
        """Extract members from game/match data"""
        members = []
        try:
            members.extend(game_or_match_data.get("homeCompetitor", {}).get("lineups", {}).get("members", []))
            members.extend(game_or_match_data.get("awayCompetitor", {}).get("lineups", {}).get("members", []))
        except Exception as e:
            logger.warning(f"Error extracting members: {e}")
        
        # Fallback to global 'members'
        if "members" in game_or_match_data and isinstance(game_or_match_data["members"], list):
            members.extend(game_or_match_data["members"])
        
        return members

    def _process_shotmap_dataframe(self, chart: Dict, game: Optional[Dict] = None) -> pd.DataFrame:
        """Process shotmap data into DataFrame"""
        events = chart.get('events', [])
        if not events:
            return pd.DataFrame()
            
        df = pd.DataFrame(events)
        
        # Map event types, statuses, and subtypes
        event_types = {e["value"]: e["name"] for e in chart.get("eventTypes", [])}
        statuses = {s["id"]: s["name"] for s in chart.get("statuses", [])}
        subtypes = {s["value"]: s["name"] for s in chart.get("eventSubTypes", [])}
        
        if "type" in df.columns:
            df["eventTypeName"] = df["type"].map(event_types)
        if "status" in df.columns:
            df["statusName"] = df["status"].map(statuses)
        if "subType" in df.columns:
            df["subTypeName"] = df["subType"].map(subtypes)
        
        # Process xgot column
        if 'xgot' in df.columns:
            df['xgot'] = df['xgot'].apply(lambda x: str(x).replace('-', '0') 
                                        if pd.notnull(x) and isinstance(x, str) else '0')
        else:
            df['xgot'] = '0'
        
        # Process xg column
        if 'xg' not in df.columns:
            df['xg'] = 0.0
        else:
            df['xg'] = pd.to_numeric(df['xg'], errors='coerce').fillna(0.0)
        
        df['xgot'] = pd.to_numeric(df['xgot'], errors='coerce').fillna(0.0)
        
        # Process outcome column
        if 'outcome' in df.columns:
            outcols = ['y', 'z', 'id', 'name', 'x']
            for col in outcols:
                df[f'outcome_{col}'] = df['outcome'].apply(
                    lambda o: o.get(col) if isinstance(o, dict) else None
                )
            df = df.rename(columns={'outcome_name': 'shot_outcome'})
            df = df.drop(columns=['outcome'])
        else:
            df['shot_outcome'] = None
        
        # Add player information if game data is available
        if game is not None:
            members = self._extract_members(game)
            player_id_to_name = {m["id"]: m.get("name") for m in members 
                               if "id" in m and "name" in m}
            player_id_to_jersey = {m["id"]: m.get("jerseyNumber") for m in members 
                                 if "id" in m and "jerseyNumber" in m}
            
            if "playerId" in df.columns:
                df["playerName"] = df["playerId"].map(player_id_to_name)
                df["jerseyNumber"] = df["playerId"].map(player_id_to_jersey)
        
        return df

    def _safe_int(self, value: Any) -> int:
        """Convert value to integer safely"""
        try:
            return int(value) if value not in [None, ''] else 0
        except (TypeError, ValueError):
            return 0

    def _process_game_records(self, games_data_from_api: List[Dict]) -> pd.DataFrame:
        """Process raw game data into standardized DataFrame"""
        if not games_data_from_api:
            return pd.DataFrame()

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

        # Process datetime
        if 'start_time_raw' in games_df.columns and not games_df.empty:
            games_df['datetime_obj'] = pd.to_datetime(games_df['start_time_raw'], errors='coerce')
            games_df['datetime_obj'] = pd.to_datetime(games_df['datetime_obj'], errors='coerce')  # تأكيد النوع

            # # ✅ أسطر الفحص
            # print("📌 قيم start_time_raw:")
            # print(games_df['start_time_raw'].head())

            # print("📌 بعد التحويل لـ datetime_obj:")
            # print(games_df['datetime_obj'].head())

            # print("📌 نوع العمود datetime_obj:")
            # print(games_df['datetime_obj'].dtype)

            # تحقق إن العمود فعلاً من نوع datetime
            if pd.api.types.is_datetime64_any_dtype(games_df['datetime_obj']):
                games_df['start_date'] = games_df['datetime_obj'].dt.strftime('%Y-%m-%d')
                games_df['start_time'] = games_df['datetime_obj'].dt.strftime('%H:%M')

                # ✅ إضافة الأعمدة الجديدة هنا
                games_df['weekday'] = games_df['datetime_obj'].dt.day_name()
                games_df['hour'] = games_df['datetime_obj'].dt.hour
            else:
                print("⚠️ التحويل لـ datetime فشل، تحقق من صيغة start_time_raw")
                games_df['start_date'] = None
                games_df['start_time'] = None
                games_df['weekday'] = None
                games_df['hour'] = None
        else:
            games_df['start_date'] = None
            games_df['start_time'] = None
            games_df['datetime_obj'] = pd.NaT
            games_df['weekday'] = None
            games_df['hour'] = None

        return games_df



    def _apply_status_filter(self, df: pd.DataFrame, status_filter: str) -> pd.DataFrame:
        """Apply status filter to DataFrame"""
        status_map = {
            'finished': ['FT', 'Ended', 'AET', 'Pen'],
            'upcoming': ['NS', 'Not Started', 'Postp', 'Scheduled'],
            'live': ['1H', '2H', 'HT', 'LIVE', 'ET']
        }
        valid_statuses = status_map.get(status_filter, [])
        if valid_statuses and 'status' in df.columns:
            return df[df['status'].isin(valid_statuses)]
        return df

    @staticmethod
    def _deduplicate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows from DataFrame"""
        unique_columns = ['id', 'team1Id', 'team2Id', 'game_id']
        columns_to_use = [col for col in unique_columns if col in df.columns]
        if columns_to_use:
            df.drop_duplicates(subset=columns_to_use, inplace=True)
        return df

    @staticmethod
    def _standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names in DataFrame"""
        column_mapping = {
            'team1ID': 'team1Id',
            'team_2_id': 'team2Id'
        }
        return df.rename(columns=column_mapping)

    def _365scores_request(self, path: str, params: Optional[Dict] = None) -> requests.Response:
        """Make request to 365Scores API"""
        base_url = f'https://webws.365scores.com/web/{path}'
        try:
            response = self.session.get(
                base_url,
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            time.sleep(self.delay)
            return response
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to 365Scores API: {e}")

    ##############################
    # Public Methods
    ##############################

    def get_ids(self, match_url: str) -> tuple:
        """Extract IDs from 365Scores match URL"""
        match_id1 = re.search(r'-(\d+-\d+-\d+)', match_url)
        id_1 = match_id1.group(1) if match_id1 else None
        
        match_id2 = re.search(r'[#/]id=(\d+)', match_url)
        if not match_id2:
            match_id2 = re.search(r'/(\d+)$', match_url.split('#')[0].split('?')[0])
        id_2 = match_id2.group(1) if match_id2 else None
        
        return id_1, id_2

    def get_match_data(self, match_url: str) -> Dict:
        """Get match data from URL"""
        matchup_id, game_id = self.get_ids(match_url)
        if not game_id:
            return {}
        data = self._fetch_match_data(game_id, matchup_id=matchup_id)
        return data.get('game', {}) if 'game' in data else {}

    def get_match_data_by_id(self, game_id: Union[str, int], 
                           competition_id: Optional[Union[str, int]] = None) -> Dict:
        """Get match data by game ID"""
        # 1. جلب القاموس الكامل من الـ API
        data = self._fetch_match_data(game_id, competition_id=competition_id)
        # 2. إرجاع محتوى مفتاح 'game' فقط (الإصلاح)
        return data.get('game', {})

    def get_requests_stats(self, match_url: str) -> Optional[requests.Response]:
        """Get stats request response for a match"""
        _, game_id = self.get_ids(match_url)
        if not game_id:
            return None
        
        try:
            url = (f'https://webws.365scores.com/web/game/stats/?appTypeId=5&langId=1'
                  f'&timezoneName=America/Buenos_Aires&userCountryId=382&games={game_id}')
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.delay)
            return response
        except requests.RequestException as e:
            logger.error(f"Failed to get stats for match: {e}")
            return None

    def get_match_general_stats(self, match_url: str) -> pd.DataFrame:
        """Get general match statistics"""
        response_obj = self.get_requests_stats(match_url)
        if response_obj is None:
            return pd.DataFrame()
        
        try:
            response_data = response_obj.json()
        except json.JSONDecodeError:
            return pd.DataFrame()
        
        # Validate response structure
        required_keys = ['statistics', 'competitors']
        if not all(key in response_data for key in required_keys):
            return pd.DataFrame()
        
        if (not isinstance(response_data['statistics'], list) or
            not isinstance(response_data['competitors'], list) or
            len(response_data['competitors']) < 2):
            return pd.DataFrame()
        
        match_stats_df = pd.DataFrame(response_data['statistics'])
        if match_stats_df.empty or 'competitorId' not in match_stats_df.columns:
            return match_stats_df
        
        # Map team names
        competitors = response_data['competitors']
        team_mapping = {
            comp.get('id'): comp.get('name', f'Team {i+1}') 
            for i, comp in enumerate(competitors[:2])
        }
        
        match_stats_df['team_name'] = match_stats_df['competitorId'].map(team_mapping).fillna('Unknown')
        return match_stats_df


    def get_match_time_stats_by_id(self, match_id: int) -> dict:
        """Fetch match time stats using match ID (safe version with clear output)"""
        try:
            # 1️⃣ جلب بيانات المباراة الأساسية
            match_data = self.get_match_data_by_id(match_id)
            if not match_data:
                return {"error": f"No match data found for match ID {match_id}"}

            competition_id = match_data.get('competitionId')
            home = match_data.get('homeCompetitor', {})
            away = match_data.get('awayCompetitor', {})

            home_id = home.get('id')
            away_id = away.get('id')
            home_name = home.get('name', 'Home')
            away_name = away.get('name', 'Away')

            if not competition_id or not home_id or not away_id:
                return {"error": f"Missing IDs to construct match URL for match ID {match_id}"}

            # 2️⃣ توليد رابط صالح
            match_url = f"https://www.365scores.com/football/match/{competition_id}/{home_id}-{away_id}-{match_id}#id={match_id}"

            # 3️⃣ استدعاء الدالة الأصلية
            stats = self.get_match_time_stats(match_url)

            if not stats:
                return {"error": "No actualGameStatistics found for this match."}

            # 4️⃣ تنظيم البيانات بشكل أوضح
            output = {
                "home_team": home_name,
                "away_team": away_name,
                "actual_play_time": stats.get("actualPlayTime", {}),
                "added_time": stats.get("addedTime", {}),
                "wasted_time": stats.get("wastedTime", {}),
                "general": stats.get("general", [])
            }

            return output

        except Exception as e:
            return {"error": str(e)}


    def get_match_time_stats(self, match_url: str) -> Dict:
        """Get match time statistics"""
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

    def get_match_shotmap(self, match_url: str) -> pd.DataFrame:
        """Get match shotmap data"""
        match_data = self.get_match_data(match_url)
        if (not match_data or 'chartEvents' not in match_data or 
            'events' not in match_data.get('chartEvents', {})):
            raise MatchDoesntHaveInfo(f"Shotmap data not found: {match_url}")
        
        # Check for valid match scores
        home_score = match_data.get("homeCompetitor", {}).get("score", 0)
        away_score = match_data.get("awayCompetitor", {}).get("score", 0)
        
        if not (isinstance(home_score, (int, float)) and isinstance(away_score, (int, float))):
            return pd.DataFrame()
        
        if home_score <= 0 and away_score <= 0:
            return pd.DataFrame()
        
        chart = match_data['chartEvents']
        return self._process_shotmap_dataframe(chart, game=match_data)

    def get_players_info(self, match_url: str) -> pd.DataFrame:
        """Get players information for a match"""
        match_data = self.get_match_data(match_url)
        if (not match_data or 'members' not in match_data or 
            not isinstance(match_data['members'], list)):
            return pd.DataFrame()
        
        teams_json = match_data['members']
        return pd.DataFrame(teams_json) if teams_json else pd.DataFrame()

    def get_team_data(self, match_url: str) -> tuple:
        """Get team data for a match"""
        match_data = self.get_match_data(match_url)
        default_home = {'name': 'Unknown Home', 'id': None, 'color': None}
        default_away = {'name': 'Unknown Away', 'id': None, 'color': None}
        
        if not match_data:
            return default_home, default_away
        
        team_details = []
        for side in ['home', 'away']:
            competitor_key = f'{side}Competitor'
            if competitor_key in match_data and isinstance(match_data[competitor_key], dict):
                competitor = match_data[competitor_key]
                team_details.append({
                    'name': competitor.get('name', f'Unknown {side.capitalize()}'),
                    'id': competitor.get('id'),
                    'color': competitor.get('color')
                })
            else:
                team_details.append({
                    'name': f'Unknown {side.capitalize()}', 
                    'id': None, 
                    'color': None
                })
        
        home = team_details[0] if len(team_details) > 0 else default_home
        away = team_details[1] if len(team_details) > 1 else default_away
        
        return home, away
    
    def get_league_top_players_stats_by_id(self, league_id, season: Optional[str] = None) -> pd.DataFrame:
        if isinstance(league_id, str) and league_id.isdigit():
            league_id = int(league_id)

        print(f"Fetching stats for league_id={league_id}, season={season}")
        try:
            url = (f'https://webws.365scores.com/web/stats/?appTypeId=5&langId=1'
                f'&timezoneName=America/Buenos_Aires&userCountryId=382&competitions={league_id}')
            if season:
                url += f'&seasonId={season}'

            print(f"Requesting URL: {url}")
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.delay)
            stats_data = response.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Request or JSON error: {e}")
            return pd.DataFrame()

        if 'stats' not in stats_data:
            print("No 'stats' key in response")
            return pd.DataFrame()

        # التأكد من وجود athletesStats
        if 'athletesStats' not in stats_data['stats']:
            print("'athletesStats' key not found in stats")
            # اطبع الـ keys المتاحة للمراجعة
            print("Available stats keys:", stats_data['stats'])
            return pd.DataFrame()

        athletes_stats = stats_data['stats']['athletesStats']
        if not athletes_stats:
            print("'athletesStats' is empty")
            return pd.DataFrame()

        total_df = pd.DataFrame()
        for i, stat_group in enumerate(athletes_stats):
            stats_df = self.parse_dataframe(stat_group)
            if not stats_df.empty:
                total_df = pd.concat([total_df, stats_df], ignore_index=True)

        if total_df.empty:
            print("Final DataFrame is empty after parsing athletesStats")
        else:
            print(f"Successfully fetched stats: {total_df.shape[0]} rows")

        return total_df


    def get_league_top_players_stats(self, league_name: str, season: Optional[str] = None) -> pd.DataFrame:
        """Fetch top players stats by league name, using league_id internally"""
        print(f"Fetching league stats for league_name='{league_name}', season={season}")

        # جلب league_id من القائمة أو fallback
        league_info = get_possible_leagues_for_page(league_name, season, '365Scores')
        if league_name not in league_info or 'id' not in league_info[league_name]:
            print(f"League '{league_name}' not found or has no id")
            return pd.DataFrame()

        league_id = league_info[league_name]['id']
        print(f"Using league_id={league_id}")

        # استخدام الدالة by_id لتفادي تكرار الكود
        return self.get_league_top_players_stats_by_id(league_id, season)

    def parse_dataframe(self, objeto: Dict) -> pd.DataFrame:
        """Parse dataframe from stats object"""
        if not (isinstance(objeto, dict) and 'rows' in objeto and 'name' in objeto):
            return pd.DataFrame()
        
        stat_category_name = objeto['name']
        df = pd.DataFrame(objeto['rows'])
        df['stat_category'] = stat_category_name
        return df

    def get_competition_results(
        self,
        competition_id: int,
        after_game: Optional[int] = None,
        direction: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None
    ) -> Dict:
        """Get competition results with pagination support"""
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
        
        try:
            response = self._365scores_request('games/results/', params=params)
            data = response.json()
            games_data_from_api = data.get('games', [])
            
            games_df = self._process_game_records(games_data_from_api)
            
            paging_data = data.get('paging', {})
            
            # Extract pagination tokens
            next_token = None
            prev_token = None
            
            next_page_url = paging_data.get('nextPage')
            if next_page_url:
                next_match = re.search(r'aftergame=(\d+)', next_page_url)
                if next_match:
                    next_token = int(next_match.group(1))
            
            prev_page_url = paging_data.get('prevPage')
            if prev_page_url:
                prev_match = re.search(r'aftergame=(\d+)', prev_page_url)
                if prev_match:
                    prev_token = int(prev_match.group(1))
            
        except (ConnectionError, json.JSONDecodeError, requests.exceptions.RequestException) as e:
            logger.error(f"Error fetching competition results: {e}")
            return {
                'games': pd.DataFrame(),
                'paging': {
                    'next_token': None,
                    'prev_token': None,
                    'total_games': 0
                }
            }
        
        if status_filter:
            games_df = self._apply_status_filter(games_df, status_filter)
        
        return {
            'games': games_df,
            'paging': {
                'next_token': next_token,
                'prev_token': prev_token,
                'total_games': paging_data.get('totalGames', len(games_data_from_api))
            }
        }

    def get_full_competition_results(
        self,
        competition_id: Optional[int] = None,
        initial_url: Optional[str] = None,
        page_size: int = 50,
        max_pages: int = 1000,
        max_games: Optional[int] = None
    ) -> pd.DataFrame:
        """Get full competition results with all pages"""
        if not initial_url and not competition_id:
            raise ValueError("Either 'competition_id' or 'initial_url' must be provided.")
        
        if initial_url:
            current_full_url = initial_url
        else:
            if not isinstance(competition_id, int):
                raise ValueError("competition_id must be an integer if initial_url is not provided.")
            current_full_url = (
                f"https://webws.365scores.com/web/games/results/?"
                f"appTypeId=5&langId=1&timezoneName=Asia/Hebron&userCountryId=115"
                f"&competitions={competition_id}&showOdds=true&includeTopBettingOpportunity=1"
            )
        
        all_games_dfs = []
        processed_game_ids = set()
        seen_full_urls = set()
        page_count = 0
        
        while current_full_url and page_count < max_pages:
            if current_full_url in seen_full_urls:
                logger.warning("Duplicate URL detected, stopping to prevent infinite loop")
                break
                
            seen_full_urls.add(current_full_url)
            page_count += 1
            
            try:
                parsed_url = urlparse(current_full_url)
                path_segments = parsed_url.path.strip('/').split('/')
                
                if len(path_segments) >= 2 and path_segments[0] == 'web':
                    api_path = '/'.join(path_segments[1:]) + '/'
                else:
                    api_path = '/'.join(path_segments) + '/'
                
                params = parse_qs(parsed_url.query)
                single_value_params = {k: v[0] for k, v in params.items()}
                single_value_params['games'] = str(page_size)
                
                response = self._365scores_request(api_path, params=single_value_params)
                data = response.json()
                
            except (ConnectionError, json.JSONDecodeError, requests.exceptions.RequestException) as e:
                logger.error(f"Error fetching page {page_count}: {e}")
                break
            
            if 'games' not in data or not data['games']:
                break
            
            df_page = self._process_game_records(data['games'])
            new_games = df_page[~df_page['game_id'].isin(processed_game_ids)]
            
            if not new_games.empty:
                all_games_dfs.append(new_games)
                processed_game_ids.update(new_games['game_id'])
            
            if max_games and len(processed_game_ids) >= max_games:
                break
            
            # Get next page URL
            next_page_relative_path = data.get('paging', {}).get('nextPage')
            current_full_url = f"https://webws.365scores.com{next_page_relative_path}" if next_page_relative_path else None
        
        if not all_games_dfs:
            return pd.DataFrame()
        
        final_df = pd.concat(all_games_dfs, ignore_index=True)
        final_df.drop_duplicates(subset=['game_id'], keep='first', inplace=True)
        
        # Sort by datetime if available
        if 'datetime_obj' in final_df.columns and not final_df['datetime_obj'].isnull().all():
            final_df = final_df.sort_values('datetime_obj', ascending=True)
        elif 'game_id' in final_df.columns:
            final_df = final_df.sort_values('game_id', ascending=True)
        
        final_df = final_df.reset_index(drop=True)
        logger.info(f"Successfully fetched {len(final_df)} unique matches")
        
        return final_df

    def get_player_heatmap_by_id(self, player_name: str, match_id: int) -> dict:
        """
        Fetch player heatmap image using player name and match ID.
        Returns a dict with either 'image' key (PIL Image) or 'error' key.
        Displays the image directly in Jupyter Notebook if available.
        """
        try:
            # 1️⃣ جلب بيانات المباراة باستخدام ID
            match_data = self.get_match_data_by_id(match_id)
            if not match_data:
                return {"error": f"No match data found for match ID {match_id}"}

            all_members = match_data.get('members', [])
            if not isinstance(all_members, list) or not all_members:
                return {"error": f"No 'members' data available for match ID {match_id}"}

            df_all = pd.DataFrame(all_members)
            if df_all.empty or 'name' not in df_all.columns:
                return {"error": f"'members' missing 'name' column for match ID {match_id}"}

            # 2️⃣ البحث عن اللاعب
            player_rows = df_all[df_all['name'] == player_name]
            if player_rows.empty:
                return {"error": f"Player '{player_name}' not found in match members for match ID {match_id}"}

            player_info = player_rows.iloc[0]
            heatmap_url = player_info.get('heatMap')

            # 3️⃣ محاولة البحث في مواقع بديلة إذا لم يكن موجود
            if not heatmap_url:
                for key in ('homeCompetitor', 'awayCompetitor'):
                    comp = match_data.get(key, {})
                    members = comp.get('lineups', {}).get('members', []) if isinstance(comp.get('lineups'), dict) else []
                    for m in members:
                        if m.get('id') == player_info.get('id') and m.get('heatMap'):
                            heatmap_url = m['heatMap']
                            break
                    if heatmap_url:
                        break

            if not heatmap_url:
                return {"error": f"No heatmap URL available for player '{player_name}' in match ID {match_id}"}

            # 4️⃣ تحميل الصورة
            resp = self.session.get(heatmap_url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            time.sleep(self.delay)
            img = Image.open(BytesIO(resp.content))

            # 5️⃣ عرض الصورة مباشرة في Jupyter Notebook
            try:
                display(img)
            except Exception:
                pass  # لو مش في Notebook، يتم تجاهل العرض

            return {"image": img}

        except Exception as e:
            return {"error": str(e)}



    def get_player_heatmap_match(self, player_name: str, match_url: str) -> Image.Image:
        """Get player heatmap for a match"""
        match_data = self.get_match_data(match_url)
        all_members = match_data.get('members', [])
        
        if not isinstance(all_members, list):
            raise MatchDoesntHaveInfo(f"No 'members' list in match_data for {match_url}")
        
        df_all = pd.DataFrame(all_members)
        if df_all.empty or 'name' not in df_all.columns:
            raise MatchDoesntHaveInfo(f"Members info missing 'name' for {match_url}")
        
        player_rows = df_all[df_all['name'] == player_name]
        if player_rows.empty:
            raise MatchDoesntHaveInfo(f"Player '{player_name}' not found in match members for {match_url}")
        
        player_info = player_rows.iloc[0]
        heatmap_url = player_info.get('heatMap')
        
        # Try alternative locations for heatmap URL
        if not heatmap_url:
            for key in ('homeCompetitor', 'awayCompetitor'):
                comp = match_data.get(key, {})
                members = comp.get('lineups', {}).get('members', []) if isinstance(comp.get('lineups'), dict) else []
                for m in members:
                    if m.get('id') == player_info.get('id') and m.get('heatMap'):
                        heatmap_url = m['heatMap']
                        break
                if heatmap_url:
                    break
        
        if not heatmap_url:
            raise MatchDoesntHaveInfo(f"No heatmap URL available for player '{player_name}' in match {match_url}")
        
        try:
            resp = self.session.get(heatmap_url, headers=self.headers, timeout=self.timeout)
            resp.raise_for_status()
            time.sleep(self.delay)
            return Image.open(BytesIO(resp.content))
        except Exception as e:
            raise MatchDoesntHaveInfo(f"Failed to fetch/open heatmap for '{player_name}': {e}")

    # Additional utility methods for backwards compatibility
    def get_general_match_stats(self, match_url: str) -> pd.DataFrame:
        """
        Get general match statistics (fallback method for compatibility)
        This method tries to extract stats from match data first, then falls back to detailed stats
        """
        match_data = self.get_match_data(match_url)
        sides = ['home', 'away']
        all_stats_records = []
        
        if not match_data:
            logger.warning(f"No match data retrieved for URL: {match_url}. Falling back to detailed stats endpoint.")
            return self._use_detailed_stats(match_url)
        
        for side in sides:
            competitor = match_data.get(side) or match_data.get(f"{side}Competitor")
            if not isinstance(competitor, dict):
                continue
                
            team_name = competitor.get('name', f"Unknown {side.capitalize()}")
            stats = None
            
            # Try different locations for stats
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
            logger.warning(f"No stats from game endpoint. Falling back to detailed stats endpoint.")
            return self._use_detailed_stats(match_url)
        
        return pd.DataFrame(all_stats_records)

    def _use_detailed_stats(self, match_url: str) -> pd.DataFrame:
        """Use detailed stats endpoint as fallback"""
        df = self.get_match_general_stats(match_url)
        if df.empty:
            return df
        
        df = df.rename(columns={'team_name': 'team'})
        cols = ['name', 'categoryName', 'value', 'team']
        return df[[c for c in cols if c in df.columns]]

    def get_match_general_stats_by_id(self, game_id: Union[str, int], 
                                    competition_id: Optional[Union[str, int]] = None) -> pd.DataFrame:
        """Fetch general match statistics using game_id"""
        url = (f"https://webws.365scores.com/web/game/stats/?"
              f"appTypeId=5&langId=1&timezoneName=America/Buenos_Aires&userCountryId=382&games={game_id}")
        
        if competition_id:
            url += f"&competitions={competition_id}"
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.delay)
            response_data = response.json()
        except (requests.RequestException, json.JSONDecodeError):
            return pd.DataFrame()
        
        # Validate response structure
        required_keys = ['statistics', 'competitors']
        if not all(key in response_data for key in required_keys):
            return pd.DataFrame()
        
        if (not isinstance(response_data['statistics'], list) or
            not isinstance(response_data['competitors'], list) or
            len(response_data['competitors']) < 2):
            return pd.DataFrame()
        
        match_stats_df = pd.DataFrame(response_data['statistics'])
        if match_stats_df.empty or 'competitorId' not in match_stats_df.columns:
            return match_stats_df
        
        # Map team names
        competitors = response_data['competitors']
        team_mapping = {
            comp.get('id'): comp.get('name', f'Team {i+1}') 
            for i, comp in enumerate(competitors[:2])
        }
        
        match_stats_df['team_name'] = match_stats_df['competitorId'].map(team_mapping).fillna('Unknown')
        return match_stats_df

    def get_shotmap_enriched(self, game_id: Union[str, int], 
                           competition_id: Union[str, int] = "552") -> pd.DataFrame:
        """Get enriched shotmap data by game ID"""
        match_data = self.get_match_data_by_id(game_id, competition_id)
        
        # تم تعديل الشرط: match_data الآن هو قاموس المباراة مباشرة
        if not (isinstance(match_data, dict) and 'chartEvents' in match_data and 
                'events' in match_data['chartEvents']):
            return pd.DataFrame()
        
        # تم تعديل التعيين: game هو نفسه match_data
        game = match_data 
        home_score = game.get('homeCompetitor', {}).get('score', 0)
        away_score = game.get('awayCompetitor', {}).get('score', 0)
        
        if not (isinstance(home_score, (int, float)) and isinstance(away_score, (int, float))):
            return pd.DataFrame()
        
        if home_score <= 0 and away_score <= 0:
            return pd.DataFrame()
        
        chart = game['chartEvents']
        return self._process_shotmap_dataframe(chart, game=game)
    
    def get_match_shotmap_by_game_id(self, game_id: Union[str, int], competition_id: Optional[Union[str, int]] = None) -> pd.DataFrame:
        """Get shotmap by game ID"""
        match_data = self.get_match_data_by_id(game_id, competition_id=competition_id)
        if (not match_data or 'chartEvents' not in match_data or 
            'events' not in match_data.get('chartEvents', {})):
            raise MatchDoesntHaveInfo(f"Shotmap data not found for game ID {game_id}")
        
        home_score = match_data.get("homeCompetitor", {}).get("score", 0)
        away_score = match_data.get("awayCompetitor", {}).get("score", 0)
        if home_score <= 0 and away_score <= 0:
            return pd.DataFrame()
        
        chart = match_data['chartEvents']
        return self._process_shotmap_dataframe(chart, game=match_data)

    def get_players_info_by_game_id(self, game_id: Union[str, int], competition_id: Optional[Union[str, int]] = None) -> pd.DataFrame:
        """Get players info by game ID"""
        match_data = self.get_match_data_by_id(game_id, competition_id=competition_id)
        if (not match_data or 'members' not in match_data or 
            not isinstance(match_data['members'], list)):
            return pd.DataFrame()
        
        teams_json = match_data['members']
        return pd.DataFrame(teams_json) if teams_json else pd.DataFrame()

    def get_team_data_by_game_id(self, game_id: Union[str, int], competition_id: Optional[Union[str, int]] = None) -> tuple:
        """Get home and away team data by game ID"""
        match_data = self.get_match_data_by_id(game_id, competition_id=competition_id)
        default_home = {'name': 'Unknown Home', 'id': None, 'color': None}
        default_away = {'name': 'Unknown Away', 'id': None, 'color': None}
        
        if not match_data:
            return default_home, default_away
        
        team_details = []
        for side in ['home', 'away']:
            competitor_key = f'{side}Competitor'
            if competitor_key in match_data and isinstance(match_data[competitor_key], dict):
                competitor = match_data[competitor_key]
                team_details.append({
                    'name': competitor.get('name', f'Unknown {side.capitalize()}'),
                    'id': competitor.get('id'),
                    'color': competitor.get('color')
                })
            else:
                team_details.append({
                    'name': f'Unknown {side.capitalize()}', 
                    'id': None, 
                    'color': None
                })
        
        home = team_details[0] if len(team_details) > 0 else default_home
        away = team_details[1] if len(team_details) > 1 else default_away
        
        return home, away

    
