from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import yaml

from . import ssdp
from .client import Client
from .player import Player, PlayerGroup


class Registry:
    """Registry that discovers and provides access to HEOS players and player groups."""

    HEOS_URN = "urn:schemas-denon-com:device:ACT-Denon:1"

    def __init__(self, file_path=".heos"):
        self.file_path = file_path

        self._players = {}
        self._groups = {}

        if Path(self.file_path).exists():
            self.load()
        else:
            self.discover()

    @property
    def players(self):
        """Returns a dict of known players."""
        return {
            player.name: Player(id=player.id, name=player.name, host=player.host)
            for player in self._players.values()
        }

    @property
    def groups(self):
        """Returns a dict of known player groups."""
        return {
            group.name: PlayerGroup(
                id=group.id, name=group.name, host=self._players[group.leader].host,
            )
            for group in self._groups.values()
        }

    def discover(self) -> None:
        """Discovers players on the local network using SSDP."""

        ssdp_responses = ssdp.discover(self.HEOS_URN)

        players, groups = {}, {}
        for ssdp_response in ssdp_responses:
            with Client(ssdp_response.host) as client:

                # Identify players.
                response = client.send_command("player/get_players")
                for entry in response.payload:
                    players[entry["name"]] = PlayerEntry(
                        name=entry["name"],
                        model=entry["model"],
                        host=entry["ip"],
                        id=entry["pid"],
                    )

                # Identify groups.
                response = client.send_command("group/get_groups")
                for entry in response.payload:
                    leader = [
                        player["name"]
                        for player in entry["players"]
                        if player["role"] == "leader"
                    ][0]
                    members = [
                        player["name"]
                        for player in entry["players"]
                        if player["role"] == "member"
                    ]

                    groups[entry["name"]] = GroupEntry(
                        name=entry["name"],
                        id=entry["gid"],
                        leader=leader,
                        members=members,
                    )

        self._players = players
        self._groups = groups
        self.save()

    def load(self):
        """Loads the registry from a .heos cache file."""

        with open(self.file_path) as file_:
            config = yaml.safe_load(file_)
            players_conf = config.get("players", [])
            groups_conf = config.get("groups", [])

        self._players = {entry["name"]: PlayerEntry(**entry) for entry in players_conf}
        self._groups = {entry["name"]: GroupEntry(**entry) for entry in groups_conf}

    def save(self):
        """Saves the registry from a .heos cache file."""

        config = {
            "players": [asdict(player) for player in self._players.values()],
            "groups": [asdict(group) for group in self._groups.values()],
        }

        with open(self.file_path, "w") as file_:
            yaml.dump(config, file_)


@dataclass
class PlayerEntry:
    """Player config entry."""

    name: str
    model: str
    host: str
    id: int


@dataclass
class GroupEntry:
    """Player group config entry."""

    name: str
    id: str
    leader: str
    members: List[str]
