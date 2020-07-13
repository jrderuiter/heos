import logging
import sys

import click

from ..registry import Registry
from .main import cli


@cli.group()
@click.option("--name", required=True, help="Name of the player group.")
@click.option(
    "--rediscover/--no-rediscover",
    default=False,
    help=(
        "Whether to rediscover devices. Uses cached devices "
        "if present when False (default)."
    ),
)
@click.pass_context
def group(ctx, name, rediscover):
    """Controls for player groups."""

    ctx.ensure_object(dict)

    registry = Registry()

    if rediscover:
        registry.discover()

    try:
        group = registry.groups[name]
    except KeyError:
        logging.error(
            f"Unknown group '{name}', available groups "
            f"are: {list(registry.groups.keys())}"
        )
        sys.exit(1)

    ctx.obj["group"] = group


@group.command()
@click.pass_context
def mute(ctx):
    """Mutes a player group."""

    with ctx.obj["group"] as group:
        group.mute = True
        logging.info(f"Muted group '{group.name}'")


@group.command()
@click.pass_context
def unmute(ctx):
    """Unmutes a player group."""

    with ctx.obj["group"] as group:
        group.mute = False
        logging.info(f"Unmuted group '{group.name}'")


@group.command()
@click.pass_context
@click.option("--level", required=True, type=int)
def volume(ctx, level):
    """Sets the volume on a player group."""

    with ctx.obj["group"] as group:
        group.volume = level
        logging.info(f"Set volume on group '{group.name}' to {group.volume}")


@group.command()
@click.pass_context
def play(ctx):
    """Starts/resumes playback on a player group."""

    with ctx.obj["group"] as group:
        group.play()


@group.command()
@click.pass_context
def pause(ctx):
    """Pauses playback on a player group."""

    with ctx.obj["group"] as group:
        group.pause()


@group.command()
@click.pass_context
def stop(ctx):
    """Stops playback on a player group."""

    with ctx.obj["group"] as group:
        group.stop()
