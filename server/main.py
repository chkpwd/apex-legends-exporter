"""Apex Legends Prometheus Exporter"""

import logging
import os
import sys
import time
import requests
from prometheus_client import (
    start_http_server,
    Gauge,
    REGISTRY,
    PROCESS_COLLECTOR,
    PLATFORM_COLLECTOR,
    GC_COLLECTOR,
    CollectorRegistry,
    Info,
)

class MapDataCollector:
    """Class to collect map data"""

    URL = "https://api.mozambiquehe.re/maprotation"

    def __init__(
        self, api_key: str, uid: str = None, player_name: str = None
    ):
        """
        Initialize the MapDataCollector instance.

        Args:
        api_key (str): The API key for authorization.
        uid (str, optional): The user ID. Defaults to None.
        player_name (str, optional): The player's name. Defaults to None.
        """
        self.uid = uid
        self.player_name = player_name
        self.headers = {"Authorization": api_key}

        # Data from current map rotation
        self.current_map_name = ""
        self.current_map_duration = 0
        self.current_map_remaining = 0

        # Data from next map rotation
        self.next_map_name = ""
        self.next_map_start = 0
        self.next_map_duration = 0

    def populate_data(self):
        """
        Collect map data from the API and populate the instance variables.
        """
        logging.debug("Collecting from: %s", self.URL)
        logging.debug("API KEY: %s", self.headers["Authorization"])

        map_rotation = requests.get(
            self.URL, headers=self.headers, timeout=10
        ).json()

        current_map_data = map_rotation["current"]
        next_map_data = map_rotation["next"]

        self.current_map_name = current_map_data["map"]
        self.next_map_name = next_map_data["map"]

        self.current_map_duration = current_map_data["DurationInMinutes"]
        self.next_map_duration = next_map_data["DurationInMinutes"]

        self.current_map_remaining = current_map_data["remainingMins"]
        self.next_map_start = next_map_data["start"]

