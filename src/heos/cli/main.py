import logging

import click

logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    pass
