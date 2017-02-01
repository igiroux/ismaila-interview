"""
level 1 main module
"""

from __future__ import print_function
import json

import click

from zenmarket.algo.level1 import price


@click.command()
@click.argument('infile', type=click.File('rb'))
@click.argument('outfile', type=click.File('wb'))
def main(infile: click.File, outfile: click.File) -> None:
    '''
    cli for level1 pricing algo
    usage:
    level1 data.json outfile.json
    cat data.json | level1 - outfile.json
    cat data.json | level1 - - > outfile.json
    '''
    data = json.loads(infile.read().decode())
    response = price(data)
    outfile.write(('%s\n' % json.dumps(response)).encode())
    outfile.flush()