class PlayerStatsCollector:
    """Class to collect player stats"""

    URL = "https://api.mozambiquehe.re/bridge"

    def __init__(
        self,
        api_key: str,
        uid: str = None,
        player_name: str = None,
        platform: str = None,
    ):
        """Initialize the PlayerStatsCollector.

        Args:
        api_key (str): The API key for accessing the stats API.
        uid (str, optional): The unique identifier for the player. Defaults to None.
        player_name (str, optional): The player's name. Defaults to None.
        platform (str, optional): The platform the player plays on. Defaults to None.
        """
        self.uid = uid
        self.platform = platform
        self.player_name = player_name
        self.headers = {"Authorization": api_key}

        # TODO: Convert to dictionary and/or properties
        """
        class test:
            def __init__(self):
            self.data = {"kills": 3, "deaths": 3}
        
            @property
            def kills(self):
            return self.data["kills"]

            @property
            def deaths(self):
                return self.data["deaths"]
        """

        # Data from global stats
        self.player_identifier = ""
        self.player_platform = ""
        self.level = 0
        self.next_level_percentage = 0
        self.banned = ""
        self.ban_duration = 0

        # Data from BR Ranking
        self.br_rank_name = ""
        self.br_rank_score = 0
        self.br_rank_div = 0

        # Data from Arena Rank
        self.arena_rank_name = ""
        self.arena_rank_score = 0
        self.arena_rank_div = 0

        # Data from BattlePass
        self.battle_pass_level = 0
        self.battle_pass_history = 0

        # Data from Realtime
        self.lobby_state = ""
        self.is_online = False
        self.is_in_game = False
        self.party_full = False
        self.selected_legend = ""
        self.current_state = ""

        # Data from Current Legend
        self.current_legend_name = ""
        self.current_legend_br_kills = 0

        # Data from Legends Kills
        self.all_legends_kills = {}

        # Data from Player Total
        self.kills = 0
        self.kill_death_ratio = ""

        # Data from Mozambique
        self.mozambique_cluster_server = ""

        # Data from API
        self.processing_time = 0

    def populate_data(self):
        """
        Populates data from the API and assigns various player stats and information to instance variables.
        """
        logging.debug("Collecting from: %s", self.URL)
        logging.debug("API KEY: %s", self.headers["Authorization"])

        if self.player_name:
            player_stats = requests.get(
                self.URL,
                headers=self.headers,
                params={"player_name": self.player_name, "platform": self.platform},
                timeout=10,
            ).json()
        else:
            player_stats = requests.get(
                self.URL,
                headers=self.headers,
                params={"uid": self.uid, "platform": self.platform},
                timeout=10,
            ).json()

        player_info_data = player_stats["global"]
        player_realtime_data = player_stats["realtime"]
        player_current_legend_data = player_stats["legends"]["selected"]
        player_legends_kills = player_stats["legends"]["all"]
        player_mozambique_data = player_stats["mozambiquehere_internal"]
        player_total_data = player_stats["total"]
        api_data = player_stats["processingTime"]

        # Data from global stats
        self.player_identifier = player_info_data["name"]
        self.player_platform = player_info_data["platform"]
        self.level = player_info_data["level"]
        self.next_level_percentage = player_info_data["toNextLevelPercent"]
        self.banned = player_info_data["bans"]["isActive"]
        self.ban_duration = player_info_data["bans"]["remainingSeconds"]

        # Data from BR Ranking
        self.br_rank_name = player_info_data["rank"]["rankName"]
        self.br_rank_score = player_info_data["rank"]["rankScore"]
        self.br_rank_div = player_info_data["rank"]["rankDiv"]

        # Data from Arena Rank
        self.arena_rank_name = player_info_data["arena"]["rankName"]
        self.arena_rank_score = player_info_data["arena"]["rankScore"]
        self.arena_rank_div = player_info_data["arena"]["rankDiv"]

        # Data from BattlePass
        self.battle_pass_level = player_info_data["battlepass"]["level"] or 0
        self.battle_pass_history = player_info_data["battlepass"]["history"] or 0

        # Data from Realtime
        self.lobby_state = player_realtime_data["lobbyState"]
        self.is_online = bool(player_realtime_data["isOnline"])
        self.is_in_game = bool(player_realtime_data["isInGame"])
        self.party_full = bool(player_realtime_data["partyFull"])
        self.selected_legend = player_realtime_data["selectedLegend"]
        self.current_state = player_realtime_data["currentState"]

        # Data from Current Legend
        self.current_legend_name = player_current_legend_data["LegendName"]
        self.current_legend_br_kills = player_current_legend_data["data"][0]["value"]

        # Data from All Legends
        self.all_legends_kills = {}

        # Generator Expression to extract kill value from all legends
        for legend_name, legend_info in player_legends_kills.items():
            if legend_name == "Global":
                continue  # skip
            if "data" not in legend_info:
                # alternative: if not legend_info.get('data'):
                continue
            kill_value = next(
                (
                    item["value"]
                    for item in legend_info["data"]
                    if item["key"] == "kills"
                ),
                0,
            )
            if kill_value != 0:
                self.all_legends_kills[legend_name] = kill_value

        # Data from Player Total
        self.kills = player_total_data["kills"]["value"]
        self.kill_death_ratio = float(player_total_data["kd"]["value"])

        # Data from Mozambique
        self.mozambique_cluster_server = player_mozambique_data["clusterSrv"]

        # Data from API
        self.processing_time = api_data

