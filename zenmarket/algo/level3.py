'''
This is simple cart pricing module
'''
from operator import itemgetter
from functools import partial
from typing import Callable, NewType

from zenmarket.algo import level2, level1
from zenmarket import model
import colander

# pylint: disable=too-few-public-methods


class L3CartProcessor(level1.L1CartProcessor):
    '''
    '''
    input_validator = model.L3InputDataDesc()

    class Discount:
        '''
        Callable that applies a discount to a price
        '''

        def __init__(self, typ, value):
            if typ == 'percentage' and value > 100:
                raise level1.BadDataFormat('discount.percentage > 100')

            switch = {
                "amount": lambda aprice: aprice - value,
                "percentage": lambda aprice: aprice * (100 - value) // 100
            }
            self.function = switch.get(typ, lambda aprice: aprice)

        def __call__(self, aprice):
            '''
            Applies a discount to a price
            '''
            return self.function(aprice)

    def __init__(self, data: dict):
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

        >>> print(L3CartProcessor({}).price())
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
        params = itemgetter('type', 'value')  # discount params
        article_id = itemgetter('article_id')
        try:
            self.input_validator.deserialize(data)
        except colander.Invalid as exc:
            raise level1.BadDataFormat(exc.msg)
        else:
            discounts = {
                article_id(discount): self.Discount(*params(discount))
                for discount in data.pop('discounts')
            }
            discounted_price = partial(
                lambda art: discounts.get(art.id, lambda _: _)(art.price))

            self.articles = {
                art.id: art._replace(price=discounted_price(art))
                for art in (
                    self.Article(**article) for article in data['articles'])
            }
            self.carts = [
                self.Cart(
                    id=cart_data['id'],
                    items=tuple(self.build_cart_items(cart_data)))
                for cart_data in data['carts']
            ]
            self.l2_processor = level2.L2CartProcessor(data)

    def price(self):
        '''
        :returns carts prices
        '''
        resp = super(L3CartProcessor, self).price()
        fee_function = self.l2_processor.fee_function
        return self.output_validator.deserialize({'carts': [
            dict(
                id=cart['id'],
                total=cart['total'] + fee_function(cart['total']))
            for cart in resp['carts']
        ]})


def price(data: dict) -> dict:
    '''
    To keep old interface
    '''
    return L3CartProcessor(data).price()
