'''
This is simple cart pricing module
'''


def cart_price(cart: dict, articles: dict, discounts: dict) -> dict:
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


def discount(article_price, discount_type, discount_value):
    if discount_type == "amount":
        return article_price - discount_value
    elif discount_type == "percentage":
        return (100 - discount_value) * article_price / 100
