import json

import click

from zenmarket.algo.level2 import price_plus_fees


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
    response = price_plus_fees(data)
    outfile.write(('%s\n' % json.dumps(
        response, outfile, indent=2, sort_keys=True)).encode())
    outfile.flush()
