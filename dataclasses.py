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
    members = game_data_dict.get('members')
    if isinstance(members, dict):
        # كما هو في الكود الحالي
        if 'homeTeamMembers' in members and isinstance(members['homeTeamMembers'], list):
            for player in members['homeTeamMembers']:
                p_id = player.get('id')
                p_name = player.get('name')
                if p_id and p_name and p_id not in player_id_to_name:
                    player_id_to_name[p_id] = p_name
                    if home_team_name and p_id not in player_id_to_team_name:
                        player_id_to_team_name[p_id] = home_team_name

        if 'awayTeamMembers' in members and isinstance(members['awayTeamMembers'], list):
            for player in members['awayTeamMembers']:
                p_id = player.get('id')
                p_name = player.get('name')
                if p_id and p_name and p_id not in player_id_to_name:
                    player_id_to_name[p_id] = p_name
                    if away_team_name and p_id not in player_id_to_team_name:
                        player_id_to_team_name[p_id] = away_team_name

    elif isinstance(members, list):
        # معالجة القائمة وربط اللاعبين بفريقهم عبر competitorId
        for player in members:
            if isinstance(player, dict):
                p_id = player.get('id')
                p_name = player.get('name')
                competitor_id = player.get('competitorId')
                if p_id and p_name and p_id not in player_id_to_name:
                    player_id_to_name[p_id] = p_name
                    # حدد الفريق المناسب
                    if competitor_id == home_team_id and home_team_name:
                        player_id_to_team_name[p_id] = home_team_name
                    elif competitor_id == away_team_id and away_team_name:
                        player_id_to_team_name[p_id] = away_team_name
    elif members is None:
        pass  # لا داعي لأي رسالة هنا
    else:
        print(f"    - تنبيه: المفتاح 'members' من نوع غير متوقع ({type(members)}) للمباراة {match_id}")

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
# 10. معالجة الإحصائيات والمعلومات الأخرى (نسخة ديناميكية)
def extract_team_stats(competitor: dict) -> dict:
    """
    استخراج إحصائيات الفريق إما من statistics أو بجمع stats من جميع اللاعبين (members).
    يرجع dict مثل: {'corners': {'home': 2, 'away': 3}, ...} أو {'Total Shots': 10, ...}
    """
    # أولاً: جرِّب statistics المباشر
    stats = competitor.get('statistics')
    if isinstance(stats, dict) and stats:  # إذا فيه بيانات
        return stats

    # ثانياً: جرِّب جمع stats من اللاعبين إذا كان statistics غير موجود أو فارغ
    stats_agg = {}
    if isinstance(competitor.get('lineups'), dict):
        members = competitor['lineups'].get('members', [])
        for player in members:
            for stat in player.get('stats', []):
                name = stat.get('name')
                value = stat.get('value')
                # جمع القيم الرقمية فقط، تجاهل النصوص مثل "90'"
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue
                if name:
                    stats_agg[name] = stats_agg.get(name, 0) + value
    return stats_agg

