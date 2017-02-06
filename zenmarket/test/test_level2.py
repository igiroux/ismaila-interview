'''
Level 2 pricing unit tests
'''
from random import randrange

import pytest

from zenmarket.algo.level1 import BadDataFormat
from zenmarket.algo import level2


@pytest.fixture(name='fee_function')
def fee_function_fixture():
    '''
    Fee Function Fixture: F3

    F3: x -> y
        0 -> 800
     1000 -> 400
     2000 -> 0
    '''
    return (
        [1000, 2000, float('+Inf')],
        [800, 400, 0]
    )


@pytest.fixture(scope='module', name='random_prices', params=(
    ([randrange(0, 1000) for _ in range(30)], 800),
    ([randrange(1000, 2000) for _ in range(30)], 400),
    ([randrange(2000, 10000) for _ in range(30)], 0),
))
def random_prices_fixture(request):
    '''
    Random price fixture
    '''
    prices, fee = request.param
    return ((price, fee) for price in prices)


@pytest.fixture(name='fee_data')
def fee_data_fixture():
    '''
    Fee input data fixture
    '''
    return [
        {
            "eligible_transaction_volume": {
                "min_price": 0,
                "max_price": 1000
            },
            "price": 800
        },
        {
            "eligible_transaction_volume": {
                "min_price": 1000,
                "max_price": 2000
            },
            "price": 400
        },
        {
            "eligible_transaction_volume": {
                "min_price": 2000,
                "max_price": None
            },
            "price": 0
        },
    ]


@pytest.fixture(name='invalid_fee_data', params=[
    ({
        "eligible_transaction_volume": {
            'min_price': min_price,
            'max_price': max_price
        },
        'price': fee
    }, exc)
    for min_price, max_price, fee, exc in [
        (-1000, 2000, 400, BadDataFormat),
        (1000, -2000, 400, BadDataFormat),
        (1000, 2000, -400, BadDataFormat),
        (2000, 1000, 400, level2.PriceRangeError),
    ]
])
def invalid_fee_data_fixture(request):
    '''
    Invalid data fixture raises exception
    '''
    fee_data_elem, exception = request.param
    return exception, [
        {
            "eligible_transaction_volume": {
                "min_price": 0,
                "max_price": 1000
            },
            "price": 800
        },
        fee_data_elem,
        {
            "eligible_transaction_volume": {
                "min_price": 2000,
                "max_price": None
            },
            "price": 0
        },
    ]


@pytest.fixture(name='simple_cart', params=[
    ({
        "id": 1,
        "items": [
            {"article_id": 1, "quantity": 20},  # 20 * 100
        ]
    }, 20 * 100 + 0),
    ({
        "id": 2,
        "items": [
            {"article_id": 2, "quantity": 5},  # 5 * 200
        ]
    }, 5 * 200 + 400),
    ({
        "id": 3,
        "items": []
    }, 0 + 800),
])
def simple_cart_fixture(request):
    '''
    Simple cart data fixture
    '''
    cart, total = request.param
    return cart['id'], total, {
        "articles": [
            {"id": 1, "name": "water", "price": 100},
            {"id": 2, "name": "honey", "price": 200},
        ],
        "carts": [cart],
        "delivery_fees": [
            {
                "eligible_transaction_volume": {
                    "min_price": 0,
                    "max_price": 1000
                },
                "price": 800
            },
            {
                "eligible_transaction_volume": {
                    "min_price": 1000,
                    "max_price": 2000
                },
                "price": 400
            },
            {
                "eligible_transaction_volume": {
                    "min_price": 2000,
                    "max_price": None
                },
                "price": 0
            }
        ],
    }


def test_fee_interpolation(random_prices, fee_function):
    '''
    Interpolation should work between bounds
    '''
    sample = random_prices
    for price, expected_fee in sample:
        assert level2.interpolate_fees(price, fee_function) == expected_fee


def test_fee_function_bounds(fee_function):
    '''
    Interpolation should work for bounds
    '''
    prices = [0, 1000, 2000]
    fees = [800, 400, 0]
    for aprice, fee in zip(prices, fees):
        assert level2.interpolate_fees(aprice, fee_function) == fee


def test_fee_data_as_cost_function(fee_data):
    '''
    cost function generator should generate expected abscissa and ordinate
    '''
    prices, fees = level2.fee_data_to_cost_table(fee_data)
    assert tuple(prices) == (1000, 2000, float('+Inf'))
    assert tuple(fees) == (800, 400, 0)


def test_invalid_fee_data(invalid_fee_data):
    '''
    Invalid data should raise proper exception
    '''
    exception, data = invalid_fee_data
    with pytest.raises(exception):
        level2.fee_data_to_cost_table(data)


def test_price(simple_cart):
    '''
    level2.price(simple_cart)[0] == {'carts': [{'id': 1, 'total': 2000}]}
    '''
    cart_id, total, data = simple_cart
    resp = level2.price(data)
    assert len(resp["carts"]) == 1
    cart = resp["carts"][0]
    assert cart["id"] == cart_id
    assert cart["total"] == total


@pytest.fixture(scope='module', name='cart_results', params=(
    ([{'id': 7, 'total': randrange(0, 1000)} for _ in range(30)], 800),
    ([{'id': 7, 'total': randrange(1000, 2000)} for _ in range(30)], 400),
    ([{'id': 7, 'total': randrange(2000, 10000)} for _ in range(30)], 0),
))
def cart_price_plus_fees_fixture(request):
    '''
    Fixture that produces level1 cart price result
    '''
    return request.param


def test_plus_fees(cart_results, fee_function):
    '''
    level2.plus_fee(cart, cost_function)
    '''
    carts, fee = cart_results
    for cart in carts:
        resp = level2.plus_fees(cart, fee_function)
        assert resp['id'] == cart['id']
        assert resp['total'] == cart['total'] + fee
