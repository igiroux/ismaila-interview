'''
Web Application
'''
import sys
import traceback
import json

import asyncio

from aiohttp import web

from zenmarket.algo import level1, level2, level3


@asyncio.coroutine
def handle_request(request, price_func):
    '''
    General request handler
    '''
    body = yield from request.post()
    data = json.loads(body['data'].file.read().decode())
    try:
        response = price_func(data)
    except:
        message = traceback.format_exception(*sys.exc_info())[-1]
        raise web.HTTPBadRequest(reason=message)
    else:
        return web.json_response(response)


def level1_handler(request):
    '''
    Request handler for /api/level1/price
    Handles level1 request pricing
    curl -F data=@level1/data.json http://<host>/api/level1/price
    '''
    return handle_request(request, level1.price)


def level2_handler(request):
    '''
    Request handler for /api/level2/price
    Handles level2 request pricing
    curl -F data=@level2/data.json http://<host>/api/level2/price
    '''
    return handle_request(request, level2.price)


def level3_handler(request):
    '''
    Request handler for /api/level3/price
    Handles level3 request pricing
    curl -F data=@level3/data.json http://<host>/api/level3/price
    '''
    return handle_request(request, level3.price)


def run_app(host='127.0.0.1', port=8888):
    '''
    aiohttp Application maker
    '''
    loop = asyncio.get_event_loop()
    app = web.Application(loop=loop)
    app.router.add_post('/api/level1/price', level1_handler)
    app.router.add_post('/api/level2/price', level2_handler)
    app.router.add_post('/api/level3/price', level3_handler)
    web.run_app(app, host=host, port=port)
