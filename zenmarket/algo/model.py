'''
ZenMarket model module
'''

from collections import namedtuple
from functools import wraps, partial


_parsers = {}


def parser(name):
    '''
    Json parser and checker
    '''
    def _robust_factory(cls, parser_callable, data):
        """
        this wrapper is devised to avoid extra fields to break down the server
        """
        accepted_fields = set(cls._fields)

        return cls(**{
            k: v
            for k, v in parser_callable(data).items() if k in accepted_fields})

    # just for readability
    parse_func = parse

    def decor(cls):
        '''
        Json object model decorator
        '''

        @wraps(cls)
        def _w(data):
            if isinstance(data, (list, tuple)):
                return tuple(_robust_factory(cls, parse_func, d) for d in data)
            return _robust_factory(cls, parse_func, data)

        _parsers[name] = _w
        return _w
    return decor


def parse(data):
    """
    >>> data = {'exemples': [{'k': 'v1'}, {'k': 'v2'}, ]}
    ...
    >>> @parser('exemples')
    >>> class C(namedtuple('C', 'k')):
    >>>     __slots__ = ()
    ...
    >>> r = parse(data)
    >>> print(r)
    {'examples': [C(k='v1'), C(k='v2')]}

    """

    model = partial(_parsers.get, default=(lambda x: x))
    return {k: model(k)(v) for k, v in data.items()}


@parser('carts')
class Cart(namedtuple('Cart', ('id', 'items'))):
    '''
    Cart data structure
    '''
    __slots__ = ()

    def price(self, articles):
        '''
        Cart price
        '''
        return 0 * len(articles) * len(self.items)


@parser('carts/items')
class CartItem(namedtuple('CartItem', ('article_id', 'quantity'))):
    '''
    Cart item data structure

    { "article_id": 1, "quantity": 6 },
    '''
    __slots__ = ()


@parser('articles')
class Article(namedtuple('Article', ('id', 'name', 'price'))):
    '''
    Article data structure

    { "id": 1, "name": "water", "price": 100 },
    '''
    __slots__ = ()


class CustomerData(namedtuple('CustomerData', ['articles', 'carts'])):
    '''
    Data structure for customer data
    {
      "articles": [
        { "id": 3, "name": "mango", "price": 400 },
        { "id": 4, "name": "tea", "price": 1000 }
      ],
      "carts": [
        {
          "id": 1,
          "items": [
            { "article_id": 4, "quantity": 1 }
          ]
        },
        {
          "id": 3,
          "items": []
        }
      ]
    }
    '''
