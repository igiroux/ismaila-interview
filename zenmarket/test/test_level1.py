'''
Level 1 pricing test
'''

# pylint: disable=missing-docstring


from zenmarket.algo.level1 import price
import pytest


@pytest.fixture(name='data')
def input_data_fixture():
    '''
    Data fixture
    '''
    return {
        "articles": [
            {"id": 1, "name": "water", "price": 100},
            {"id": 2, "name": "honey", "price": 200},
            {"id": 3, "name": "mango", "price": 400},
            {"id": 4, "name": "tea", "price": 1000},
        ],
        "carts": [
            {
                "id": 1,
                "items": [
                    {"article_id": 1, "quantity": 6},
                    {"article_id": 2, "quantity": 2},
                    {"article_id": 4, "quantity": 1},
                ]
            },
            {
                "id": 2,
                "items": [
                    {"article_id": 2, "quantity": 1},
                    {"article_id": 3, "quantity": 3}
                ]
            },
            {
                "id": 3,
                "items": []
            }
        ]

    }


@pytest.fixture(name='empty_data')
def empty_data_input_data_fixture():
    '''
    Empty dict fixture
    '''

    return {"articles": [], "carts": []}


@pytest.fixture(scope='module', name='invalid_data', params=[
    {"articles": []},
    {"carts": []}
])
def invalid_data_input_data_fixture(request):
    '''
    Empty dict fixture
    '''

    return request.param


@pytest.fixture(scope='module', name='simple_cart', params=[
    ([{"article_id": 4, "quantity": 1}], 1000),
    ([{"article_id": 4, "quantity": 2}], 2000),
    ([
        {"article_id": 4, "quantity": 1},
        {"article_id": 1, "quantity": 1},
    ], 1100),
    ([
        {"article_id": 4, "quantity": 2},
        {"article_id": 1, "quantity": 3},
        {"article_id": 3, "quantity": 1},
    ], 2700),
])
def simple_cart_input_data_fixture(request):
    '''
    Empty dict fixture
    '''
    cart_items, total_price = request.param
    return total_price, {
        "articles": [
            {"id": 4, "name": "tea", "price": 1000},
            {"id": 1, "name": "tea", "price": 100},
            {"id": 3, "name": "tea", "price": 400},
        ],
        "carts": [{'id': 10, 'items': cart_items}]
    }


@pytest.fixture(scope='module', name='multi_cart', params=[
    ([
        {'id': 1, 'items': [{"article_id": 4, "quantity": 1}]},
        {'id': 2, 'items': [{"article_id": 4, "quantity": 2}]},
    ], {'carts': [{'id': 1, 'total': 1000}, {'id': 2, 'total': 2000}]}),
    ([
        {'id': 3, 'items': [
            {"article_id": 4, "quantity": 1},
            {"article_id": 1, "quantity": 1},
        ]},
        {'id': 4, 'items': [
            {"article_id": 4, "quantity": 2},
            {"article_id": 1, "quantity": 3},
            {"article_id": 3, "quantity": 1},
        ]},
    ], {'carts': [{'id': 3, 'total': 1100}, {'id': 4, 'total': 2700}]}),
])
def multi_cart_input_data_fixture(request):
    '''
    Empty dict fixture
    '''
    carts, response = request.param
    return {
        "articles": [
            {"id": 4, "name": "tea", "price": 1000},
            {"id": 1, "name": "tea", "price": 100},
            {"id": 3, "name": "tea", "price": 400},
        ],
        "carts": carts
    }, response


@pytest.fixture(scope='module', name='corrupted_data', params=[
    {'articles': [], 'carts': None},  # carts
    {'articles': [], 'carts': [
        {'id': 1, 'items': [{"article_id": None, "quantity": 1}]}  # article_id
    ]},
    {'articles': [], 'carts': [{'items': []}, ], },  # cart id missing
    {'articles': [], 'carts': [{'id': 25, }, ], },  # cart items missing
    {'articles': [{"id": 4, }], 'carts': [
        {'id': 4, 'items': [{"article_id": 4, "quantity": 2}]},
    ]},  # article price missing
    {'articles': [{"id": 4, "price": 1000}], 'carts': [
        {'id': 4, 'items': [{"article_id": 4, }]},
    ]},  # cart item quantity missing
    {'articles': [{"id": 4, "price": 1000}], 'carts': [
        {'id': 4, 'items': [{"quantity": 2, }]},
    ]},  # cart item article_id missing
])
def corrupted_input_data_fixture(request):
    '''
    Data
    '''

    return request.param


def _test_response_format(response):
    assert response and isinstance(response, dict)
    assert "carts" in response


def test_price_empty_dict():
    """
    Empty dict should return empty response {"carts": []}
    """

    resp = price({})
    _test_response_format(resp)
    assert not resp["carts"], 'Empty dict should return empty {"carts": []}'


def test_price_valid_data(empty_data):
    """
    Empty cart returns {"carts": []}
    """

    resp = price(empty_data)
    _test_response_format(resp)
    assert not resp["carts"], 'Empty data should return {"carts": []}'


def test_price_invalid_data(invalid_data):
    """
    Invalid data raises ValueError
    """
    with pytest.raises(ValueError):
        price(invalid_data)


def _test_plain_response_format(response):
    _test_response_format(response)
    assert response["carts"]
    assert isinstance(response["carts"], (list, tuple))
    for cart in response["carts"]:
        assert isinstance(cart, dict)
        assert cart
        assert "id" in cart
        assert "total" in cart


def test_simple_article_cart(simple_cart):
    '''
    One cart price
    :returns the price of the article
    '''
    total_price, data = simple_cart
    resp = price(data)
    _test_plain_response_format(resp)
    assert len(resp["carts"]) == 1
    cart = resp["carts"][0]
    assert cart["id"] == 10
    assert cart["total"] == total_price


def test_multi_article_cart(multi_cart):
    '''
    Unique article price returns the price of the article
    '''
    data, expected = multi_cart
    resp = price(data)
    _test_plain_response_format(resp)
    assert len(resp["carts"]) == len(expected["carts"])
    for ref_cart, cart in zip(expected["carts"], resp["carts"]):
        assert cart['id'] == ref_cart['id']
        assert cart['total'] == ref_cart['total']


def test_price_corrupted_data(corrupted_data):
    """
    Invalid data raises ValueError
    """
    with pytest.raises(ValueError):
        price(corrupted_data)