def extract_data_to_dataframes(df_games: pd.DataFrame):
    """
    تستخرج البيانات من DataFrame المباريات إلى DataFrames منفصلة.
    """
    all_matches_data = []
    all_players_data = []
    all_events_data = []
    all_chart_events_data = []
    all_top_performers_data = []
    all_widgets_data = []
    all_officials_data = []
    all_stages_data = []

    if 'game' not in df_games.columns or df_games['game'].isnull().all():
        print("تحذير: عمود 'game' غير موجود أو فارغ في DataFrame المدخل.")
        return [pd.DataFrame()] * 8

    total_games = len(df_games)
    print(f"جاري معالجة {total_games} مباراة...")

    for index, row in df_games.iterrows():
        game_data_dict = row['game']
        match_id = game_data_dict.get('id', f'unknown_{index}')

        try:
            filtered_data = process_game_data(game_data_dict, match_id)
            
            # 1. بيانات المباريات الأساسية
            # داخل process_game_data قبل return filtered_match_data:
            home_stats = {}
            away_stats = {}
            if 'homeCompetitor' in game_data_dict and isinstance(game_data_dict['homeCompetitor'], dict):
                home_stats = extract_team_stats(game_data_dict['homeCompetitor'])
            if 'awayCompetitor' in game_data_dict and isinstance(game_data_dict['awayCompetitor'], dict):
                away_stats = extract_team_stats(game_data_dict['awayCompetitor'])

            filtered_match_data['homeTeamStats'] = home_stats
            filtered_match_data['awayTeamStats'] = away_stats

            # لم تعد بحاجة لإضافة filtered_match_data['statistics'] بالطريقة السابقة
            return filtered_match_data

            # 2. بيانات اللاعبين
            for team_key in ['homeTeam', 'awayTeam']:
                team_data = filtered_data.get(team_key)
                if team_data and team_data.get('lineups') and team_data['lineups'].get('members'):
                    for player_data in team_data['lineups']['members']:
                        player_entry = {
                            'matchId': match_id,
                            'playerId': player_data.get('id'),
                            'playerName': player_data.get('name'),
                            'teamName': team_data.get('name'),
                            'isHomeTeam': (team_key == 'homeTeam'),
                            'positionName': player_data.get('position', {}).get('name') if player_data.get('position') else None,
                            'isStarter': player_data.get('statusText') == 'Starter',
                            'formation_name': player_data.get('formation', {}).get('name') if player_data.get('formation') else None,
                            'ranking': player_data.get('ranking'),
                            'popularityRank': player_data.get('popularityRank'),
                            'hasStats': player_data.get('hasStats'),
                            'nationalId': player_data.get('nationalId'),
                        }
                        
                        # إضافة الإحصائيات
                        if player_data.get('stats'):
                            for stat in player_data['stats']:
                                # تحديد اسم الإحصائية
                                stat_name = stat.get('name')
                                stat_type = stat.get('type')
                                
                                if stat_name:
                                    stat_key = f"stat_{stat_name}"
                                elif stat_type is not None:
                                    stat_key = f"stat_type_{stat_type}"
                                else:
                                    stat_key = "stat_unknown"
                                
                                player_entry[stat_key] = stat.get('value')
                        
                        all_players_data.append(player_entry)

            # 3. أحداث المباراة
            if 'events' in filtered_data:
                for event in filtered_data['events']:
                    event['matchId'] = match_id
                    all_events_data.append(event)

            # 4. أحداث الرسم البياني
            if 'chartEvents' in filtered_data:
                for event_type, events_list in filtered_data['chartEvents'].items():
                    for event in events_list:
                        event['matchId'] = match_id
                        event['chartEventTypeCategory'] = event_type
                        all_chart_events_data.append(event)

            # 5. أفضل اللاعبين أداءً
            if 'topPerformers' in filtered_data:
                for category in filtered_data['topPerformers']:
                    for team_key in ['homePlayer', 'awayPlayer']:
                        player_data = category.get(team_key)
                        if player_data:
                            top_perf_entry = {
                                'matchId': match_id,
                                'categoryName': category.get('name'),
                                'playerId': player_data.get('id'),
                                'athleteId': player_data.get('athleteId'),
                                'playerName': player_data.get('name'),
                                'teamName': filtered_data['homeTeam']['name'] if team_key == 'homePlayer' else filtered_data['awayTeam']['name'],
                                'isHomeTeam': (team_key == 'homePlayer'),
                                'positionName': player_data.get('positionName'),
                                'positionShortName': player_data.get('positionShortName'),
                                'imageVersion': player_data.get('imageVersion'),
                                'nameForURL': player_data.get('nameForURL')
                            }
                            
                            # إضافة الإحصائيات
                            if player_data.get('stats'):
                                for stat in player_data['stats']:
                                    # تحديد اسم الإحصائية
                                    stat_name = stat.get('name')
                                    stat_type = stat.get('type')
                                    
                                    if stat_name:
                                        stat_key = f"stat_{stat_name}"
                                    elif stat_type is not None:
                                        stat_key = f"stat_type_{stat_type}"
                                    else:
                                        stat_key = "stat_unknown"
                                    
                                    top_perf_entry[stat_key] = stat.get('value')
                            
                            all_top_performers_data.append(top_perf_entry)

            # 6. الأدوات (Widgets)
            if 'widgets' in filtered_data:
                for widget in filtered_data['widgets']:
                    widget['matchId'] = match_id
                    all_widgets_data.append(widget)

            # 7. المسؤولون
            if 'officials' in filtered_data:
                for official in filtered_data['officials']:
                    official['matchId'] = match_id
                    all_officials_data.append(official)

            # 8. مراحل المباراة
            if 'stages' in filtered_data:
                for stage in filtered_data['stages']:
                    stage['matchId'] = match_id
                    all_stages_data.append(stage)

        except Exception as e:
            print(f"    - خطأ في معالجة المباراة {match_id}: {e}")
            import traceback
            traceback.print_exc()

    # إنشاء DataFrames
    df_matches = pd.DataFrame(all_matches_data)
    df_players = pd.DataFrame(all_players_data)
    df_events = pd.DataFrame(all_events_data)
    df_chart_events = pd.DataFrame(all_chart_events_data)
    df_top_performers = pd.DataFrame(all_top_performers_data)
    df_widgets = pd.DataFrame(all_widgets_data)
    df_officials = pd.DataFrame(all_officials_data)
    df_stages = pd.DataFrame(all_stages_data)

    print("\nتم استخلاص البيانات بنجاح!")
    print(f"  - المباريات: {len(df_matches)} سجل")
    print(f"  - اللاعبون: {len(df_players)} سجل")
    print(f"  - الأحداث: {len(df_events)} سجل")
    print(f"  - أحداث الرسم: {len(df_chart_events)} سجل")
    print(f"  - أفضل اللاعبين: {len(df_top_performers)} سجل")
    print(f"  - الأدوات: {len(df_widgets)} سجل")
    print(f"  - المسؤولون: {len(df_officials)} سجل")
    print(f"  - المراحل: {len(df_stages)} سجل")
    
    return df_matches, df_players, df_events, df_chart_events, df_top_performers, df_widgets, df_officials, df_stages

