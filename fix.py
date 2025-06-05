import pandas as pd
import json
import os
import dataclasses
from typing import List, Dict, Any, Optional
import traceback

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
    athleteId: Optional[int] = None  # <<< الحل الجديد

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
            #shortName=data.get('shortName')
            athleteId=data.get('athleteId')  # <<< الحل الجديد
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
    x: Optional[float] = dataclasses.field(default=None)  # <<< التعديل
    y: Optional[float] = dataclasses.field(default=None)  # <<< التعديل
    # إضافة حقل جديد للتعامل مع الاسم
    playerName: Optional[str] = None  # <<< الحل الجديد

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
            x=data.get('x', None),  # القيمة الافتراضية None
            y=data.get('y', None),  # القيمة الافتراضية None
            # نسخ اسم اللاعب مباشرة من البيانات الأصلية
            playerName=data.get('playerName')  # <<< الحل الجديد
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
    members: Optional[Dict[str, List[Dict[str, Any]]]] = dataclasses.field(default_factory=dict) # <<< التعديل
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
        members=data.get('members', {})
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
            members=GameMembers.from_dict(members) if members and isinstance(members, dict) else None,
            events=[GameEvent.from_dict(e) for e in events_data if isinstance(e, dict)],
            chartEvents=processed_chart_events,
            topPerformers=TopPerformers.from_dict(top_performers_data) if top_performers_data and isinstance(top_performers_data, dict) else None,
            widgets=[Widget.from_dict(w) for w in widgets_data if isinstance(w, dict)],
            statistics=GameStatistics.from_dict(statistics_data) if statistics_data and isinstance(statistics_data, dict) else None,
            officials=[Official.from_dict(o) for o in officials_data if isinstance(o, dict)],
            stages=[GameStage.from_dict(s) for s in stages_data if isinstance(s, dict)]
        )

import pandas as pd
import json
import os
import dataclasses
from typing import List, Dict, Any, Optional

# ... (جميع تعريفات الـ dataclasses تبقى كما هي) ...

# متغير عام لتجميع جميع مفاتيح الإحصائيات
all_stat_keys_global = set()

# ======== دالة استخراج إحصائيات الفريق ========
def extract_team_stats(competitor: dict) -> dict:
    """
    تستخرج إحصائيات الفريق من مصادر متعددة في بنية البيانات
    وتجمع جميع مفاتيح الإحصائيات التي تم مواجهتها
    """
    global all_stat_keys_global
    stats = {}
    
    # المصدر 1: من 'statistics' المباشر
    if isinstance(competitor.get('statistics'), dict):
        stats.update(competitor['statistics'])
        # جمع المفاتيح
        all_stat_keys_global.update(competitor['statistics'].keys())
    
    # المصدر 2: من 'status'
    elif isinstance(competitor.get('status'), dict):
        stats.update(competitor['status'])
        # جمع المفاتيح
        all_stat_keys_global.update(competitor['status'].keys())
    
    # المصدر 3: من إحصائيات اللاعبين
    elif isinstance(competitor.get('lineups'), dict):
        members = competitor['lineups'].get('members', [])
        if members:
            # نجمع إحصائيات من كل اللاعبين
            player_stat_keys = set()
            for player in members:
                if isinstance(player.get('stats'), list):
                    for stat in player['stats']:
                        name = stat.get('name')
                        value = stat.get('value')
                        if name:
                            # جمع اسم الإحصائية
                            player_stat_keys.add(name)
                            
                            # معالجة القيمة
                            try:
                                value = float(value)
                                stats[name] = stats.get(name, 0) + value
                            except (TypeError, ValueError):
                                stats[name] = value
            
            # إضافة مفاتيح إحصائيات اللاعبين للمجموعة العامة
            all_stat_keys_global.update(player_stat_keys)
    
    return stats

# ======== دالة جلب الإحصائية بعدة احتمالات ========
def get_stat(stats: dict, *keys):
    """
    جلب قيمة إحصائية من dict بعدة احتمالات للأسماء (case-insensitive)
    ويدعم تنسيقات مختلفة للقيم (أرقام، نصوص، نسب مئوية)
    """
    if not isinstance(stats, dict):
        return None
    
    # البحث في المفاتيح المباشرة
    for key in keys:
        if key in stats:
            return stats[key]
    
    # البحث بأحرف صغيرة/كبيرة
    for stat_key, value in stats.items():
        stat_key_lower = stat_key.lower()
        for key in keys:
            if key.lower() == stat_key_lower:
                return value
    
    # البحث في القيم المعقدة (مثل {'home': 5, 'away': 3})
    for stat_key, value in stats.items():
        if isinstance(value, dict):
            for sub_key in ['value', 'home', 'total']:
                if sub_key in value:
                    return value[sub_key]
    
    return None


