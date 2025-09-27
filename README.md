# fix_some
fix some file in LanusStats 
Add get_match_data_by_id to fetch match data by game ID.

Add get_match_general_stats_by_id to get general match stats by ID.

Add get_match_shotmap_by_game_id to fetch shotmap by match ID.

Add get_players_info_by_game_id to fetch player info by match ID.

Add get_team_data_by_game_id to fetch team info by match ID.

Add get_match_time_stats_by_id to fetch time stats by match ID (smart URL generation).

Add get_player_heatmap_by_id to fetch player heatmap by player name and match ID.

Improve exception handling in all _by_id methods; return clear error messages.

Convert members list to DataFrame for safer filtering in heatmap and players info.

Ensure all _by_id methods return consistent structured output (dict, tuple, DataFrame).

Add alternative lookup for missing heatmap URLs in player heatmap method.

Add time.sleep(self.delay) after HTTP requests to avoid rapid API calls.

Standardize _by_id methods to fetch → validate → return pattern.
