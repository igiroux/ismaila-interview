'''
This is simple cart pricing module
'''
from collections import namedtuple
import colander
from zenmarket import model

# pylint: disable=too-few-public-methods


class UndefinedArticleReference(Exception):
    '''
    Exception raised when a reference to article does not exist
    '''
    pass


class BadDataFormat(Exception):
    '''
    Exception raised when input data can't be deserialized
    '''
    pass


class L1CartProcessor:
    '''
    Compute cart object price

    :param data dict: {'articles': [...], 'carts': [...]}
    :returns {'carts': [{'id': <id>, 'total': <total>}, ...]}
    :raises BadDataFormat
    E.g.:

    >>> data = {
    ...   "articles": [
    ...     {"id": 1, "name": "water", "price": 100},
    ...     {"id": 4, "name": "tea", "price": 1000},
    ...   ],
    ...   "carts": [
    ...     {
    ...       "id": 1,
    ...       "items": [
    ...         { "article_id": 1, "quantity": 6 },
    ...         { "article_id": 4, "quantity": 1 }
    ...       ]
    ...     },
    ...     {
    ...       "id": 3,
    ...       "items": []
    ...     }
    ...   ]
    ... }

    >>> print(L1CartProcessor({}).price()) # KO raises BadDataFormat
    {'carts': []}
    >>> print(L1CartProcessor({"articles": [], carts: []}).price())
    {'carts': []}

    >>> print(L1CartProcessor(
    ...     {
    ...         "articles": [
    ...             { "id": 4, "name": "tea", "price": 1000 }
    ...         ],
    ...         "carts": [
    ...             {"id": 10, items: [{ "article_id": 4, "quantity": 1 }]}
    ...         ]
    ...     }
    ... ).price())
    {'carts': [
        {'id': 10, 'total': 1000},
    ]}
    '''

    input_validator = model.L1InputDataDesc()
    output_validator = model.ResponseDesc()

    class Article(namedtuple('Article', ['id', 'name', 'price'])):
        '''
        Data structure article
        '''
        pass

    class CartItem(namedtuple('CartItem', ['article', 'quantity'])):
        '''
        Data structure for cart item
        '''

        def price(self):
            '''
            :return cart item price
            '''
            return self.article.price * self.quantity

    class Cart(namedtuple('Cart', ['id', 'items'])):
        '''
        Data structure for a cart
        '''

        def total(self):
            '''
            :returns: Cart total price
            '''
            return sum(item.price() for item in self.items)

    def build_cart_items(self, cart_data):
        '''
        Generator that yields the proper cart object
        '''
        for item in cart_data['items']:
            article_id = item['article_id']
            quantity = item['quantity']
            try:
                article = self.articles[article_id]
            except KeyError:
                raise UndefinedArticleReference(
                    'Article(id={}) is not defined'.format(article_id))
            else:
                yield self.CartItem(article=article, quantity=quantity)

    def __init__(self, data: dict):
        '''
        L1CartProcess ctor
        '''
        try:
            data = self.input_validator.deserialize(data)
        except colander.Invalid as exc:
            raise BadDataFormat(exc.msg)
        else:
            self.articles = {
                article['id']: self.Article(**article)
                for article in data['articles']}

            self.carts = [
                self.Cart(
                    id=cart_data['id'],
                    items=tuple(self.build_cart_items(cart_data)))
                for cart_data in data['carts']
            ]

    def price(self):
        '''
        :returns carts prices
        '''
        return self.output_validator.deserialize({'carts': [
            {'id': cart.id, 'total': cart.total()}
            for cart in self.carts
        ]})


def price(data: dict):
    '''
    To keep old interface
    '''
    return L1CartProcessor(data).price()
