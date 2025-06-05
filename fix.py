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
# --- الكود الرئيسي لتنقية البيانات وإنشاء DataFrames ---
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

    # تهيئة القواميس لربط الـ IDs بالأسماء
    player_id_to_name = {}
    player_id_to_team_name = {}
    team_id_to_name = {}

    home_team_name = None
    away_team_name = None
    home_team_id = None
    away_team_id = None

    # --- البدء بملء player_id_to_name و team_id_to_name من Competitors و Lineups (أكثر موثوقية) ---
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
    
    # --- ملء player_id_to_name من game.members (كمصدر ثانوي أو تأكيد) ---
    # هذا الجزء يمكن أن يكمل الأسماء إذا لم تكن موجودة في lineups
    if 'members' in game_data_dict and isinstance(game_data_dict['members'], dict):
        if 'homeTeamMembers' in game_data_dict['members'] and isinstance(game_data_dict['members']['homeTeamMembers'], list):
            for player in game_data_dict['members']['homeTeamMembers']:
                p_id = player.get('id')
                p_name = player.get('name')
                if p_id and p_name and p_id not in player_id_to_name: # أضف فقط إذا لم يكن موجودًا بالفعل
                    player_id_to_name[p_id] = p_name
                    if home_team_name and p_id not in player_id_to_team_name:
                        player_id_to_team_name[p_id] = home_team_name

        if 'awayTeamMembers' in game_data_dict['members'] and isinstance(game_data_dict['members']['awayTeamMembers'], list):
            for player in game_data_dict['members']['awayTeamMembers']:
                p_id = player.get('id')
                p_name = player.get('name')
                if p_id and p_name and p_id not in player_id_to_name: # أضف فقط إذا لم يكن موجودًا بالفعل
                    player_id_to_name[p_id] = p_name
                    if away_team_name and p_id not in player_id_to_team_name:
                        player_id_to_team_name[p_id] = away_team_name
    else:
        # هذا التحذير لا يزال مهماً لأنه قد يشير إلى نقص في البيانات الأصلية
        print(f"    - تحذير: المفتاح 'members' (على مستوى game) غير موجود أو ليس قاموساً للمباراة {match_id}. (قد يؤثر على ربط أسماء اللاعبين)")


    # إعادة بناء معلومات الفرق باستخدام dataclasses الجديدة
    # الآن سيتم استخدام player_id_to_name الذي تم إنشاؤه مسبقًا
    home_competitor_obj = Competitor.from_dict(game_data_dict['homeCompetitor']) if 'homeCompetitor' in game_data_dict and isinstance(game_data_dict['homeCompetitor'], dict) else None
    away_competitor_obj = Competitor.from_dict(game_data_dict['awayCompetitor']) if 'awayCompetitor' in game_data_dict and isinstance(game_data_dict['awayCompetitor'], dict) else None

    if home_competitor_obj:
        home_team_info = dataclasses.asdict(home_competitor_obj)
        # تحديث أسماء اللاعبين في التشكيلة بناءً على player_id_to_name (هذا الجزء كان صحيحًا)
        if home_team_info.get('lineups') and home_team_info['lineups'].get('members'):
            for player in home_team_info['lineups']['members']:
                if 'id' in player and player['id'] in player_id_to_name:
                    player['name'] = player_id_to_name[player['id']]
        filtered_match_data['homeTeam'] = home_team_info
    else:
        print(f"    - تحذير: المفتاح 'homeCompetitor' غير موجود أو ليس قاموساً للمباراة {match_id}. (سيتم تخطيه)")

    if away_competitor_obj:
        away_team_info = dataclasses.asdict(away_competitor_obj)
        # تحديث أسماء اللاعبين في التشكيلة بناءً على player_id_to_name (هذا الجزء كان صحيحًا)
        if away_team_info.get('lineups') and away_team_info['lineups'].get('members'):
            for player in away_team_info['lineups']['members']:
                if 'id' in player and player['id'] in player_id_to_name:
                    player['name'] = player_id_to_name[player['id']]
        filtered_match_data['awayTeam'] = away_team_info
    else:
        print(f"    - تحذير: المفتاح 'awayCompetitor' غير موجود أو ليس قاموساً للمباراة {match_id}. (سيتم تخطيه)")


    # 3. معالجة الأحداث الرئيسية (events) بالتفصيل
    # الآن بعد أن أصبح player_id_to_name أكثر اكتمالًا
    if 'events' in game_data_dict and isinstance(game_data_dict['events'], list):
        filtered_events = []
        for event_data in game_data_dict['events']:
            try:
                event_obj = GameEvent.from_dict(event_data)
                event_info = dataclasses.asdict(event_obj)

                # ربط أسماء اللاعبين والفرق بالأحداث
                if event_info.get('playerId') in player_id_to_name:
                    event_info['playerName'] = player_id_to_name[event_info['playerId']]
                # ربط اسم الفريق بالـ competitorId
                if event_info.get('competitorId') in team_id_to_name:
                    event_info['teamName'] = team_id_to_name[event_info['competitorId']]

                filtered_events.append(event_info)
            except Exception as e:
                print(f"    - خطأ في معالجة حدث واحد داخل 'events' للمباراة {match_id}: {e} - بيانات الحدث: {event_data.get('id', 'N/A')}")


        if filtered_events:
            filtered_match_data['events'] = filtered_events
    else:
        print(f"    - تحذير: المفتاح 'events' غير موجود أو ليس قائمة للمباراة {match_id}. (سيتم تخطيه)")

    # 4. معالجة chartEvents بالتفصيل وربط اللاعبين
    # الآن بعد أن أصبح player_id_to_name أكثر اكتمالًا
    if 'chartEvents' in game_data_dict and isinstance(game_data_dict['chartEvents'], dict):
        extracted_chart_events = {}
        for key, events_list in game_data_dict['chartEvents'].items():
            if isinstance(events_list, list):
                processed_events = []
                for event_data in events_list:
                    try:
                        # هنا تم التعديل
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
                        print(f"    - خطأ في معالجة حدث واحد داخل 'chartEvents' للمباراة {match_id} (key: {key}): {e} - بيانات الحدث: {event_data.get('key', 'N/A')}")
                extracted_chart_events[key] = processed_events

        if extracted_chart_events:
            filtered_match_data['chartEvents'] = extracted_chart_events
        else:
            print(f"    - تحذير: المفتاح 'chartEvents.events' موجود لكنه فارغ أو غير صالح للمباراة {match_id}.")
    else:
        print(f"    - تحذير: المفتاح 'chartEvents' غير موجود أو ليس قاموساً للمباراة {match_id}. (سيتم تخطيه)")


    # 5. معالجة game.topPerformers بالتفصيل
    # الآن بعد أن أصبح player_id_to_name أكثر اكتمالًا
    if 'topPerformers' in game_data_dict and isinstance(game_data_dict['topPerformers'], dict):
        top_performers_obj = TopPerformers.from_dict(game_data_dict['topPerformers'])
        filtered_top_performers_categories = []
        if top_performers_obj.categories:
            for category_obj in top_performers_obj.categories:
                category_info = dataclasses.asdict(category_obj)
                # تحديث أسماء اللاعبين
                if category_info.get('homePlayer'):
                    # تحقق من playerId و athleteId
                    player_id = category_info['homePlayer'].get('id')
                    athlete_id = category_info['homePlayer'].get('athleteId')
                    
                    if player_id in player_id_to_name:
                        category_info['homePlayer']['name'] = player_id_to_name[player_id]
                    elif athlete_id in player_id_to_name: # بعض الأحيان يكون الـ ID هو athleteId
                         category_info['homePlayer']['name'] = player_id_to_name[athlete_id]


                if category_info.get('awayPlayer'):
                    # تحقق من playerId و athleteId
                    player_id = category_info['awayPlayer'].get('id')
                    athlete_id = category_info['awayPlayer'].get('athleteId')

                    if player_id in player_id_to_name:
                        category_info['awayPlayer']['name'] = player_id_to_name[player_id]
                    elif athlete_id in player_id_to_name:
                         category_info['awayPlayer']['name'] = player_id_to_name[athlete_id]

                filtered_top_performers_categories.append(category_info)

        if filtered_top_performers_categories:
            filtered_match_data['topPerformers'] = filtered_top_performers_categories
        else:
            print(f"    - تحذير: المفتاح 'topPerformers.categories' موجود لكنه فارغ أو غير صالح للمباراة {match_id}.")
    else:
        print(f"    - تحذير: المفتاح 'topPerformers' غير موجود أو ليس قاموساً للمباراة {match_id}. (سيتم تخطيه)")

    # 6. معالجة game.widgets بالتفصيل
    if 'widgets' in game_data_dict and isinstance(game_data_dict['widgets'], list):
        filtered_widgets = []
        for widget_data in game_data_dict['widgets']:
            widget_obj = Widget.from_dict(widget_data)
            filtered_widgets.append(dataclasses.asdict(widget_obj))
        if filtered_widgets:
            filtered_match_data['widgets'] = filtered_widgets
    else:
        print(f"    - تحذير: المفتاح 'widgets' غير موجود أو ليس قائمة للمباراة {match_id}. (سيتم تخطيه)")

    # 7. الإحصائيات الرئيسية (statistics)
    if 'statistics' in game_data_dict and isinstance(game_data_dict['statistics'], dict):
        stats_obj = GameStatistics.from_dict(game_data_dict['statistics'])
        filtered_match_data['statistics'] = dataclasses.asdict(stats_obj)
    else:
        print(f"    - تحذير: المفتاح 'statistics' (على مستوى المباراة) غير موجود للمباراة {match_id}. (سيتم تخطيه)")

    # 8. المسؤولون عن المباراة (officials)
    if 'officials' in game_data_dict and isinstance(game_data_dict['officials'], list):
        filtered_officials = []
        for official_data in game_data_dict['officials']:
            official_obj = Official.from_dict(official_data)
            if official_obj.role == 'Referee':
                filtered_officials.append(dataclasses.asdict(official_obj))
        if filtered_officials:
            filtered_match_data['officials'] = filtered_officials
    else:
        print(f"    - تحذير: المفتاح 'officials' غير موجود أو ليس قائمة للمباراة {match_id}. (سيتم تخطيه)")

    # 9. معالجة game.stages
    if 'stages' in game_data_dict and isinstance(game_data_dict['stages'], list):
        filtered_stages = []
        for stage_data in game_data_dict['stages']:
            stage_obj = GameStage.from_dict(stage_data)
            filtered_stages.append(dataclasses.asdict(stage_obj))
        if filtered_stages:
            filtered_match_data['stages'] = filtered_stages
    else:
        print(f"    - تحذير: المفتاح 'stages' غير موجود أو ليس قائمة للمباراة {match_id}. (سيتم تخطيه)")

    

    
    return filtered_match_data


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
            
            # --- تعبئة df_matches ---
            all_matches_data.append({
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
                'statistics_corners_home': filtered_data.get('statistics', {}).get('corners', {}).get('home'),
                'statistics_corners_away': filtered_data.get('statistics', {}).get('corners', {}).get('away'),
                'statistics_shotsOnTarget_home': filtered_data.get('statistics', {}).get('shotsOnTarget', {}).get('home'),
                'statistics_shotsOnTarget_away': filtered_data.get('statistics', {}).get('shotsOnTarget', {}).get('away'),
                'statistics_possession_home': filtered_data.get('statistics', {}).get('possession', {}).get('home'),
                'statistics_possession_away': filtered_data.get('statistics', {}).get('possession', {}).get('away'),
            })

            # --- استخلاص بيانات اللاعبين (df_players) ---
            home_comp_obj = filtered_data.get('homeTeam')
            if home_comp_obj and home_comp_obj.get('lineups') and home_comp_obj['lineups'].get('members'):
                for player_data in home_comp_obj['lineups']['members']:
                    formation_name = None
                    if player_data.get('formation'):
                        if isinstance(player_data['formation'], dict):
                            formation_name = player_data['formation'].get('name')
                    
                    # معالجة مشكلة positionName
                    position_name = None
                    if player_data.get('position'):
                        if isinstance(player_data['position'], dict):
                            position_name = player_data['position'].get('name')
                    player_entry = {
                        'matchId': match_id,
                        'playerId': player_data.get('id'),
                        'playerName': player_data.get('name'),
                        'teamName': home_comp_obj.get('name'),
                        'isHomeTeam': True,
                        'positionName': position_name,
                        'isStarter': player_data.get('statusText') == 'Starter',
                        'formation_name': formation_name,
                        'ranking': player_data.get('ranking'),
                        'popularityRank': player_data.get('popularityRank'),
                        'hasStats': player_data.get('hasStats'),
                        'nationalId': player_data.get('nationalId'),
                    }

                    # إضافة الإحصائيات
                    if player_data.get('stats'):
                        for stat in player_data['stats']:
                            stat_key = stat.get('name') or f"type_{stat.get('type')}"
                            player_entry[f"stat_{stat_key}"] = stat.get('value')
                    
                    all_players_data.append(player_entry)
                    
            # نفس المعالجة للفريق الضيف
            away_comp_obj = filtered_data.get('awayTeam')
            if away_comp_obj and away_comp_obj.get('lineups') and away_comp_obj['lineups'].get('members'):
                for player_data in away_comp_obj['lineups']['members']:
                    # معالجة مشكلة formation_name
                    formation_name = None
                    if player_data.get('formation'):
                        if isinstance(player_data['formation'], dict):
                            formation_name = player_data['formation'].get('name')
                    
                    # معالجة مشكلة positionName
                    position_name = None
                    if player_data.get('position'):
                        if isinstance(player_data['position'], dict):
                            position_name = player_data['position'].get('name')
                    
                    player_entry = {
                        'matchId': match_id,
                        'playerId': player_data.get('id'),
                        'playerName': player_data.get('name'),
                        'teamName': away_comp_obj.get('name'),
                        'isHomeTeam': False,
                        'positionName': position_name,
                        'isStarter': player_data.get('statusText') == 'Starter',
                        'formation_name': formation_name,
                        'ranking': player_data.get('ranking'),
                        'popularityRank': player_data.get('popularityRank'),
                        'hasStats': player_data.get('hasStats'),
                        'nationalId': player_data.get('nationalId'),
                    }
                    
                    if player_data.get('stats'):
                        for stat in player_data['stats']:
                            stat_key = stat.get('name') or f"type_{stat.get('type')}"
                            player_entry[f"stat_{stat_key}"] = stat.get('value')
                    
                    all_players_data.append(player_entry)


            if 'events' in filtered_data:
                for event in filtered_data['events']:
                    # نسخ آمن للحدث
                    event_copy = {
                        'matchId': match_id,
                        'order': event.get('order'),
                        'gameTimeDisplay': event.get('gameTimeDisplay'),
                        'gameTime': event.get('gameTime'),
                        'addedTime': event.get('addedTime'),
                        'isMajor': event.get('isMajor'),
                        'playerId': event.get('playerId'),
                        'competitorId': event.get('competitorId'),
                        'statusId': event.get('statusId'),
                        'stageId': event.get('stageId'),
                        'num': event.get('num'),
                        'gameTimeAndStatusDisplayType': event.get('gameTimeAndStatusDisplayType'),
                        'extraPlayers': event.get('extraPlayers', []),
                        'teamName': event.get('teamName'),
                        'playerName': event.get('playerName', 'Unknown'),
                    }
                    
                    # نسخ eventType بشكل آمن
                    if 'eventType' in event and isinstance(event['eventType'], dict):
                        event_copy['eventType'] = event['eventType']
                    
                    all_events_data.append(event_copy)


            # --- استخلاص أحداث الرسم البياني (df_chart_events) ---
            if 'chartEvents' in filtered_data:
                for event_type, events_list in filtered_data['chartEvents'].items():
                    for event in events_list:
                        # نسخ آمن للحدث
                        chart_event_copy = {
                            'matchId': match_id,
                            'chartEventTypeCategory': event_type,
                            'key': event.get('key'),
                            'time': event.get('time'),
                            'minute': event.get('minute'),
                            'type': event.get('type'),
                            'subType': event.get('subType'),
                            'playerId': event.get('playerId'),
                            'xg': event.get('xg'),
                            'xgot': event.get('xgot'),
                            'bodyPart': event.get('bodyPart'),
                            'goalDescription': event.get('goalDescription'),
                            'competitorNum': event.get('competitorNum'),
                            'x': event.get('x'),
                            'y': event.get('y'),
                            'playerName': event.get('playerName', 'Unknown'),
                            'involvedTeam': event.get('involvedTeam'),
                        }
                        
                        # نسخ outcome بشكل آمن
                        if 'outcome' in event and isinstance(event['outcome'], dict):
                            chart_event_copy['outcome'] = event['outcome']
                        
                        all_chart_events_data.append(chart_event_copy)

            # --- استخلاص أفضل اللاعبين أداءً (df_top_performers) ---
            if 'topPerformers' in filtered_data:
                for category in filtered_data['topPerformers']:
                    if category.get('homePlayer'):
                        top_perf_entry_home = {
                            'matchId': match_id,
                            'categoryName': category.get('name'),
                            'playerId': category['homePlayer'].get('id'),
                            'athleteId': category['homePlayer'].get('athleteId'),
                            'playerName': category['homePlayer'].get('name'),
                            'teamName': home_comp_obj.get('name') if home_comp_obj else None,
                            'isHomeTeam': True,
                            'positionName': category['homePlayer'].get('positionName'),
                            'positionShortName': category['homePlayer'].get('positionShortName'),
                            'imageVersion': category['homePlayer'].get('imageVersion'),
                            'nameForURL': category['homePlayer'].get('nameForURL')
                        }
                        if category['homePlayer'].get('stats'):
                            for stat in category['homePlayer']['stats']:
                                stat_key = stat.get('name') or f"type_{stat.get('type')}"
                                top_perf_entry_home[f"stat_{stat_key}"] = stat.get('value')
                        all_top_performers_data.append(top_perf_entry_home)

                    if category.get('awayPlayer'):
                        top_perf_entry_away = {
                            'matchId': match_id,
                            'categoryName': category.get('name'),
                            'playerId': category['awayPlayer'].get('id'),
                            'athleteId': category['awayPlayer'].get('athleteId'),
                            'playerName': category['awayPlayer'].get('name'),
                            'teamName': away_comp_obj.get('name') if away_comp_obj else None,
                            'isHomeTeam': False,
                            'positionName': category['awayPlayer'].get('positionName'),
                            'positionShortName': category['awayPlayer'].get('positionShortName'),
                            'imageVersion': category['awayPlayer'].get('imageVersion'),
                            'nameForURL': category['awayPlayer'].get('nameForURL')
                        }
                        if category['awayPlayer'].get('stats'):
                            for stat in category['awayPlayer']['stats']:
                                stat_key = stat.get('name') or f"type_{stat.get('type')}"
                                top_perf_entry_away[f"stat_{stat_key}"] = stat.get('value')
                        all_top_performers_data.append(top_perf_entry_away)

            # --- استخلاص الأدوات (df_widgets) ---
            if 'widgets' in filtered_data:
                for widget in filtered_data['widgets']:
                    widget_copy = widget.copy()
                    widget_copy['matchId'] = match_id
                    all_widgets_data.append(widget_copy)

            # --- استخلاص المسؤولين (df_officials) ---
            if 'officials' in filtered_data:
                for official in filtered_data['officials']:
                    official_copy = official.copy()
                    official_copy['matchId'] = match_id
                    all_officials_data.append(official_copy)

            # --- استخلاص المراحل (df_stages) ---
            if 'stages' in filtered_data:
                for stage in filtered_data['stages']:
                    stage_copy = stage.copy()
                    stage_copy['matchId'] = match_id
                    all_stages_data.append(stage_copy)
        

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
    print("\nاكتمل استخلاص البيانات إلى DataFrames.")


    return df_matches, df_players, df_events, df_chart_events, df_top_performers, df_widgets, df_officials, df_stages

