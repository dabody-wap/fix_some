import pandas as pd
import json
import os
import dataclasses
from typing import List, Dict, Any, Optional

# ======== تعريف هياكل البيانات (Data Classes) ========
@dataclasses.dataclass
class Position:
    id: Optional[int] = None
    name: Optional[str] = None

@dataclasses.dataclass
class FormationDetail:
    id: Optional[int] = None
    name: Optional[str] = None
    shortName: Optional[str] = None

@dataclasses.dataclass
class YardFormation:
    line: Optional[int] = None
    fieldPosition: Optional[int] = None
    fieldLine: Optional[int] = None
    fieldSide: Optional[int] = None

@dataclasses.dataclass
class PlayerStat:
    type: Optional[int] = None
    value: Optional[Any] = None
    isTop: Optional[bool] = None
    categoryId: Optional[int] = None
    name: Optional[str] = None
    shortName: Optional[str] = None
    order: Optional[int] = None
    imageId: Optional[int] = None

@dataclasses.dataclass
class LineupMember:
    id: Optional[int] = None
    status: Optional[int] = None
    statusText: Optional[str] = None
    position: Optional[Position] = None
    formation: Optional[FormationDetail] = None
    yardFormation: Optional[YardFormation] = None
    hasStats: Optional[bool] = None
    ranking: Optional[int] = None
    heatMap: Optional[str] = None
    popularityRank: Optional[int] = None
    competitorId: Optional[int] = None
    nationalId: Optional[int] = None
    stats: Optional[List[PlayerStat]] = dataclasses.field(default_factory=list)
    name: Optional[str] = None
    shortName: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LineupMember":
        position_data = data.get('position')
        formation_data = data.get('formation')
        yard_formation_data = data.get('yardFormation')
        stats_data = data.get('stats', [])

        return cls(
            id=data.get('id'),
            status=data.get('status'),
            statusText=data.get('statusText'),
            position=Position(**position_data) if position_data and isinstance(position_data, dict) else None,
            formation=FormationDetail(**formation_data) if formation_data and isinstance(formation_data, dict) else None,
            yardFormation=YardFormation(**yard_formation_data) if yard_formation_data and isinstance(yard_formation_data, dict) else None,
            hasStats=data.get('hasStats'),
            ranking=data.get('ranking'),
            heatMap=data.get('heatMap'),
            popularityRank=data.get('popularityRank'),
            competitorId=data.get('competitorId'),
            nationalId=data.get('nationalId'),
            stats=[PlayerStat(**s) for s in stats_data if isinstance(s, dict)] if stats_data else [],
            name=data.get('name'),
            shortName=data.get('shortName')
        )

