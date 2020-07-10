import logging

import click

from .registry import Registry

logging.basicConfig(level=logging.INFO)


@click.group()
def main():
    pass


@main.group()
def group():
    pass


@group.command()
@click.option("--name", required=True)
@click.option("--mute/--unmute", default=True)
def set_mute(name, mute):
    """Mutes/unmutes a player group."""

    registry = Registry()

    action = "Mute" if mute else "Unmute"
    with registry.groups[name] as group:
        group.mute = mute
        logging.info(f"{action}d group '{group.name}'")


@group.command()
@click.option("--name", required=True)
@click.option("--level", required=True, type=int)
def set_volume(name, level):
    """Sets the volume on a player group."""

    registry = Registry()

    with registry.groups[name] as group:
        group.volume = level
        logging.info(f"Set volume on group '{group.name}' to {group.volume}")


@main.group()
def player():
    pass


@player.command()
@click.option("--name", required=True)
@click.option("--mute/--unmute", default=True)
def set_mute(name, mute):
    """Mutes/unmutes a player."""

    registry = Registry()

    action = "Mute" if mute else "Unmute"
    with registry.players[name] as player:
        player.mute = mute
        logging.info(f"{action}d player '{player.name}'")


@player.command()
@click.option("--name", required=True)
@click.option("--level", required=True, type=int)
def set_volume(name, level):
    """Sets the volume on a player."""

    registry = Registry()

    with registry.players[name] as player:
        player.volume = level
        logging.info(f"Set volume on player '{player.name}' to {player.volume}")
