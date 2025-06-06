import pandas as pd
import json
import os
import dataclasses
from typing import List, Dict, Any, Optional

# تعريف الـ dataclasses التي تمثل هيكل بياناتك
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
class LineupMember: # تمثل اللاعب داخل التشكيلة (lineups.members)
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
    name: Optional[str] = None # هذا الحقل مهم لربط الاسم باللاعب
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
class Lineup: # تمثل معلومات التشكيلة ككل (homeCompetitor.lineups)
    status: Optional[int] = None
    formation: Optional[str] = None
    hasFieldPositions: Optional[bool] = None
    members: Optional[List[LineupMember]] = dataclasses.field(default_factory=list) # قائمة اللاعبين

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
    # لا نضيف x و y هنا! يجب أن تكون في ChartEvent إذا كانت تمثل إحداثيات الحدث نفسه

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
    x: Optional[float] = None # إضافة x هنا
    y: Optional[float] = None # إضافة y هنا

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChartEvent":
        # Extract outcome data safely
        outcome_data = data.get('outcome')
        
        # Prepare outcome_for_dataclass to only contain 'id' and 'name'
        outcome_for_dataclass = None
        if outcome_data and isinstance(outcome_data, dict):
            # ننشئ قاموساً جديداً يحتوي فقط على المفاتيح المتوقعة لـ ChartEventOutcome
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
            # نمرر outcome_for_dataclass الذي تم تنقيته
            outcome=ChartEventOutcome(**outcome_for_dataclass) if outcome_for_dataclass else None,
            competitorNum=data.get('competitorNum'),
            x=data.get('x'), # استخراج x مباشرة من بيانات الحدث الأصلية
            y=data.get('y')  # استخراج y مباشرة من بيانات الحدث الأصلية
        )

@dataclasses.dataclass
class GameMembers: # تمثل game.members
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
        # استخراج البيانات بأمان مع قيم افتراضية
        line_types_ids = data.get('lineTypesIds', [])
        id_val = data.get('id')
        sport_id = data.get('sportId')
        competition_id = data.get('competitionId')
        status_id = data.get('statusId')
        season_num = data.get('seasonNum')
        stage_num = data.get('stageNum')
        group_num = data.get('groupNum')
        round_num = data.get('roundNum')
        round_name = data.get('roundName')
        stage_name = data.get('stageName')
        group_name = data.get('groupName')
        competition_display_name = data.get('competitionDisplayName')
        start_time = data.get('startTime')
        status_group = data.get('statusGroup')
        status_text = data.get('statusText')
        short_status_text = data.get('shortStatusText')
        game_time_and_status = data.get('gameTimeAndStatus')
        
        # معالجة المتغيرات المتداخلة
        home_comp_data = data.get('homeCompetitor')
        away_comp_data = data.get('awayCompetitor')
        members_data = data.get('members')
        events_data = data.get('events', [])
        chart_events_data = data.get('chartEvents', {})
        top_performers_data = data.get('topPerformers')
        widgets_data = data.get('widgets', [])
        statistics_data = data.get('statistics')
        officials_data = data.get('officials', [])
        stages_data = data.get('stages', [])

        # معالجة الأحداث البيانية
        processed_chart_events = {}
        if isinstance(chart_events_data, dict):
            for key, events_list_data in chart_events_data.items():
                if isinstance(events_list_data, list):
                    processed_chart_events[key] = [
                        ChartEvent.from_dict(ce) 
                        for ce in events_list_data 
                        if isinstance(ce, dict)
                    ]

        # معالجة المنافسين
        home_competitor = None
        if isinstance(home_comp_data, dict):
            try:
                home_competitor = Competitor.from_dict(home_comp_data)
            except Exception as e:
                print(f"خطأ في معالجة homeCompetitor: {e}")
                home_competitor = None

        away_competitor = None
        if isinstance(away_comp_data, dict):
            try:
                away_competitor = Competitor.from_dict(away_comp_data)
            except Exception as e:
                print(f"خطأ في معالجة awayCompetitor: {e}")
                away_competitor = None

        # معالجة الأعضاء
        members_obj = None
        if isinstance(members_data, dict):
            try:
                members_obj = GameMembers.from_dict(members_data)
            except Exception as e:
                print(f"خطأ في معالجة members: {e}")
                members_obj = None

        # معالجة أفضل الأداء
        top_performers = None
        if isinstance(top_performers_data, dict):
            try:
                top_performers = TopPerformers.from_dict(top_performers_data)
            except Exception as e:
                print(f"خطأ في معالجة topPerformers: {e}")
                top_performers = None

        # معالجة الإحصائيات
        statistics = None
        if isinstance(statistics_data, dict):
            try:
                statistics = GameStatistics.from_dict(statistics_data)
            except Exception as e:
                print(f"خطأ في معالجة statistics: {e}")
                statistics = None

        # إنشاء نسخة من الكلاس
        return cls(
            lineTypesIds=line_types_ids,
            id=id_val,
            sportId=sport_id,
            competitionId=competition_id,
            statusId=status_id,
            seasonNum=season_num,
            stageNum=stage_num,
            groupNum=group_num,
            roundNum=round_num,
            roundName=round_name,
            stageName=stage_name,
            groupName=group_name,
            competitionDisplayName=competition_display_name,
            startTime=start_time,
            statusGroup=status_group,
            statusText=status_text,
            shortStatusText=short_status_text,
            gameTimeAndStatus=game_time_and_status,
            homeCompetitor=home_competitor,
            awayCompetitor=away_competitor,
            members=members_obj,
            events=[GameEvent.from_dict(e) for e in events_data if isinstance(e, dict)],
            chartEvents=processed_chart_events,
            topPerformers=top_performers,
            widgets=[Widget.from_dict(w) for w in widgets_data if isinstance(w, dict)],
            statistics=statistics,
            officials=[Official.from_dict(o) for o in officials_data if isinstance(o, dict)],
            stages=[GameStage.from_dict(s) for s in stages_data if isinstance(s, dict)]
        )