@dataclasses.dataclass
class Lineup:
    status: Optional[int] = None
    formation: Optional[str] = None
    hasFieldPositions: Optional[bool] = None
    members: Optional[List[LineupMember]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Lineup":
        members_data = data.get('members', [])
        return cls(
            status=data.get('status'),
            formation=data.get('formation'),
            hasFieldPositions=data.get('hasFieldPositions'),
            members=[LineupMember.from_dict(m) for m in members_data if isinstance(m, dict)]
        )

@dataclasses.dataclass
class RecentMatch:
    id: Optional[int] = None
    date: Optional[str] = None
    homeTeamName: Optional[str] = None
    homeTeamScore: Optional[int] = None
    awayTeamName: Optional[str] = None
    awayTeamScore: Optional[int] = None
    competitionName: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RecentMatch":
        return cls(
            id=data.get('id'),
            date=data.get('date'),
            homeTeamName=data.get('homeTeamName'),
            homeTeamScore=data.get('homeTeamScore'),
            awayTeamName=data.get('awayTeamName'),
            awayTeamScore=data.get('awayTeamScore'),
            competitionName=data.get('competitionName')
        )

@dataclasses.dataclass
class StatCategory:
    id: Optional[int] = None
    name: Optional[str] = None
    orderLevel: Optional[int] = None
    orderByPosition: Optional[List[Dict[str, Any]]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatCategory":
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            orderLevel=data.get('orderLevel'),
            orderByPosition=data.get('orderByPosition', [])
        )

@dataclasses.dataclass
class Competitor:
    id: Optional[int] = None
    countryId: Optional[int] = None
    sportId: Optional[int] = None
    name: Optional[str] = None
    score: Optional[int] = None
    isQualified: Optional[bool] = None
    toQualify: Optional[bool] = None
    isWinner: Optional[bool] = None
    type: Optional[int] = None
    nameForURL: Optional[str] = None
    imageVersion: Optional[int] = None
    color: Optional[str] = None
    awayColor: Optional[str] = None
    mainCompetitionId: Optional[int] = None
    recentMatches: Optional[List[RecentMatch]] = dataclasses.field(default_factory=list)
    lineups: Optional[Lineup] = None
    statsCategory: Optional[List[StatCategory]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Competitor":
        recent_matches_data = data.get('recentMatches', [])
        lineups_data = data.get('lineups')
        stats_category_data = data.get('statsCategory', [])
        
        return cls(
            id=data.get('id'),
            countryId=data.get('countryId'),
            sportId=data.get('sportId'),
            name=data.get('name'),
            score=data.get('score'),
            isQualified=data.get('isQualified'),
            toQualify=data.get('toQualify'),
            isWinner=data.get('isWinner'),
            type=data.get('type'),
            nameForURL=data.get('nameForURL'),
            imageVersion=data.get('imageVersion'),
            color=data.get('color'),
            awayColor=data.get('awayColor'),
            mainCompetitionId=data.get('mainCompetitionId'),
            recentMatches=[RecentMatch.from_dict(m) for m in recent_matches_data if isinstance(m, dict)],
            lineups=Lineup.from_dict(lineups_data) if lineups_data and isinstance(lineups_data, dict) else None,
            statsCategory=[StatCategory.from_dict(s) for s in stats_category_data if isinstance(s, dict)]
        )

@dataclasses.dataclass
class EventType:
    id: Optional[int] = None
    name: Optional[str] = None
    subTypeId: Optional[int] = None
    subTypeName: Optional[str] = None

@dataclasses.dataclass
class GameEvent:
    order: Optional[int] = None
    gameTimeDisplay: Optional[str] = None
    gameTime: Optional[float] = None
    addedTime: Optional[int] = None
    isMajor: Optional[bool] = None
    eventType: Optional[EventType] = None
    playerId: Optional[int] = None
    competitorId: Optional[int] = None
    statusId: Optional[int] = None
    stageId: Optional[int] = None
    num: Optional[int] = None
    gameTimeAndStatusDisplayType: Optional[int] = None
    extraPlayers: Optional[List[int]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameEvent":
        event_type_data = data.get('eventType')
        return cls(
            order=data.get('order'),
            gameTimeDisplay=data.get('gameTimeDisplay'),
            gameTime=data.get('gameTime'),
            addedTime=data.get('addedTime'),
            isMajor=data.get('isMajor'),
            eventType=EventType(**event_type_data) if event_type_data and isinstance(event_type_data, dict) else None,
            playerId=data.get('playerId'),
            competitorId=data.get('competitorId'),
            statusId=data.get('statusId'),
            stageId=data.get('stageId'),
            num=data.get('num'),
            gameTimeAndStatusDisplayType=data.get('gameTimeAndStatusDisplayType'),
            extraPlayers=data.get('extraPlayers', [])
        )

@dataclasses.dataclass
class ChartEventOutcome:
    id: Optional[int] = None
    name: Optional[str] = None

@dataclasses.dataclass
class ChartEvent:
    key: Optional[int] = None
    time: Optional[int] = None
    minute: Optional[int] = None
    type: Optional[int] = None
    subType: Optional[int] = None
    playerId: Optional[int] = None
    xg: Optional[float] = None
    xgot: Optional[float] = None
    bodyPart: Optional[int] = None
    goalDescription: Optional[str] = None
    outcome: Optional[ChartEventOutcome] = None
    competitorNum: Optional[int] = None
    x: Optional[float] = None
    y: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChartEvent":
        outcome_data = data.get('outcome')
        outcome_for_dataclass = None
        if outcome_data and isinstance(outcome_data, dict):
            outcome_for_dataclass = {
                'id': outcome_data.get('id'),
                'name': outcome_data.get('name')
            }

        return cls(
            key=data.get('key'),
            time=data.get('time'),
            minute=data.get('minute'),
            type=data.get('type'),
            subType=data.get('subType'),
            playerId=data.get('playerId'),
            xg=data.get('xg'),
            xgot=data.get('xgot'),
            bodyPart=data.get('bodyPart'),
            goalDescription=data.get('goalDescription'),
            outcome=ChartEventOutcome(**outcome_for_dataclass) if outcome_for_dataclass else None,
            competitorNum=data.get('competitorNum'),
            x=data.get('x'),
            y=data.get('y')
        )

@dataclasses.dataclass
class GameMembers:
    homeTeamMembers: Optional[List[Dict[str, Any]]] = dataclasses.field(default_factory=list)
    awayTeamMembers: Optional[List[Dict[str, Any]]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameMembers":
        return cls(
            homeTeamMembers=data.get('homeTeamMembers', []),
            awayTeamMembers=data.get('awayTeamMembers', [])
        )

@dataclasses.dataclass
class TopPerformerPlayer:
    id: Optional[int] = None
    athleteId: Optional[int] = None
    name: Optional[str] = None
    shortName: Optional[str] = None
    positionName: Optional[str] = None
    positionShortName: Optional[str] = None
    imageVersion: Optional[int] = None
    nameForURL: Optional[str] = None
    stats: Optional[List[PlayerStat]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopPerformerPlayer":
        stats_data = data.get('stats', [])
        return cls(
            id=data.get('id'),
            athleteId=data.get('athleteId'),
            name=data.get('name'),
            shortName=data.get('shortName'),
            positionName=data.get('positionName'),
            positionShortName=data.get('positionShortName'),
            imageVersion=data.get('imageVersion'),
            nameForURL=data.get('nameForURL'),
            stats=[PlayerStat(**s) for s in stats_data if isinstance(s, dict)]
        )

@dataclasses.dataclass
class TopPerformerCategory:
    name: Optional[str] = None
    homePlayer: Optional[TopPerformerPlayer] = None
    awayPlayer: Optional[TopPerformerPlayer] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopPerformerCategory":
        home_player_data = data.get('homePlayer')
        away_player_data = data.get('awayPlayer')
        return cls(
            name=data.get('name'),
            homePlayer=TopPerformerPlayer.from_dict(home_player_data) if home_player_data and isinstance(home_player_data, dict) else None,
            awayPlayer=TopPerformerPlayer.from_dict(away_player_data) if away_player_data and isinstance(away_player_data, dict) else None
        )

@dataclasses.dataclass
class TopPerformers:
    categories: Optional[List[TopPerformerCategory]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TopPerformers":
        categories_data = data.get('categories', [])
        return cls(
            categories=[TopPerformerCategory.from_dict(c) for c in categories_data if isinstance(c, dict)]
        )

@dataclasses.dataclass
class Widget:
    provider: Optional[str] = None
    partnerId: Optional[int] = None
    widgetUrl: Optional[str] = None
    widgetRatio: Optional[float] = None
    widgetType: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Widget":
        return cls(
            provider=data.get('provider'),
            partnerId=data.get('partnerId'),
            widgetUrl=data.get('widgetUrl'),
            widgetRatio=data.get('widgetRatio'),
            widgetType=data.get('widgetType')
        )

@dataclasses.dataclass
class GameStatistics:
    corners: Optional[Dict[str, int]] = dataclasses.field(default_factory=dict)
    shotsOnTarget: Optional[Dict[str, int]] = dataclasses.field(default_factory=dict)
    possession: Optional[Dict[str, int]] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameStatistics":
        return cls(
            corners=data.get('corners', {}),
            shotsOnTarget=data.get('shotsOnTarget', {}),
            possession=data.get('possession', {}),
        )

@dataclasses.dataclass
class Official:
    id: Optional[int] = None
    role: Optional[str] = None
    countryId: Optional[int] = None
    name: Optional[str] = None
    nameForURL: Optional[str] = None
    imageVersion: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Official":
        return cls(
            id=data.get('id'),
            role=data.get('role'),
            countryId=data.get('countryId'),
            name=data.get('name'),
            nameForURL=data.get('nameForURL'),
            imageVersion=data.get('imageVersion')
        )

@dataclasses.dataclass
class GameStage:
    id: Optional[int] = None
    name: Optional[str] = None
    shortName: Optional[str] = None
    homeCompetitorScore: Optional[int] = None
    awayCompetitorScore: Optional[int] = None
    isEnded: Optional[bool] = None
    isCurrent: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameStage":
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            shortName=data.get('shortName'),
            homeCompetitorScore=data.get('homeCompetitorScore'),
            awayCompetitorScore=data.get('awayCompetitorScore'),
            isEnded=data.get('isEnded'),
            isCurrent=data.get('isCurrent')
        )

@dataclasses.dataclass
class GameData:
    lineTypesIds: Optional[List[int]] = dataclasses.field(default_factory=list)
    id: Optional[int] = None
    sportId: Optional[int] = None
    competitionId: Optional[int] = None
    statusId: Optional[int] = None
    seasonNum: Optional[int] = None
    stageNum: Optional[int] = None
    groupNum: Optional[int] = None
    roundNum: Optional[int] = None
    roundName: Optional[str] = None
    stageName: Optional[str] = None
    groupName: Optional[str] = None
    competitionDisplayName: Optional[str] = None
    startTime: Optional[str] = None
    statusGroup: Optional[int] = None
    statusText: Optional[str] = None
    shortStatusText: Optional[str] = None
    gameTimeAndStatus: Optional[str] = None
    homeCompetitor: Optional[Competitor] = None
    awayCompetitor: Optional[Competitor] = None
    members: Optional[GameMembers] = None
    events: Optional[List[GameEvent]] = dataclasses.field(default_factory=list)
    chartEvents: Optional[Dict[str, List[ChartEvent]]] = dataclasses.field(default_factory=dict)
    topPerformers: Optional[TopPerformers] = None
    widgets: Optional[List[Widget]] = dataclasses.field(default_factory=list)
    statistics: Optional[GameStatistics] = None
    officials: Optional[List[Official]] = dataclasses.field(default_factory=list)
    stages: Optional[List[GameStage]] = dataclasses.field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameData":
        home_comp_data = data.get('homeCompetitor')
        away_comp_data = data.get('awayCompetitor')
        members_data = data.get('members')
        events_data = data.get('events', [])
        chart_events_data = data.get('chartEvents')
        top_performers_data = data.get('topPerformers')
        widgets_data = data.get('widgets', [])
        statistics_data = data.get('statistics')
        officials_data = data.get('officials', [])
        stages_data = data.get('stages', [])

        processed_chart_events = {}
        if chart_events_data and isinstance(chart_events_data, dict):
            for key, events_list_data in chart_events_data.items():
                if isinstance(events_list_data, list):
                    processed_chart_events[key] = [ChartEvent.from_dict(ce) for ce in events_list_data if isinstance(ce, dict)]
        
        return cls(
            lineTypesIds=data.get('lineTypesIds', []),
            id=data.get('id'),
            sportId=data.get('sportId'),
            competitionId=data.get('competitionId'),
            statusId=data.get('statusId'),
            seasonNum=data.get('seasonNum'),
            stageNum=data.get('stageNum'),
            groupNum=data.get('groupNum'),
            roundNum=data.get('roundNum'),
            roundName=data.get('roundName'),
            stageName=data.get('stageName'),
            groupName=data.get('groupName'),
            competitionDisplayName=data.get('competitionDisplayName'),
            startTime=data.get('startTime'),
            statusGroup=data.get('statusGroup'),
            statusText=data.get('statusText'),
            shortStatusText=data.get('shortStatusText'),
            gameTimeAndStatus=data.get('gameTimeAndStatus'),
            homeCompetitor=Competitor.from_dict(home_comp_data) if home_comp_data and isinstance(home_comp_data, dict) else None,
            awayCompetitor=Competitor.from_dict(away_comp_data) if away_comp_data and isinstance(away_comp_data, dict) else None,
            members=GameMembers.from_dict(members_data) if members_data and isinstance(members_data, dict) else None,
            events=[GameEvent.from_dict(e) for e in events_data if isinstance(e, dict)],
            chartEvents=processed_chart_events,
            topPerformers=TopPerformers.from_dict(top_performers_data) if top_performers_data and isinstance(top_performers_data, dict) else None,
            widgets=[Widget.from_dict(w) for w in widgets_data if isinstance(w, dict)],
            statistics=GameStatistics.from_dict(statistics_data) if statistics_data and isinstance(statistics_data, dict) else None,
            officials=[Official.from_dict(o) for o in officials_data if isinstance(o, dict)],
            stages=[GameStage.from_dict(s) for s in stages_data if isinstance(s, dict)]
        )

# ======== وظائف معالجة البيانات ========
def process_game_data(game_data_dict: Dict[str, Any], match_id: Any) -> Dict[str, Any]:
    """
    تنقية قاموس بيانات مباراة واحدة واستخلاص المعلومات الرئيسية.
    """
    filtered_match_data = {}

    # 1. معلومات المباراة الأساسية
    filtered_match_data['matchId'] = game_data_dict.get('id')
    filtered_match_data['competitionName'] = game_data_dict.get('competitionDisplayName')
    filtered_match_data['startTime'] = game_data_dict.get('startTime')
    filtered_match_data['statusText'] = game_data_dict.get('statusText')
    filtered_match_data['shortStatusText'] = game_data_dict.get('shortStatusText')
    filtered_match_data['gameTimeAndStatus'] = game_data_dict.get('gameTimeAndStatus')

    # 2. تهيئة القواميس لربط الـ IDs بالأسماء
    player_id_to_name = {}
    player_id_to_team_name = {}
    team_id_to_name = {}

    home_team_name = None
    away_team_name = None
    home_team_id = None
    away_team_id = None

    # 3. معالجة بيانات الفريق المنزل
    if 'homeCompetitor' in game_data_dict and isinstance(game_data_dict['homeCompetitor'], dict):
        home_comp_data = game_data_dict['homeCompetitor']
        home_team_name = home_comp_data.get('name')
        home_team_id = home_comp_data.get('id')
        if home_team_id:
            team_id_to_name[home_team_id] = home_team_name

        if 'lineups' in home_comp_data and isinstance(home_comp_data['lineups'], dict):
            if 'members' in home_comp_data['lineups'] and isinstance(home_comp_data['lineups']['members'], list):
                for player in home_comp_data['lineups']['members']:
                    p_id = player.get('id')
                    p_name = player.get('name')
                    if p_id and p_name:
                        player_id_to_name[p_id] = p_name
                    if p_id and home_team_name:
                        player_id_to_team_name[p_id] = home_team_name

    # 4. معالجة بيانات الفريق الضيف
    if 'awayCompetitor' in game_data_dict and isinstance(game_data_dict['awayCompetitor'], dict):
        away_comp_data = game_data_dict['awayCompetitor']
        away_team_name = away_comp_data.get('name')
        away_team_id = away_comp_data.get('id')
        if away_team_id:
            team_id_to_name[away_team_id] = away_team_name

        if 'lineups' in away_comp_data and isinstance(away_comp_data['lineups'], dict):
            if 'members' in away_comp_data['lineups'] and isinstance(away_comp_data['lineups']['members'], list):
                for player in away_comp_data['lineups']['members']:
                    p_id = player.get('id')
                    p_name = player.get('name')
                    if p_id and p_name:
                        player_id_to_name[p_id] = p_name
                    if p_id and away_team_name:
                        player_id_to_team_name[p_id] = away_team_name

    # 5. ملء بيانات اللاعبين من أعضاء الفريق
    if 'members' in game_data_dict and isinstance(game_data_dict['members'], dict):
        if 'homeTeamMembers' in game_data_dict['members'] and isinstance(game_data_dict['members']['homeTeamMembers'], list):
            for player in game_data_dict['members']['homeTeamMembers']:
                p_id = player.get('id')
                p_name = player.get('name')
                if p_id and p_name and p_id not in player_id_to_name:
                    player_id_to_name[p_id] = p_name
                    if home_team_name and p_id not in player_id_to_team_name:
                        player_id_to_team_name[p_id] = home_team_name

        if 'awayTeamMembers' in game_data_dict['members'] and isinstance(game_data_dict['members']['awayTeamMembers'], list):
            for player in game_data_dict['members']['awayTeamMembers']:
                p_id = player.get('id')
                p_name = player.get('name')
                if p_id and p_name and p_id not in player_id_to_name:
                    player_id_to_name[p_id] = p_name
                    if away_team_name and p_id not in player_id_to_team_name:
                        player_id_to_team_name[p_id] = away_team_name
    else:
        print(f"    - تحذير: المفتاح 'members' غير موجود أو ليس قاموساً للمباراة {match_id}")

    # 6. بناء كائنات الفريق باستخدام dataclasses
    home_competitor_obj = None
    if 'homeCompetitor' in game_data_dict and isinstance(game_data_dict['homeCompetitor'], dict):
        home_competitor_obj = Competitor.from_dict(game_data_dict['homeCompetitor'])
        home_team_info = dataclasses.asdict(home_competitor_obj)
        if home_team_info.get('lineups') and home_team_info['lineups'].get('members'):
            for player in home_team_info['lineups']['members']:
                if 'id' in player and player['id'] in player_id_to_name:
                    player['name'] = player_id_to_name[player['id']]
        filtered_match_data['homeTeam'] = home_team_info
    else:
        print(f"    - تحذير: المفتاح 'homeCompetitor' غير موجود للمباراة {match_id}")

    away_competitor_obj = None
    if 'awayCompetitor' in game_data_dict and isinstance(game_data_dict['awayCompetitor'], dict):
        away_competitor_obj = Competitor.from_dict(game_data_dict['awayCompetitor'])
        away_team_info = dataclasses.asdict(away_competitor_obj)
        if away_team_info.get('lineups') and away_team_info['lineups'].get('members'):
            for player in away_team_info['lineups']['members']:
                if 'id' in player and player['id'] in player_id_to_name:
                    player['name'] = player_id_to_name[player['id']]
        filtered_match_data['awayTeam'] = away_team_info
    else:
        print(f"    - تحذير: المفتاح 'awayCompetitor' غير موجود للمباراة {match_id}")

    # 7. معالجة الأحداث الرئيسية
    if 'events' in game_data_dict and isinstance(game_data_dict['events'], list):
        filtered_events = []
        for event_data in game_data_dict['events']:
            try:
                event_obj = GameEvent.from_dict(event_data)
                event_info = dataclasses.asdict(event_obj)

                # ربط أسماء اللاعبين والفرق بالأحداث
                if event_info.get('playerId') in player_id_to_name:
                    event_info['playerName'] = player_id_to_name[event_info['playerId']]
                if event_info.get('competitorId') in team_id_to_name:
                    event_info['teamName'] = team_id_to_name[event_info['competitorId']]

                filtered_events.append(event_info)
            except Exception as e:
                print(f"    - خطأ في معالجة حدث: {e}")
        filtered_match_data['events'] = filtered_events
    else:
        print(f"    - تحذير: المفتاح 'events' غير موجود للمباراة {match_id}")

    # 8. معالجة أحداث الرسم البياني
    if 'chartEvents' in game_data_dict and isinstance(game_data_dict['chartEvents'], dict):
        extracted_chart_events = {}
        for key, events_list in game_data_dict['chartEvents'].items():
            if isinstance(events_list, list):
                processed_events = []
                for event_data in events_list:
                    try:
                        chart_event_obj = ChartEvent.from_dict(event_data)
                        chart_event_info = dataclasses.asdict(chart_event_obj)
                        
                        if chart_event_info.get('playerId') in player_id_to_name:
                            chart_event_info['playerName'] = player_id_to_name[chart_event_info['playerId']]
                        if chart_event_info.get('playerId') in player_id_to_team_name:
                            chart_event_info['teamName'] = player_id_to_team_name[chart_event_info['playerId']]

                        # تحديد الفريق المعني
                        if chart_event_info.get('competitorNum') == 1 and home_team_name:
                            chart_event_info['involvedTeam'] = home_team_name
                        elif chart_event_info.get('competitorNum') == 2 and away_team_name:
                            chart_event_info['involvedTeam'] = away_team_name

                        processed_events.append(chart_event_info)
                    except Exception as e:
                        print(f"    - خطأ في معالجة حدث الرسم: {e}")
                extracted_chart_events[key] = processed_events
        filtered_match_data['chartEvents'] = extracted_chart_events
    else:
        print(f"    - تحذير: المفتاح 'chartEvents' غير موجود للمباراة {match_id}")

    # 9. معالجة أفضل اللاعبين أداءً
    if 'topPerformers' in game_data_dict and isinstance(game_data_dict['topPerformers'], dict):
        top_performers_obj = TopPerformers.from_dict(game_data_dict['topPerformers'])
        filtered_top_performers_categories = []
        if top_performers_obj.categories:
            for category_obj in top_performers_obj.categories:
                category_info = dataclasses.asdict(category_obj)
                
                # تحديث أسماء اللاعبين للفريق المنزل
                if category_info.get('homePlayer'):
                    player_id = category_info['homePlayer'].get('id')
                    athlete_id = category_info['homePlayer'].get('athleteId')
                    if player_id in player_id_to_name:
                        category_info['homePlayer']['name'] = player_id_to_name[player_id]
                    elif athlete_id in player_id_to_name:
                        category_info['homePlayer']['name'] = player_id_to_name[athlete_id]
                
                # تحديث أسماء اللاعبين للفريق الضيف
                if category_info.get('awayPlayer'):
                    player_id = category_info['awayPlayer'].get('id')
                    athlete_id = category_info['awayPlayer'].get('athleteId')
                    if player_id in player_id_to_name:
                        category_info['awayPlayer']['name'] = player_id_to_name[player_id]
                    elif athlete_id in player_id_to_name:
                        category_info['awayPlayer']['name'] = player_id_to_name[athlete_id]
                
                filtered_top_performers_categories.append(category_info)
        filtered_match_data['topPerformers'] = filtered_top_performers_categories
    else:
        print(f"    - تحذير: المفتاح 'topPerformers' غير موجود للمباراة {match_id}")

    # 10. معالجة الإحصائيات والمعلومات الأخرى
    # [الكود المتبقي للمراحل الأخرى...]
    
    return filtered_match_data

def extract_data_to_dataframes(df_games: pd.DataFrame):
    """
    تستخرج البيانات من DataFrame المباريات إلى DataFrames منفصلة.
    """
    # [تنفيذ الدالة كما هي مع الحفاظ على المنطق الأصلي...]
    pass

# ======== الكود الرئيسي للتنفيذ ========
if __name__ == "__main__":
    # [الكود الرئيسي للتنفيذ...]
    pass
