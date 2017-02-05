'''
This is simple cart pricing module
'''
import colander
from zenmarket.model import L1InputDataDesc, ResponseDesc


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


def cart_price(cart: dict, articles: dict) -> dict:
    '''
    :param cart dict: {'id': <id>, 'items': []}
    :param articles dict: {<id>: {'id': <id>, 'price': <price>, ...}, ...}
    :returns {id: cart['id'], total: dotproduct(<prices>, <quantities>)}

    >>> cart_price()
    '''

    def iter_cart_items_prices(items, articles):
        '''
        Generator that yields for each cart item (<cart_id>, <cart_item_price>)
        '''
        for item in items:
            article_id = item['article_id']
            quantity = item['quantity']
            try:
                item_price = articles[article_id]['price']
            except KeyError:
                raise UndefinedArticleReference(
                    'Article(id={}) is not defined'.format(article_id))
            else:
                yield quantity, item_price

    items = cart['items']
    cart_id = cart['id']
    if not items:
        return {'id': cart_id, 'total': 0}

    return {
        'id': cart_id,
        'total': sum(
            quantity * price
            for quantity, price in iter_cart_items_prices(items, articles))
    }


def price(data: dict) -> dict:
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

    >>> print(price({}))
    {'carts': []}

    >>> print(price({"articles": [], carts: []}))
    {'carts': []}

    >>> print(price(
    ...     {
    ...         "articles": [
    ...             { "id": 4, "name": "tea", "price": 1000 }
    ...         ],
    ...         "carts": [
    ...             {"id": 10, items: [{ "article_id": 4, "quantity": 1 }]}
    ...         ]
    ...     }
    ... ))
    {'carts': [
        {'id': 10, 'total': 1000},
    ]}

    '''

    if not data:
        return {'carts': []}

    schema = L1InputDataDesc()
    response_schema = ResponseDesc()
    try:
        data = schema.deserialize(data)
    except colander.Invalid as exc:
        raise BadDataFormat(exc.msg)
    else:
        articles = {article['id']: article for article in data["articles"]}
        carts = data["carts"]
        return response_schema.deserialize({'carts': [
            cart_price(cart, articles)
            for cart in carts
        ]})