# -- دالة بناء قاموس شامل للأسماء من كل مصدر في المباراة --
def build_player_name_map(game: dict):
    player_id_to_name = {}

    # 1. من lineups (home/away)
    for comp_key in ['homeCompetitor', 'awayCompetitor']:
        comp = game.get(comp_key, {})
        members = comp.get('lineups', {}).get('members', [])
        for m in members:
            for key in ['id', 'athleteId', 'playerId']:
                pid = m.get(key)
                if pid and m.get('name'):
                    player_id_to_name[pid] = m['name']

    # 2. من members (لو dict أو list)
    members_obj = game.get('members')
    if isinstance(members_obj, dict):
        for side in ['homeTeamMembers', 'awayTeamMembers']:
            for m in members_obj.get(side, []):
                for key in ['id', 'athleteId', 'playerId']:
                    pid = m.get(key)
                    if pid and m.get('name'):
                        player_id_to_name[pid] = m['name']
    elif isinstance(members_obj, list):
        for m in members_obj:
            for key in ['id', 'athleteId', 'playerId']:
                pid = m.get(key)
                if pid and m.get('name'):
                    player_id_to_name[pid] = m['name']

    # 3. من topPerformers
    top_p = game.get('topPerformers', {}).get('categories', [])
    for cat in top_p:
        for k in ['homePlayer', 'awayPlayer']:
            p = cat.get(k)
            if p and p.get('name'):
                for key in ['id', 'athleteId', 'playerId']:
                    pid = p.get(key)
                    if pid:
                        player_id_to_name[pid] = p['name']

    # 4. من events/chartEvents لو فيها playerName
    for e in game.get('events', []):
        for key in ['playerId', 'athleteId']:
            pid = e.get(key)
            if pid and e.get('playerName'):
                player_id_to_name[pid] = e['playerName']
    for ce_list in game.get('chartEvents', {}).values():
        for ce in ce_list:
            for key in ['playerId', 'athleteId']:
                pid = ce.get(key)
                if pid and ce.get('playerName'):
                    player_id_to_name[pid] = ce['playerName']

    return player_id_to_name

# -- دالة ربط الاسم --
def resolve_player_name(pid, player_id_to_name):
    if pid is None:
        return "Unknown"
    return player_id_to_name.get(pid, "Unknown")

