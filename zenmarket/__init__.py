'''
CLI for zenmarket
'''
import sys
import traceback
import json
from typing import Callable, NewType
import click

from zenmarket.algo import level1 as l1, level2 as l2, level3 as l3


# pylint: disable=C0103,W0702
PriceFunc = NewType('PriceFunc', Callable[[dict], dict])


def pricing(infile: click.File, outfile: click.File, price: PriceFunc) -> None:
    '''
    Gets data from infile, computes price(data), writes the result to outfile
    '''
    try:
        data = json.loads(infile.read().decode())
        response = price(data)
        outfile.write(('%s\n' % json.dumps(
            response, outfile, indent=2, sort_keys=True)).encode())
        outfile.flush()
    except:
        print(traceback.format_exception(*sys.exc_info())[-1], file=sys.stderr)
        sys.exit(1)


@click.group()
def cli():
    '''
    Command line root
    '''
    pass


@cli.command()
@click.argument('infile', type=click.File('rb'))
@click.argument('outfile', type=click.File('wb'))
def level1(infile: click.File, outfile: click.File) -> None:
    '''
    cli for level1 pricing algo
    usage:
    level1 data.json outfile.json
    cat data.json | zm-cli level1 - outfile.json
    cat data.json | zm-cli level1 - - > outfile.json
    '''
    return pricing(infile, outfile, l1.price)


@cli.command()
@click.argument('infile', type=click.File('rb'))
@click.argument('outfile', type=click.File('wb'))
def level2(infile: click.File, outfile: click.File) -> None:
    '''
    cli for level2 pricing algo
    usage:
    level2 data.json outfile.json
    cat data.json | zm-cli level2 - outfile.json
    cat data.json | zm-cli level2 - - > outfile.json
    '''
    return pricing(infile, outfile, l2.price)


@cli.command()
@click.argument('infile', type=click.File('rb'))
@click.argument('outfile', type=click.File('wb'))
def level3(infile: click.File, outfile: click.File) -> None:
    '''
    cli for level3 pricing algo
    usage:
    level3 data.json outfile.json
    cat data.json | zm-cli level3 - outfile.json
    cat data.json | zm-cli level3 - - > outfile.json
    '''
    return pricing(infile, outfile, l3.price)
