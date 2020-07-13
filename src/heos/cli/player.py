import logging
import sys

import click

from ..registry import Registry
from .main import cli


@cli.group()
@click.option("--name", required=True, help="Name of the player.")
@click.option(
    "--rediscover/--no-rediscover",
    default=False,
    help=(
        "Whether to rediscover devices. Uses cached devices "
        "if present when False (default)."
    ),
)
@click.pass_context
def player(ctx, name, rediscover):
    """Controls for players."""

    ctx.ensure_object(dict)

    registry = Registry()

    if rediscover:
        registry.discover()

    try:
        player = registry.players[name]
    except KeyError:
        logging.error(
            f"Unknown player '{name}', available players "
            f"are: {list(registry.players.keys())}"
        )
        sys.exit(1)

    ctx.obj["player"] = player


@player.command()
@click.pass_context
def mute(ctx):
    """Mutes a player."""

    with ctx.obj["player"] as player:
        player.mute = True
        logging.info(f"Muted player '{player.name}'")


@player.command()
@click.pass_context
def unmute(ctx):
    """Unmutes a player."""

    with ctx.obj["player"] as player:
        player.mute = False
        logging.info(f"Unmuted player '{player.name}'")


@player.command()
@click.option("--level", required=True, type=int)
@click.pass_context
def volume(ctx, level):
    """Sets the volume on a player."""

    with ctx.obj["player"] as player:
        player.volume = level
        logging.info(f"Set volume on player '{player.name}' to {player.volume}")


@player.command()
@click.pass_context
def play(ctx):
    """Starts/resumes playback on a player."""

    with ctx.obj["player"] as player:
        player.play()


@player.command()
@click.pass_context
def pause(ctx):
    """Pauses playback on a player."""

    with ctx.obj["player"] as player:
        player.pause()


@player.command()
@click.pass_context
def stop(ctx):
    """Stops playback on a player."""

    with ctx.obj["player"] as player:
        player.stop()