# ======== الكود الرئيسي للتنفيذ ========
if __name__ == "__main__":
    # مسار ملف البيانات
    PICKLE_PATH = r'C:\Users\E.abed\Desktop\FootballData\all_games_data.pkl'
    OUTPUT_DIR = r'C:\Users\E.abed\Desktop\FootballData\processed_data'
    
    try:
        print(f"جاري تحميل البيانات من: {PICKLE_PATH}")
        df_games = pd.read_pickle(PICKLE_PATH)
        
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"تم إنشاء مجلد الإخراج: {OUTPUT_DIR}")
        
        # معالجة البيانات
        results = extract_data_to_dataframes(df_games)
        df_names = [
            'matches', 'players', 'events', 
            'chart_events', 'top_performers', 
            'widgets', 'officials', 'stages'
        ]
        
        # حفظ النتائج بصيغة JSON
        for i, df in enumerate(results):
            if not df.empty:
                output_path = os.path.join(OUTPUT_DIR, f'df_{df_names[i]}.json')
                df.to_json(output_path, orient='records', force_ascii=False, indent=2)
                print(f"تم حفظ {df_names[i]} ({len(df)} سجل) في: {output_path}")
        
        print("\nتم الانتهاء من معالجة جميع البيانات بنجاح!")
        
    except FileNotFoundError:
        print(f"خطأ: الملف {PICKLE_PATH} غير موجود!")
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