# --- مثال على كيفية استخدام الكود ---
# يجب عليك تشغيل هذا الكود في بيئة Python الخاصة بك.

# مسار ملف الـ pickle الخاص بك
pickle_file_path = r'C:\Users\E.abed\Desktop\FootballData\all_games_data.pkl'

# مسار مجلد الإخراج لملفات JSON (اختياري، إذا كنت لا تريد حفظها JSON)
output_directory = r'C:\Users\E.abed\Desktop\FootballData\filtered_games'
os.makedirs(output_directory, exist_ok=True) # تأكد من وجود المجلد

try:
    print(f"جاري تحميل ملف الـ pickle من: {pickle_file_path}")
    df_all_games = pd.read_pickle(pickle_file_path)
    print(f"تم تحميل الـ DataFrame بنجاح. يحتوي على {len(df_all_games)} صفوف.")

    # استدعاء دالة الاستخراج لإنشاء DataFrames
    df_matches, df_players, df_events, df_chart_events, df_top_performers, df_widgets, df_officials, df_stages = extract_data_to_dataframes(df_all_games)

    print("\n--- نتائج DataFrames بعد المعالجة ---")
    print(f"عدد الصفوف في df_matches: {len(df_matches)}")
    print(f"عدد الصفوف في df_players: {len(df_players)}")
    print(f"عدد الصفوف في df_events: {len(df_events)}")
    print(f"عدد الصفوف في df_chart_events: {len(df_chart_events)}")
    print(f"عدد الصفوف في df_top_performers: {len(df_top_performers)}")
    print(f"عدد الصفوف في df_widgets: {len(df_widgets)}")
    print(f"عدد الصفوف في df_officials: {len(df_officials)}")
    print(f"عدد الصفوف في df_stages: {len(df_stages)}")

    # عرض أول 5 صفوف من كل DataFrame للتأكد
    print("\n--- أول 5 صفوف من df_players (اللاعبون) ---\n")
    print(df_players.head())
    print("\n--- أول 5 صفوف من df_events (الأحداث) ---\n")
    print(df_events.head())
    print("\n--- أول 5 صفوف من df_chart_events (أحداث الرسم البياني) ---\n")
    print(df_chart_events.head())
    print("\n--- أول 5 صفوف من df_top_performers (أفضل اللاعبين أداءً) ---\n")
    print(df_top_performers.head())
    print("\n--- أول 5 صفوف من df_officials (المسؤولون) ---\n")
    print(df_officials.head())


except FileNotFoundError:
    print(f"خطأ: الملف {pickle_file_path} غير موجود. يرجى التأكد من المسار الصحيح.")
except Exception as e:
    print(f"حدث خطأ أثناء معالجة ملف الـ pickle: {e}")
    import traceback
    traceback.print_exc()
