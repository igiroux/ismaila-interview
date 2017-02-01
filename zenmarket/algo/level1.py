'''
This is simple cart pricing module
'''


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
            try:
                item_price = articles[item['article_id']]['price']
                item_quantity = item['quantity']
            except KeyError:
                raise ValueError(
                    'Cart item price could not be found {}'.format(item))
            else:
                yield item_quantity, item_price

    try:
        items = cart['items']
        cart_id = cart['id']
    except KeyError:
        raise ValueError(
            'Wrong cart fmt %r. Expected {"id": <id>, "items": []}' % cart)
    else:
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

    try:
        articles = {article['id']: article for article in data["articles"]}
        carts = list(data["carts"])
    except KeyError:
        raise ValueError('Invalid input data {}. \n'.format(data))
    except TypeError:
        raise ValueError(
            'Invalid input value for key "carts". Expected Iterable')
    else:
        return {'carts': [
            cart_price(cart, articles)
            for cart in carts
        ]}