# -- الكود الرئيسي لاستخراج الجداول بباينية صحيحة وقوية --
def extract_data_to_dataframes(df_games: pd.DataFrame):
    all_matches_data, all_players_data, all_events_data = [], [], []
    all_chart_events_data, all_top_performers_data, all_widgets_data = [], [], []
    all_officials_data, all_stages_data = [], []
    stats_rows = []

    def resolve_player_name(pid, player_id_to_name):
        if pid is None:
            return "Unknown"
        return player_id_to_name.get(pid, "Unknown")

    def build_player_name_map(game: dict):
        player_id_to_name = {}
        # 1. lineups (home/away)
        for comp_key in ['homeCompetitor', 'awayCompetitor']:
            comp = game.get(comp_key, {})
            members = comp.get('lineups', {}).get('members', [])
            for m in members:
                for key in ['id', 'athleteId', 'playerId']:
                    pid = m.get(key)
                    if pid and m.get('name'):
                        player_id_to_name[pid] = m['name']
        # 2. members (لو dict أو list)
        members_obj = game.get('members')
        if isinstance(members_obj, dict):
            for side in ['homeTeamMembers', 'awayTeamMembers']:
                for m in members_obj.get(side, []):
                    for key in ['id', 'athleteId', 'playerId']:
                        pid = m.get(key)
                        if pid and m.get('name'):
                            player_id_to_name[pid] = m['name']
        elif isinstance(members_obj, list):
            for m in members_obj:
                for key in ['id', 'athleteId', 'playerId']:
                    pid = m.get(key)
                    if pid and m.get('name'):
                        player_id_to_name[pid] = m['name']
        # 3. topPerformers
        top_p = game.get('topPerformers', {}).get('categories', [])
        for cat in top_p:
            for k in ['homePlayer', 'awayPlayer']:
                p = cat.get(k)
                if p and p.get('name'):
                    for key in ['id', 'athleteId', 'playerId']:
                        pid = p.get(key)
                        if pid:
                            player_id_to_name[pid] = p['name']
        # 4. events/chartEvents لو فيها playerName
        for e in game.get('events', []):
            for key in ['playerId', 'athleteId']:
                pid = e.get(key)
                if pid and e.get('playerName'):
                    player_id_to_name[pid] = e['playerName']
        for ce_list in game.get('chartEvents', {}).values():
            for ce in ce_list:
                for key in ['playerId', 'athleteId']:
                    pid = ce.get(key)
                    if pid and ce.get('playerName'):
                        player_id_to_name[pid] = ce['playerName']
        return player_id_to_name

    def extract_minute(time_str):
        import re
        if isinstance(time_str, str):
            m = re.match(r"(\d+)", time_str)
            if m:
                return int(m.group(1))
        return "Unknown"

    if 'game' not in df_games.columns or df_games['game'].empty:
        print("لا يوجد عمود 'game' أو أنه فارغ في DataFrame المدخل.")
        
        return tuple(pd.DataFrame() for _ in range(9))

    for index, row in df_games.iterrows():
        game = row['game']
        match_id = game.get('id', f'unknown_{index}')

        player_id_to_name = build_player_name_map(game)

        # -- تجهيز أسماء الفرق --
        home_team = game.get('homeCompetitor', {})
        away_team = game.get('awayCompetitor', {})
        home_team_name = home_team.get('name')
        away_team_name = away_team.get('name')
        home_team_id = home_team.get('id')
        away_team_id = away_team.get('id')
        team_id_to_name = {home_team_id: home_team_name, away_team_id: away_team_name}


        # === ضع كود الطباعات هنا 👇👇👇 ===
        
        # === نهاية كود الطباعات ===

        # --- df_matches ---
        for index, row in df_games.iterrows():

            game = row['game']  # خطأ! يجب أن يكون هذا السطر بمسافة بادئة
            match_id = game.get('id', f'unknown_{index}')

            home_team = game.get('homeCompetitor', {})
            away_team = game.get('awayCompetitor', {})
            home_team_name = home_team.get('name')
            away_team_name = away_team.get('name')

            match_row = {
                'matchId': match_id,
                'competitionName': game.get('competitionDisplayName'),
                'startTime': game.get('startTime'),
                'statusText': game.get('statusText'),
                'shortStatusText': game.get('shortStatusText'),
                'gameTimeAndStatus': game.get('gameTimeAndStatus'),
                'homeTeamName': home_team_name,
                'homeTeamScore': home_team.get('score'),
                'awayTeamName': away_team_name,
                'awayTeamScore': away_team.get('score'),
            }

            for prefix, team in [('home', home_team), ('away', away_team)]:
                team_name = team.get('name')
                members = team.get('lineups', {}).get('members', [])
                stats_agg = {}
                for player in members:
                    for stat in player.get('stats', []):
                        stat_name = stat.get('name')
                        stat_value = stat.get('value')
                        if stat_name is not None:
                            try:
                                val = float(stat_value)
                            except (ValueError, TypeError):
                                val = stat_value
                            if isinstance(val, (int, float)):
                                stats_agg[stat_name] = stats_agg.get(stat_name, 0) + val
                            else:
                                if stat_name not in stats_agg:
                                    stats_agg[stat_name] = val
                # أضف كل إحصائية كعمود في match_row
                for stat_name, stat_value in stats_agg.items():
                    match_row[f"{stat_name}_{prefix}"] = stat_value

            all_matches_data.append(match_row)
        
        ##########################################################################

        # --- df_players ---
        for team_obj, is_home in [(home_team, True), (away_team, False)]:
            lu = team_obj.get('lineups', {})
            for p in lu.get('members', []):
                formation_name = p.get('formation', {}).get('name') if isinstance(p.get('formation'), dict) else None
                position_name = p.get('position', {}).get('name') if isinstance(p.get('position'), dict) else None
                entry = {
                    'matchId': match_id,
                    'playerId': p.get('id'),
                    'playerName': resolve_player_name(p.get('id'), player_id_to_name),
                    'teamName': team_obj.get('name'),
                    'isHomeTeam': is_home,
                    'positionName': position_name,
                    'isStarter': p.get('statusText') == 'Starter',
                    'formation_name': formation_name,
                    'ranking': p.get('ranking'),
                    'popularityRank': p.get('popularityRank'),
                    'hasStats': p.get('hasStats'),
                    'nationalId': p.get('nationalId'),
                }
                if p.get('stats'):
                    for stat in p['stats']:
                        stat_key = stat.get('name') or f"type_{stat.get('type')}"
                        entry[f"stat_{stat_key}"] = stat.get('value')
                all_players_data.append(entry)

        # --- df_events ---
        for e in game.get('events', []):
            event_copy = {
                'matchId': match_id,
                'order': e.get('order'),
                'gameTimeDisplay': e.get('gameTimeDisplay'),
                'gameTime': e.get('gameTime'),
                'addedTime': e.get('addedTime'),
                'isMajor': e.get('isMajor'),
                'playerId': e.get('playerId'),
                'competitorId': e.get('competitorId'),
                'statusId': e.get('statusId'),
                'stageId': e.get('stageId'),
                'num': e.get('num'),
                'gameTimeAndStatusDisplayType': e.get('gameTimeAndStatusDisplayType'),
                'extraPlayers': e.get('extraPlayers', []),
                'teamName': team_id_to_name.get(e.get('competitorId'), 'Unknown'),
                'playerName': resolve_player_name(e.get('playerId'), player_id_to_name),
            }
            if 'eventType' in e and isinstance(e['eventType'], dict):
                event_copy['eventType'] = e['eventType']
            all_events_data.append(event_copy)

        # --- df_chart_events ---
        chart_events = game.get('chartEvents', {})
        events_list = chart_events.get('events', [])
        for ce in events_list:
            chart_event_copy = {
                'matchId': match_id,
                'key': ce.get('key'),
                'time': ce.get('time'),
                'minute': ce.get('minute'),  # أو extract_minute(ce.get('time'))
                'type': ce.get('type'),
                'subType': ce.get('subType'),
                'playerId': ce.get('playerId'),
                'xg': ce.get('xg'),
                'xgot': ce.get('xgot'),
                'bodyPart': ce.get('bodyPart'),
                'goalDescription': ce.get('goalDescription', 'Unknown'),
                'competitorNum': ce.get('competitorNum'),
                'x': ce.get('line', 'Unknown'),
                'y': ce.get('side', 'Unknown'),
                'playerName': resolve_player_name(ce.get('playerId'), player_id_to_name),
                'involvedTeam': home_team_name if ce.get('competitorNum') == 1 else away_team_name if ce.get('competitorNum') == 2 else 'Unknown',
            }
            if 'outcome' in ce and isinstance(ce['outcome'], dict):
                chart_event_copy['outcome'] = ce['outcome']
            all_chart_events_data.append(chart_event_copy)

        # --- df_top_performers ---
        top_p = game.get('topPerformers', {}).get('categories', [])
        for cat in top_p:
            for side, is_home in [('homePlayer', True), ('awayPlayer', False)]:
                p = cat.get(side)
                if p:
                    entry = {
                        'matchId': match_id,
                        'categoryName': cat.get('name'),
                        'playerId': p.get('id'),
                        'athleteId': p.get('athleteId'),
                        'playerName': resolve_player_name(p.get('id'), player_id_to_name) if p.get('id') is not None else resolve_player_name(p.get('athleteId'), player_id_to_name),
                        'teamName': home_team_name if is_home else away_team_name,
                        'isHomeTeam': is_home,
                        'positionName': p.get('positionName'),
                        'positionShortName': p.get('positionShortName'),
                        'imageVersion': p.get('imageVersion'),
                        'nameForURL': p.get('nameForURL')
                    }
                    if p.get('stats'):
                        for stat in p['stats']:
                            stat_key = stat.get('name') or f"type_{stat.get('type')}"
                            entry[f"stat_{stat_key}"] = stat.get('value')
                    all_top_performers_data.append(entry)

        # --- df_widgets ---
        for w in game.get('widgets', []):
            wc = w.copy()
            wc['matchId'] = match_id
            all_widgets_data.append(wc)

        # --- df_officials ---
        for o in game.get('officials', []):
            oc = o.copy()
            oc['matchId'] = match_id
            all_officials_data.append(oc)

        # --- df_stages ---
        for s in game.get('stages', []):
            sc = s.copy()
            sc['matchId'] = match_id
            all_stages_data.append(sc)

        # --- df_stats ---
        for stat_type, team_stats in stats.items():
            if isinstance(team_stats, dict):
                for side, value in team_stats.items():
                    stats_rows.append({
                        'matchId': match_id,
                        'stat_name': stat_type,
                        'team': 'homeTeam' if side == 'home' else 'awayTeam',
                        'value': value
                    })

    df_matches = pd.DataFrame(all_matches_data)
    df_players = pd.DataFrame(all_players_data)
    df_events = pd.DataFrame(all_events_data)
    df_chart_events = pd.DataFrame(all_chart_events_data)
    df_top_performers = pd.DataFrame(all_top_performers_data)
    df_widgets = pd.DataFrame(all_widgets_data)
    df_officials = pd.DataFrame(all_officials_data)
    df_stages = pd.DataFrame(all_stages_data)
    df_stats = pd.DataFrame(stats_rows)

    # ====== التعديل الجديد: بناء ملفات لاعبين مختصر وlong format ======
    core_stats = [
        'Minutes', 'Goals', 'Assists', 'Total Shots', 'Shots On Target', 'Shots Off Target',
        'Key Passes', 'Expected Goals', 'Touches', 'Passes Completed'
    ]
    id_cols = [
        'matchId', 'playerId', 'playerName', 'teamName', 'isHomeTeam', 'positionName', 'isStarter'
    ]
    stat_cols = [f"stat_{stat}" for stat in core_stats if f"stat_{stat}" in df_players.columns]
    columns_needed = id_cols + stat_cols

    df_players_short = df_players[columns_needed].copy()
    df_players_long = df_players_short.melt(
        id_vars=id_cols,
        value_vars=stat_cols,
        var_name='stat_name',
        value_name='stat_value'
    ).dropna(subset=['stat_value'])

    print("\nاكتمل استخلاص البيانات إلى DataFrames.")
    # أرجع كل شيء بما فيها الملفات الجديدة
    return (df_matches, df_players, df_events, df_chart_events, df_top_performers,
            df_widgets, df_officials, df_stages, df_stats, df_players_short, df_players_long)