# ======== وظائف معالجة البيانات ========
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

   # 2. نظام متكامل لإدارة بيانات اللاعبين
    player_id_to_info = {}
    athlete_id_to_info = {}
    player_id_to_team = {}
    team_id_to_name = {}

    home_team_name = None
    away_team_name = None
    home_team_id = None
    away_team_id = None
    

    # 3. تجميع بيانات اللاعبين من جميع المصادر
    def register_player(player_data: Dict[str, Any], team_name: str, is_home: bool):
        """تسجيل لاعب في النظام المركزي"""
        p_id = player_data.get('id')
        athlete_id = player_data.get('athleteId')
        
        if not p_id and not athlete_id:
            return
        
        # إنشاء أو تحديث سجل اللاعب
        player_info = {}
        if p_id and p_id in player_id_to_info:
            player_info = player_id_to_info[p_id]
        elif athlete_id and athlete_id in athlete_id_to_info:
            player_info = athlete_id_to_info[athlete_id]
        else:
            player_info = {}
        
        # تحديث المعلومات من المصدر الحالي
        if player_data.get('name'):
            player_info['name'] = player_data['name']
        if player_data.get('shortName'):
            player_info['shortName'] = player_data['shortName']
        if player_data.get('position') and isinstance(player_data['position'], dict):
            player_info['positionName'] = player_data['position'].get('name')
        if player_data.get('jerseyNumber'):
            player_info['jerseyNumber'] = player_data['jerseyNumber']
        if player_data.get('nameForURL'):
            player_info['nameForURL'] = player_data['nameForURL']
        
        # التسجيل في أنظمة التخزين
        if p_id:
            player_id_to_info[p_id] = player_info
            player_id_to_team[p_id] = team_name
        if athlete_id:
            athlete_id_to_info[athlete_id] = player_info
            player_id_to_team[athlete_id] = team_name


    # 4. تجميع بيانات من الفريق المنزل
    if 'homeCompetitor' in game_data_dict and isinstance(game_data_dict['homeCompetitor'], dict):
        home_comp = game_data_dict['homeCompetitor']
        home_team_name = home_comp.get('name')
        home_team_id = home_comp.get('id')
        team_id_to_name[home_team_id] = home_team_name

            
        # اللاعبين في التشكيلة
        if home_comp.get('lineups') and isinstance(home_comp['lineups'], dict):
            members = home_comp['lineups'].get('members', [])
            for player in members:
                register_player(player, home_team_name, True)

        # اللاعبين في الإحصائيات
        if home_comp.get('statsCategory') and isinstance(home_comp['statsCategory'], list):
            for category in home_comp['statsCategory']:
                if category.get('orderByPosition') and isinstance(category['orderByPosition'], list):
                    for player in category['orderByPosition']:
                        register_player(player, home_team_name, True)

                            
    # 5. تجميع بيانات من الفريق الضيف
    if 'awayCompetitor' in game_data_dict and isinstance(game_data_dict['awayCompetitor'], dict):
        away_comp = game_data_dict['awayCompetitor']
        away_team_name = away_comp.get('name')
        away_team_id = away_comp.get('id')
        team_id_to_name[away_team_id] = away_team_name

        # اللاعبين في التشكيلة
        if away_comp.get('lineups') and isinstance(away_comp['lineups'], dict):
            members = away_comp['lineups'].get('members', [])
            for player in members:
                register_player(player, away_team_name, False)


        # اللاعبين في الإحصائيات
        if away_comp.get('statsCategory') and isinstance(away_comp['statsCategory'], list):
            for category in away_comp['statsCategory']:
                if category.get('orderByPosition') and isinstance(category['orderByPosition'], list):
                    for player in category['orderByPosition']:
                        register_player(player, away_team_name, False)

        
        # 6. تجميع بيانات من أعضاء الفريق (المصدر الأساسي)
    if 'members' in game_data_dict and isinstance(game_data_dict['members'], dict):
        members_data = game_data_dict['members']

        # فريق المنزل
        if 'homeTeamMembers' in members_data and isinstance(members_data['homeTeamMembers'], list):
            for player in members_data['homeTeamMembers']:
                register_player(player, home_team_name, True)
        
        # فريق الضيف
        if 'awayTeamMembers' in members_data and isinstance(members_data['awayTeamMembers'], list):
            for player in members_data['awayTeamMembers']:
                register_player(player, away_team_name, False)


    # 6. بناء كائنات الفريق باستخدام dataclasses
    # الفريق المنزل
    if 'homeCompetitor' in game_data_dict and isinstance(game_data_dict['homeCompetitor'], dict):
        home_competitor_obj = Competitor.from_dict(game_data_dict['homeCompetitor'])
        home_team_info = dataclasses.asdict(home_competitor_obj)
        
        if home_team_info.get('lineups') and home_team_info['lineups'].get('members'):
            for player in home_team_info['lineups']['members']:
                p_id = player.get('id')
                if p_id and p_id in player_id_to_info:
                    # تحديث جميع الحقول من المصدر الموثوق
                    player['name'] = player_id_to_info[p_id].get('name', player.get('name', ''))
                    player['shortName'] = player_id_to_info[p_id].get('shortName', player.get('shortName', ''))
                    player['jerseyNumber'] = player_id_to_info[p_id].get('jerseyNumber', player.get('jerseyNumber', ''))
                    player['nameForURL'] = player_id_to_info[p_id].get('nameForURL', player.get('nameForURL', ''))
        
        filtered_match_data['homeTeam'] = home_team_info
    else:
        print(f"    - تحذير: المفتاح 'homeCompetitor' غير موجود للمباراة {match_id}")

    # الفريق الضيف (باستخدام المتغيرات الصحيحة)
    if 'awayCompetitor' in game_data_dict and isinstance(game_data_dict['awayCompetitor'], dict):
        away_competitor_obj = Competitor.from_dict(game_data_dict['awayCompetitor'])  # تصحيح هنا
        away_team_info = dataclasses.asdict(away_competitor_obj)  # تصحيح هنا
        
        if away_team_info.get('lineups') and away_team_info['lineups'].get('members'):
            for player in away_team_info['lineups']['members']:
                p_id = player.get('id')
                if p_id and p_id in player_id_to_info:
                    # تحديث جميع الحقول من المصدر الموثوق
                    player['name'] = player_id_to_info[p_id].get('name', player.get('name', ''))
                    player['shortName'] = player_id_to_info[p_id].get('shortName', player.get('shortName', ''))
                    player['jerseyNumber'] = player_id_to_info[p_id].get('jerseyNumber', player.get('jerseyNumber', ''))
                    player['nameForURL'] = player_id_to_info[p_id].get('nameForURL', player.get('nameForURL', ''))
        
        filtered_match_data['awayTeam'] = away_team_info  # تصحيح هنا
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
                player_id = event_info.get('playerId')
                if player_id and player_id in player_id_to_info:
                    event_info['playerName'] = player_id_to_info[player_id].get('name', '')
                
                competitor_id = event_info.get('competitorId')
                if competitor_id and competitor_id in team_id_to_name:
                    event_info['teamName'] = team_id_to_name[competitor_id]

                filtered_events.append(event_info)
            except Exception as e:
                print(f"    - خطأ في معالجة حدث: {e}")
        filtered_match_data['events'] = filtered_events
    else:
        print(f"    - تحذير: المفتاح 'events' غير موجود للمباراة {match_id}")

    # 8. معالجة chartEvents
    # 9. ربط بيانات اللاعبين في أحداث الرسم البياني
    if 'chartEvents' in game_data_dict and isinstance(game_data_dict['chartEvents'], dict):
        extracted_chart_events = {}
        for key, events_list in game_data_dict['chartEvents'].items():
            if isinstance(events_list, list):
                processed_events = []
                for event_data in events_list:
                    try:
                        chart_event_obj = ChartEvent.from_dict(event_data)
                        chart_event_info = dataclasses.asdict(chart_event_obj)
                        
                        # ربط معلومات اللاعب باستخدام نظامنا المركزي
                        player_id = event_data.get('playerId')
                        athlete_id = event_data.get('athleteId')
                        
                        player_info = {}
                        if player_id and player_id in player_id_to_info:
                            player_info = player_id_to_info[player_id]
                        elif athlete_id and athlete_id in athlete_id_to_info:
                            player_info = athlete_id_to_info[athlete_id]
                        
                        if player_info:
                            for field in ['name', 'shortName', 'jerseyNumber', 'positionName']:
                                if field in player_info:
                                    chart_event_info[field] = player_info[field]

                        
                        # تحديد الفريق المعني
                        competitor_num = chart_event_info.get('competitorNum')
                        if competitor_num == 1 and home_team_name:
                            chart_event_info['involvedTeam'] = home_team_name
                        elif competitor_num == 2 and away_team_name:
                            chart_event_info['involvedTeam'] = away_team_name

                        processed_events.append(chart_event_info)
                    except Exception as e:
                        print(f"    - خطأ في معالجة حدث الرسم: {e}")
                extracted_chart_events[key] = processed_events
        filtered_match_data['chartEvents'] = extracted_chart_events
    else:
        print(f"    - تحذير: المفتاح 'chartEvents' غير موجود للمباراة {match_id}")

    # 10. معالجة الإحصائيات
    home_stats = {}
    away_stats = {}
    
    if 'homeCompetitor' in game_data_dict and isinstance(game_data_dict['homeCompetitor'], dict):
        home_stats = extract_team_stats(game_data_dict['homeCompetitor'])
    
    if 'awayCompetitor' in game_data_dict and isinstance(game_data_dict['awayCompetitor'], dict):
        away_stats = extract_team_stats(game_data_dict['awayCompetitor'])
    
    filtered_match_data['homeTeamStats'] = home_stats
    filtered_match_data['awayTeamStats'] = away_stats

    # 11. معالجة widgets
    if 'widgets' in game_data_dict and isinstance(game_data_dict['widgets'], list):
        filtered_widgets = []
        for widget_data in game_data_dict['widgets']:
            widget_obj = Widget.from_dict(widget_data)
            filtered_widgets.append(dataclasses.asdict(widget_obj))
        if filtered_widgets:
            filtered_match_data['widgets'] = filtered_widgets
    else:
        print(f"    - تحذير: المفتاح 'widgets' غير موجود للمباراة {match_id}")

    # 12. معالجة officials
    if 'officials' in game_data_dict and isinstance(game_data_dict['officials'], list):
        filtered_officials = []
        for official_data in game_data_dict['officials']:
            official_obj = Official.from_dict(official_data)
            filtered_officials.append(dataclasses.asdict(official_obj))
        if filtered_officials:
            filtered_match_data['officials'] = filtered_officials
    else:
        print(f"    - تحذير: المفتاح 'officials' غير موجود للمباراة {match_id}")

    # 13. معالجة stages
    if 'stages' in game_data_dict and isinstance(game_data_dict['stages'], list):
        filtered_stages = []
        for stage_data in game_data_dict['stages']:
            stage_obj = GameStage.from_dict(stage_data)
            filtered_stages.append(dataclasses.asdict(stage_obj))
        if filtered_stages:
            filtered_match_data['stages'] = filtered_stages
    else:
        print(f"    - تحذير: المفتاح 'stages' غير موجود للمباراة {match_id}")
    print(f"معلومات اللاعبين للمباراة {match_id}:")
    # في دالة process_game_data
    print(f"معالجة المباراة {match_id}")
    print(f"عدد اللاعبين في الفريق المنزل: {len(player_id_to_info)}")
    if player_id_to_info:
        sample_player = next(iter(player_id_to_info.values()))
        print(f"لاعب عينة: {sample_player.get('name')}")

    return filtered_match_data

