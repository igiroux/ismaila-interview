'''
Level 3 pricing tests
'''
import pytest
from zenmarket.algo import level3


def test_discount():
    '''
    Test discounting
    '''
    assert level3.discount_as_func('amount', 10)(100) == 90
    assert level3.discount_as_func('percentage', 10)(300) == 270


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


def _test_response_format(response):
    assert response and isinstance(response, dict)
    assert "carts" in response


def _test_plain_response_format(response):
    _test_response_format(response)
    assert response["carts"]
    assert isinstance(response["carts"], (list, tuple))
    for cart in response["carts"]:
        assert isinstance(cart, dict)
        assert cart
        assert "id" in cart
        assert "total" in cart


def test_discounted_simple_cart(simple_cart):
    '''
    One cart price returns the price of the article
    '''
    total_price, data = simple_cart
    resp = level3.price(data)
    _test_plain_response_format(resp)
    assert len(resp["carts"]) == 1
    cart = resp["carts"][0]
    assert cart["id"] == 10
    assert cart["total"] == total_price, data['carts']