if __name__ == "__main__":
    pickle_file_path = r'C:\Users\E.abed\Desktop\FootballData\all_games_data.pkl'
    output_directory = r'C:\Users\E.abed\Desktop\FootballData\filtered_games'
    os.makedirs(output_directory, exist_ok=True)

    print(f"جاري تحميل ملف الـ pickle من: {pickle_file_path}")
    df_all_games = pd.read_pickle(pickle_file_path)
    print(f"تم تحميل الـ DataFrame بنجاح. يحتوي على {len(df_all_games)} صفوف.")

    # استقبل جميع الجداول بما فيها المختصر والطويل
    (df_matches, df_players, df_events, df_chart_events, df_top_performers,
     df_widgets, df_officials, df_stages, df_stats, df_players_short, df_players_long) = extract_data_to_dataframes(df_all_games)

    print("تم استخراج الجداول بنجاح.")

    # حفظ كل DataFrame كـ JSON
    dfs_to_save = [
        ("df_matches", df_matches),
        ("df_players", df_players),
        ("df_events", df_events),
        ("df_chart_events", df_chart_events),
        ("df_top_performers", df_top_performers),
        ("df_widgets", df_widgets),
        ("df_officials", df_officials),
        ("df_stages", df_stages),
        ("df_stats", df_stats),
        ("players_short", df_players_short),
        ("players_long", df_players_long),
    ]
    for name, df in dfs_to_save:
        df.to_json(os.path.join(output_directory, f"{name}.json"), orient="records", force_ascii=False, indent=2)
    print(f"تم حفظ جميع الجداول بنجاح في: {output_directory}")