def extract_data_to_dataframes(df_games: pd.DataFrame):

    all_matches_data = []
    all_players_data = []
    all_events_data = []
    all_chart_events_data = []
    all_top_performers_data = []
    all_widgets_data = []
    all_officials_data = []
    all_stages_data = []

    if 'game' not in df_games.columns or df_games['game'].empty:
        print("لا يوجد عمود 'game' أو أنه فارغ في DataFrame المدخل.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    total_games = len(df_games)
    print(f"جاري معالجة {total_games} مباراة...")

    for index, row in df_games.iterrows():
        game_data_dict = row['game']
        match_id = game_data_dict.get('id', f'unknown_{index}')

        try:
            filtered_data = process_game_data(game_data_dict, match_id)
            
            home_stats = filtered_data.get('homeTeamStats', {})
            away_stats = filtered_data.get('awayTeamStats', {})

            match_info = {
                'matchId': filtered_data.get('matchId'),
                'competitionName': filtered_data.get('competitionName'),
                'startTime': filtered_data.get('startTime'),
                'statusText': filtered_data.get('statusText'),
                'shortStatusText': filtered_data.get('shortStatusText'),
                'gameTimeAndStatus': filtered_data.get('gameTimeAndStatus'),
                'homeTeamName': filtered_data.get('homeTeam', {}).get('name'),
                'homeTeamScore': filtered_data.get('homeTeam', {}).get('score'),
                'awayTeamName': filtered_data.get('awayTeam', {}).get('name'),
                'awayTeamScore': filtered_data.get('awayTeam', {}).get('score'),
                # إحصائيات متقدمة
                'corners_home': get_stat(home_stats, "Corners", "Corner Kicks", "corners"),
                'corners_away': get_stat(away_stats, "Corners", "Corner Kicks", "corners"),
                'shotsOnTarget_home': get_stat(home_stats, "Shots On Target", "shotsOnTarget"),
                'shotsOnTarget_away': get_stat(away_stats, "Shots On Target", "shotsOnTarget"),
                'shotsTotal_home': get_stat(home_stats, "Total Shots", "Shots"),
                'shotsTotal_away': get_stat(away_stats, "Total Shots", "Shots"),
                'passesCompleted_home': get_stat(home_stats, "Passes Completed"),
                'passesCompleted_away': get_stat(away_stats, "Passes Completed"),
                'possession_home': get_stat(home_stats, "Possession", "Ball Possession", "possession"),
                'possession_away': get_stat(away_stats, "Possession", "Ball Possession", "possession"),
                'fouls_home': get_stat(home_stats, "Fouls", "Fouls Committed"),
                'fouls_away': get_stat(away_stats, "Fouls", "Fouls Committed"),
                'offsides_home': get_stat(home_stats, "Offsides"),
                'offsides_away': get_stat(away_stats, "Offsides"),
                'saves_home': get_stat(home_stats, "Saves", "Goalkeeper Saves"),
                'saves_away': get_stat(away_stats, "Saves", "Goalkeeper Saves"),
                'yellowCards_home': get_stat(home_stats, "Yellow Cards", "Yellow cards"),
                'yellowCards_away': get_stat(away_stats, "Yellow Cards", "Yellow cards"),
                'redCards_home': get_stat(home_stats, "Red Cards", "Red cards"),
                'redCards_away': get_stat(away_stats, "Red Cards", "Red cards"),
                
            }
            
            all_matches_data.append(match_info)
            
            # 2. بيانات اللاعبين
            home_comp_obj = filtered_data.get('homeTeam')
            if home_comp_obj and home_comp_obj.get('lineups') and home_comp_obj['lineups'].get('members'):
                for player_data in home_comp_obj['lineups']['members']:
                    # معالجة آمنة للحقول المتداخلة
                    position_name = player_data.get('position', {}).get('name') if isinstance(player_data.get('position'), dict) else None
                    formation_name = player_data.get('formation', {}).get('name') if isinstance(player_data.get('formation'), dict) else None
                        
                    player_entry = {
                        'matchId': match_id,
                        'playerId': player_data.get('id'),
                        'playerName': player_data.get('name'),
                        'teamName': home_comp_obj.get('name'),
                        'isHomeTeam': (team_key == 'homeTeam'),
                        'positionName': position_name,
                        'isStarter': player_data.get('statusText') == 'Starter',
                        'formation_name': formation_name,
                        'ranking': player_data.get('ranking'),
                        'popularityRank': player_data.get('popularityRank'),
                        'hasStats': player_data.get('hasStats'),
                        'nationalId': player_data.get('nationalId'),
                    }

                       # إضافة الإحصائيات بشكل آمن
                    if player_data.get('stats'):
                        for stat in player_data['stats']:
                            stat_key = stat.get('name') or f"type_{stat.get('type')}"
                            player_entry[f"stat_{stat_key}"] = stat.get('value')
                    
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
    # بعد معالجة جميع المباريات
    print("\nجميع مفاتيح الإحصائيات التي تم مواجهتها عبر جميع الفرق:")
    print(sorted(all_stat_keys_global))
    
    return df_matches, df_players, df_events, df_chart_events, df_top_performers, df_widgets, df_officials, df_stages

if __name__ == "__main__":
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
            else:
                print(f"تحذير: {df_names[i]} فارغ، لم يتم حفظه")
        
        print("\nتم الانتهاء من معالجة جميع البيانات بنجاح!")
        
    except FileNotFoundError:
        print(f"خطأ: الملف {PICKLE_PATH} غير موجود!")
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {e}")
        import traceback
        traceback.print_exc()
