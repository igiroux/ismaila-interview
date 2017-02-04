'''
This is simple cart pricing module
'''
from operator import itemgetter
from typing import Callable, NewType

from zenmarket.algo import level2


def cart_price(cart: dict, articles: dict, discounts: dict) -> dict:
    '''
    :param cart dict: {'id': <id>, 'items': []}
    :param articles dict: {<id>: {'id': <id>, 'price': <price>, ...}, ...}
    :returns {id: cart['id'], total: dotproduct(<prices>, <quantities>)}

    >>> cart_price()
    '''

    def iter_cart_items_prices(items, articles, discounts):
        '''
        Generator that yields for each cart item (<cart_id>, <cart_item_price>)
        '''
        for item in items:
            try:
                item_price = articles[item['article_id']]['price']
                item_quantity = item['quantity']
                item_discount_func = discounts.get(
                    item['article_id'], lambda aprice: aprice)
            except KeyError:
                raise ValueError(
                    'Cart item price could not be found {}'.format(item))
            else:
                yield item_quantity, item_price, item_discount_func

    try:
        items = cart['items']
        cart_id = cart['id']
    except KeyError:
        raise ValueError(
            'Wrong cart fmt %r. Expected {"id": <id>, "items": []}' % cart)
    else:
        if not items:
            return {'id': cart_id, 'total': 0}

        resp = {
            'id': cart_id,
            'total': sum(
                quantity * discount_fun(price)
                for quantity, price, discount_fun in iter_cart_items_prices(
                    items, articles, discounts
                )
            )
        }
        return resp


# pylint: disable=C0103
DiscountFun = NewType('DiscountFun', Callable[[int], int])


def discount_as_func(discount_type: str, discount_value: int) -> DiscountFun:
    '''
    :returns a discount function which applies a discount to a price
    '''
    switch = {
        "amount": lambda aprice: aprice - discount_value,
        "percentage": lambda aprice: aprice * (100 - discount_value) // 100
    }
    return switch.get(discount_type, lambda aprice: aprice)


def price(data: dict) -> dict:
    '''
    Compute cart object price

    :param data dict: {'articles': [...], 'carts': [...]}
    :returns {'carts': [{'id': <id>, 'total': <total>}, ...]}
    E.g.:

    >>> data = {
    ...     "articles": [
    ...       {"id": 1, "name": "water", "price": 100},
    ...       {"id": 4, "name": "tea", "price": 1000},
    ...     ],
    ...     "carts": [
    ...       {
    ...         "id": 1,
    ...         "items": [
    ...           { "article_id": 1, "quantity": 6 },
    ...           { "article_id": 4, "quantity": 1 }
    ...         ]
    ...       },
    ...       {
    ...         "id": 3,
    ...         "items": []
    ...       }
    ...     ],
    ...     "delivery_fees": [
    ...         {
    ...             "eligible_transaction_volume": {
    ...                 "min_price": 0,
    ...                 "max_price": 1000
    ...             },
    ...             "price": 800
    ...         },
    ...         {
    ...             "eligible_transaction_volume": {
    ...                 "min_price": 1000,
    ...                 "max_price": 2000
    ...             },
    ...             "price": 400
    ...         },
    ...         {
    ...             "eligible_transaction_volume": {
    ...                 "min_price": 2000,
    ...                 "max_price": None
    ...             },
    ...             "price": 0
    ...         },
    ...     ],
    ...     "discounts": [
    ...         {"article_id": 2, "type": "amount", "value": 25},
    ...         {"article_id": 5, "type": "percentage", "value": 30},
    ...     ],
    ... }

    >>> print(price({}))
    {'carts': []}

    >>> print(price({"articles": [], carts: []}))
    {'carts': []}

    >>> print(price({
    ...     "articles": [
    ...         { "id": 10, "name": "tea", "price": 100 }
    ...         { "id": 20, "name": "tea", "price": 200 }
    ...         { "id": 40, "name": "tea", "price": 400 }
    ...     ],
    ...     "carts": [
    ...         {"id": 1, items: [
    ...             { "article_id": 10, "quantity": 2 },
    ...             { "article_id": 20, "quantity": 1 },
    ...             { "article_id": 30, "quantity": 1 },
    ...         ]}
    ...     ],
    ...     "delivery_fees": [
    ...         {
    ...             "eligible_transaction_volume": {
    ...                 "min_price": 0,
    ...                 "max_price": 1000
    ...             },
    ...             "price": 800
    ...         },
    ...         {
    ...             "eligible_transaction_volume": {
    ...                 "min_price": 1000,
    ...                 "max_price": 2000
    ...             },
    ...             "price": 400
    ...         },
    ...         {
    ...             "eligible_transaction_volume": {
    ...                 "min_price": 2000,
    ...                 "max_price": None
    ...             },
    ...             "price": 0
    ...         },
    ...     ],
    ...     "discounts": [
    ...         {"article_id": 20, "type": "amount", "value": 20},
    ...         {"article_id": 30, "type": "percentage", "value": 10},
    ...     ],

    ... }))
    {'carts': [{'id': 1, 'total': 1540}, ]}

    '''

    if not data:
        return {'carts': []}

    params = itemgetter('type', 'value')  # discount params
    article_id = itemgetter('article_id')

    try:
        articles = {article['id']: article for article in data["articles"]}
        carts = iter(data["carts"])
        discounts = {
            article_id(discount): discount_as_func(*params(discount))
            for discount in iter(data['discounts'])
        }
        fees_data = data['delivery_fees']
    except KeyError:
        raise ValueError('Invalid input data {}. \n'.format(data))
    except TypeError:
        raise ValueError(
            'Invalid input value for key "carts". Expected Iterable')
    else:
        cost_func = level2.fee_data_to_cost_table(fees_data)
        return {'carts': [
            level2.plus_fees(cart_price(cart, articles, discounts), cost_func)
            for cart in carts
        ]}
