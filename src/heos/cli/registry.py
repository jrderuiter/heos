import logging
import sys

import click

from ..registry import Registry
from .main import cli


@cli.group()
@click.option(
    "--rediscover/--no-rediscover",
    default=False,
    help=(
        "Whether to rediscover devices. Uses cached devices "
        "if present when False (default)."
    ),
)
@click.pass_context
def registry(ctx, rediscover):
    """Discover available players and groups."""

    ctx.ensure_object(dict)

    registry = Registry()

    if rediscover:
        registry.discover()

    ctx.obj["registry"] = registry


@registry.command()
@click.pass_context
def players(ctx):
    """Prints known players."""

    for key in ctx.obj["registry"].players.keys():
        print(key)


@registry.command()
@click.pass_context
def groups(ctx):
    """Prints known groups."""

    for key in ctx.obj["registry"].groups.keys():
        print(key)