class ApexCollector:
    """Class aggregates the data from the collectors and exposes it using Prometheus metrics."""

    def __init__(
        self,
        player_stats_collector: PlayerStatsCollector,
        map_stats_collector: MapDataCollector,
        registry: CollectorRegistry = REGISTRY,
    ):
        """
        Initializes the class with the player_stats_collector, map_stats_collector, and optional registry. 
        """
        self.registry = registry

        # Define Prometheus metrics for map stats
        self.current_session_map = Info(
            "apex_current_map", "Name of the current map", registry=registry
        )

        self.current_session_duration = Gauge(
            "apex_current_map_duration_total",
            "Duration of the current map in minutes",
            registry=registry,
        )

        self.current_session_remaining = Gauge(
            "apex_current_map_remaining_total",
            "Time remaining of the current map in minutes",
            registry=registry,
        )

        self.next_session_map = Info(
            "apex_next_map", "Name of the next map", registry=registry
        )

        self.next_session_start = Gauge(
            "apex_next_map_start_total",
            "Start time of the next map in minutes",
            registry=registry,
        )

        self.next_session_duration = Gauge(
            "apex_next_map_duration_minutes",
            "Duration of the next map in minutes",
            registry=registry,
        )

        # Define Prometheus Metrics for Player Stats
        self.player_identifier = Info(
            "apex_player_identifier", "Name of the player", registry=registry
        )

        self.player_platform = Info(
            "player_platform", "Platform of the player", registry=registry
        )

        self.level = Gauge("player_level", "Level of the player", registry=registry)

        self.next_level_percentage = Gauge(
            "player_next_level_percentage",
            "Next level percentage of the player",
            registry=registry,
        )

        self.banned = Info("player_banned", "Is the player banned", registry=registry)

        self.ban_duration = Gauge(
            "player_ban_duration", "Ban duration of the player", registry=registry
        )

        self.br_rank_name = Info(
            "player_br_rank_name", "BR Rank Name of the player", registry=registry
        )

        self.br_rank_score = Gauge(
            "player_br_rank_score", "BR Rank Score of the player", registry=registry
        )

        self.br_rank_div = Gauge(
            "player_br_rank_div", "BR Rank Division of the player", registry=registry
        )

        self.arena_rank_name = Info(
            "player_arena_rank_name", "Arena Rank Name of the player", registry=registry
        )

        self.arena_rank_score = Gauge(
            "player_arena_rank_score",
            "Arena Rank Score of the player",
            registry=registry,
        )

        self.arena_rank_div = Gauge(
            "player_arena_rank_div",
            "Arena Rank Division of the player",
            registry=registry,
        )

        self.battle_pass_level = Gauge(
            "player_battle_pass_level",
            "Battle Pass Level of the player",
            registry=registry,
        )

        self.battle_pass_history = Gauge(
            "player_battle_pass_history",
            "Battle Pass History of the player",
            registry=registry,
        )

        self.lobby_state = Info(
            "player_lobby_state", "Lobby state of the player", registry=registry
        )

        self.is_online = Gauge(
            "player_is_online", "Is the player online", registry=registry
        )

        self.is_in_game = Gauge(
            "player_is_in_game", "Is the player in a game", registry=registry
        )

        self.party_full = Info(
            "player_party_full", "Is the player in a party", registry=registry
        )

        self.selected_legend = Info(
            "player_selected_legend", "Name of the selected legend", registry=registry
        )

        self.active_legend = Info(
            "player_active_legend", "Name of the active legend", registry=registry
        )

        self.active_legend_kills = Gauge(
            "player_active_legend_kills",
            "Total kills of the active legend",
            registry=registry,
        )

        self.current_state = Info(
            "player_current_state", "Current state of the player", registry=registry
        )

        self.legend_kills = Gauge(
            "player_legend_kills",
            "Total kills for each legend",
            ["legend_name"],
            registry=registry,
        )

        self.kills = Gauge(
            "player_kills_total", "Total kills of the player", registry=registry
        )

        self.kill_death_ratio = Gauge(
            "player_kill_death_ratio",
            "Kill/Death Ratio of the player",
            registry=registry,
        )

        self.mozambique_cluster_server = Info(
            "player_mozambique_cluster_server",
            "Cluster name presenting API",
            registry=registry,
        )

        self.processing_time = Gauge(
            "player_processing_time",
            "API Processing Time in milliseconds",
            registry=registry,
        )

        self.player_stats_collector = player_stats_collector

        self.map_stats_collector = map_stats_collector

    def collect(self):
        """
        Collects and populates various player and map statistics, and
        defines Prometheus metrics for map and player stats.
        """
        self.player_stats_collector.populate_data()
        self.map_stats_collector.populate_data()

        # Improve readability by variablizing the map name
        current_map_name = self.map_stats_collector.current_map_name
        next_map_name = self.map_stats_collector.next_map_name

        # Define Prometheus Metrics for Map Stats
        self.current_session_map.info({"map_name": current_map_name})
        self.current_session_duration.set(self.map_stats_collector.current_map_duration)
        self.current_session_remaining.set(
            self.map_stats_collector.current_map_remaining
        )
        self.next_session_map.info({"next_map_name": next_map_name})
        self.next_session_duration.set(self.map_stats_collector.next_map_duration)
        self.next_session_start.set(self.map_stats_collector.next_map_start)

        # Define Prometheus Metrics for Player Stats
        self.player_identifier.info(
            {"player_identifier": self.player_stats_collector.player_identifier}
        )
        self.player_platform.info(
            {"platform": self.player_stats_collector.player_platform}
        )
        self.level.set(self.player_stats_collector.level)
        self.next_level_percentage.set(
            self.player_stats_collector.next_level_percentage
        )
        self.banned.info({"banned": str(self.player_stats_collector.banned)})
        self.ban_duration.set(self.player_stats_collector.ban_duration)
        self.br_rank_name.info(
            {"br_rank_name": self.player_stats_collector.br_rank_name}
        )
        self.br_rank_score.set(self.player_stats_collector.br_rank_score)
        self.br_rank_div.set(self.player_stats_collector.br_rank_div)
        self.arena_rank_name.info(
            {"arena_rank_name": self.player_stats_collector.arena_rank_name}
        )
        self.arena_rank_score.set(self.player_stats_collector.arena_rank_score)
        self.arena_rank_div.set(self.player_stats_collector.arena_rank_div)
        self.battle_pass_level.set(self.player_stats_collector.battle_pass_level)
        self.battle_pass_history.set(self.player_stats_collector.battle_pass_history)
        self.lobby_state.info(
            {"lobby_state": self.player_stats_collector.lobby_state}
        )  # TODO: convert to ENUM
        self.is_online.set(int(self.player_stats_collector.is_online))
        self.is_in_game.set(int(self.player_stats_collector.is_in_game))
        self.party_full.info(
            {"party_full": str(self.player_stats_collector.party_full)}
        )
        self.selected_legend.info(
            {"selected_legend": self.player_stats_collector.selected_legend}
        )
        self.active_legend.info(
            {"active_legend": self.player_stats_collector.current_legend_name}
        )
        self.active_legend_kills.set(
            self.player_stats_collector.current_legend_br_kills
        )
        self.current_state.info(
            {"current_state": self.player_stats_collector.current_state}
        )
        for legend_name, kills in self.player_stats_collector.all_legends_kills.items():
            self.legend_kills.labels(legend_name).set(kills)
        self.kills.set(self.player_stats_collector.kills)
        self.kill_death_ratio.set(float(self.player_stats_collector.kill_death_ratio))
        self.mozambique_cluster_server.info(
            {
                "mozambique_cluster_server": self.player_stats_collector.mozambique_cluster_server
            }
        )
        self.processing_time.set(self.player_stats_collector.processing_time)

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO").upper()),
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.info("Starting exporter")

    # Check required environment variables are set
    if not os.environ.get("USER_ID") and not os.environ.get("PLAYER_NAME"):
        logging.error("Either USER_ID or PLAYER_NAME must be set")
        sys.exit(1)

    if os.environ.get("USER_ID") and os.environ.get("PLAYER_NAME"):
        logging.error("Both USER_ID and PLAYER_NAME cannot be set")
        sys.exit(1)

    if not os.environ.get("API_KEY"):
        logging.error("API_KEY not set")
        sys.exit(1)

    credentials = {
        "uid": os.environ.get("USER_ID"),
        "player_name": os.environ.get("PLAYER_NAME"),
        "api_key": os.environ.get("API_KEY"),
    }

    # Pass platform as an argument ONLY to the PlayerStatsCollector
    player_data = PlayerStatsCollector(
        **credentials, platform=os.environ.get("PLATFORM", "").upper()
    )
    map_data = MapDataCollector(**credentials)

    collector = ApexCollector(player_data, map_data)

    # Unregister default collectors
    for collector in [PROCESS_COLLECTOR, PLATFORM_COLLECTOR, GC_COLLECTOR]:
        REGISTRY.unregister(collector)

    start_http_server(port=5000)

    while True:
        collector.collect()
        time.sleep(30) # TODO: Collect only when requesting data; modify prometheus_client to do this
