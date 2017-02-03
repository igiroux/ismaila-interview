'''
Level 2 pricing unit tests
'''
from random import randrange

import pytest

from zenmarket.algo.level2 import delivery_fees, fee_data_to_cost_table


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
    return ((price, price + fee) for price in prices)


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
    {
        key: {
            min_key: min_price,
            max_key: max_price
        },
        price_key: price_value
    }
    for key, (min_key, min_price), (max_key, max_price), (price_key, price_value) in [
        ("eligible_transaction_volume", ('min_price', 1000), ('max_price', 1000), ('price', 400))
    ]
])
def invalid_fee_data_fixture(request):
    '''
    '''
    return [
        {
            "eligible_transaction_volume": {
                "min_price": 0,
                "max_price": 1000
            },
            "price": 800
        },
        request.param,
        {
            "eligible_transaction_volume": {
                "min_price": 2000,
                "max_price": None
            },
            "price": 0
        },
    ]


def test_fee_interpolation(random_prices, fee_function):
    '''
    Interpolation should work between bounds
    '''
    sample = random_prices
    for price, expected_cost in sample:
        assert delivery_fees(price, fee_function) == expected_cost


def test_fee_function_bounds(fee_function):
    '''
    Interpolation should work for bounds
    '''
    prices = [0, 1000, 2000]
    fees = [800, 400, 0]
    for price, fee in zip(prices, fees):
        assert delivery_fees(price, fee_function) == price + fee


def test_fee_data_as_cost_function(fee_data):
    x, fx = fee_data_to_cost_table(fee_data)
    assert tuple(x) == (1000, 2000, float('+Inf'))
    assert tuple(fx) == (800, 400, 0)


def test_invalid_fee_data(invalid_fee_data):
    '''
    Test data format
    '''
    fee_data_to_cost_table(invalid_fee_data)
