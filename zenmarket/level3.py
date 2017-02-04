'''
Level 2 priceing main function
'''
import json

import click
from zenmarket.algo import level3


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
    response = level3.price(data)
    outfile.write(('%s\n' % json.dumps(
        response, outfile, indent=2, sort_keys=True)).encode())
    outfile.flush()
