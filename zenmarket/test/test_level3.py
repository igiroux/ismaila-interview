'''
Level 3 pricing tests
'''
import pytest
from zenmarket.algo import level3


@pytest.fixture(scope='module', name='simple_cart', params=[
    ([{"article_id": 4, "quantity": 1}], 1 * 1000 + 400),
    ([{"article_id": 4, "quantity": 2}], 2 * 1000 + 0),
    ([
        {"article_id": 4, "quantity": 1},  # 1 * 1000
        {"article_id": 1, "quantity": 1},  # 1 * 100
    ], 1100 + 400),
    ([
        {"article_id": 5, "quantity": 1},  # 1 * 999 * (100 - 30) // 100
    ], 1 * 999 * (100 - 30) // 100 + 800),
    ([
        {"article_id": 5, "quantity": 1},  # _ 999 * (100 - 30) // 100
        {"article_id": 6, "quantity": 1},  # + 999 < 2000
    ], 999 * (100 - 30) // 100 + 999 + 400),
    ([
        {"article_id": 4, "quantity": 2},  # _ 2 * 1000
    ], 2 * 1000 + 0),
    ([
        {"article_id": 2, "quantity": 10},  # + 10 * (200 - 25)
    ], 10 * (200 - 25) + 400),
    ([
        {"article_id": 3, "quantity": 1},  # + 1 * 400
    ], 1 * 400 + 800),
    ([
        {"article_id": 5, "quantity": 2},  # + 2 * 999 * (100 - 30) // 100
    ], 2 * 999 * (100 - 30) // 100 + 400),
    ([
        {"article_id": 4, "quantity": 2},  # _ 2 * 1000
        {"article_id": 2, "quantity": 10},  # 10 * (200 - 25)
        {"article_id": 3, "quantity": 1},  # _ 1 * 400
        {"article_id": 5, "quantity": 2},  # _ 2 * 999 * (100 - 30) // 100
    ], 2 * 1000 + 10 * (200 - 25) + 1 * 400 + 2 * 999 * (100 - 30) // 100),
])
def simple_cart_input_data_fixture(request):
    '''
    Empty dict fixture
    '''
    cart_items, total_price = request.param
    return total_price, {
        "articles": [
            {"id": 1, "name": "tea", "price": 100},
            {"id": 2, "name": "honey", "price": 200},
            {"id": 3, "name": "tea", "price": 400},
            {"id": 4, "name": "tea", "price": 1000},
            {"id": 5, "name": "ketchup", "price": 999},
            {"id": 6, "name": "mayonnaise", "price": 999},

        ],
        "carts": [{'id': 10, 'items': cart_items}],
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
            },
        ],
        "discounts": [
            {"article_id": 2, "type": "amount", "value": 25},
            {"article_id": 5, "type": "percentage", "value": 30},
        ],
    }


def test_discounted_simple_cart(simple_cart):
    '''
    One cart price returns the price of the article
    '''
    total_price, data = simple_cart
    resp = level3.price(data)
    assert len(resp["carts"]) == 1
    cart = resp["carts"][0]
    assert cart["id"] == 10
    assert cart["total"] == total_price, data['carts']


@pytest.fixture(name='sample_l3_data', params=[
    ({"id": 3, "items": [
        {"article_id": 5, "quantity": 1},
        {"article_id": 6, "quantity": 1},
    ]}, 1798),
    ({"id": 1, "items": [
        {"article_id": 1, "quantity": 6},
        {"article_id": 2, "quantity": 2},
        {"article_id": 4, "quantity": 1},
    ]}, 2350)
])
def simple_l3_cart_fixture(request):
    '''
    Complete level3 input data
    '''
    cart, total = request.param
    return cart, total, {
        "articles": [
            {"id": 1, "name": "water", "price": 100},
            {"id": 2, "name": "honey", "price": 200},
            {"id": 4, "name": "tea", "price": 1000},
            {"id": 5, "name": "ketchup", "price": 999},
            {"id": 6, "name": "mayonnaise", "price": 999},
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
            },
        ],
        "discounts": [
            {"article_id": 2, "type": "amount", "value": 25},
            {"article_id": 5, "type": "percentage", "value": 30},
            {"article_id": 6, "type": "percentage", "value": 30},
        ],
    }


def test_price(sample_l3_data):
    '''
    level3.price(sample_l3_data[-1]) == {'carts': [
        {"id": 1, "total": 2350},
        {"id": 2, "total": 1775},
    ]}
    '''
    input_cart, total, data = sample_l3_data
    response = level3.price(data)
    assert len(response['carts']) == 1
    cart = response['carts'][0]
    assert cart['id'] == input_cart['id']
    assert cart['total'] == total
