
'''
Level 2 costing: Compute delivery fees
'''
import numbers
from typing import List, Tuple, NewType
import bisect

import colander

from zenmarket.algo import level1
from zenmarket.model import L1InputDataDesc, DeliveryFees, ResponseDesc

# pylint: disable=C0103

Price = NewType('Price', numbers.Number)
PriceRange = Tuple[List[Price], List[Price]]


class PriceRangeError(Exception):
    '''
    Exception raised when min_price >= max_price
    '''
    pass


class InterpolationError(Exception):
    '''
    Exception raised during interpolation
    '''
    pass


def interpolate_fees(aprice: Price, cost_function: PriceRange):
    '''
    :returns
    '''
    x, fx = cost_function
    try:
        value = fx[bisect.bisect_right(x, aprice)]
    except:
        raise InterpolationError('Unknown error')
    else:
        return value


def fee_data_to_cost_table(fee_data: List[dict]) -> PriceRange:
    '''
    [
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
    ]

    :returns [
        [1000, 2000, float('+Inf')],
        [800, 400, 0],
    ]
    '''
    def iter_price_info():
        '''
        Generator that yields price info
        '''
        for info in fee_data:
            price_range = info['eligible_transaction_volume']
            min_price = price_range['min_price']
            max_price = price_range['max_price'] or float('+Inf')
            cost = info['price']
            if min_price < max_price:
                yield min_price, max_price, cost
            else:
                raise PriceRangeError(
                    'Bad price range (min_price, max_price): {}'
                    .format((min_price, max_price)))

    sorted_data = sorted(
        [(max_price, cost) for _, max_price, cost in iter_price_info()],
        key=lambda z: z[0])
    prices = [x for x, _ in sorted_data]
    fees = [y for _, y in sorted_data]
    return prices, fees


def price(data: dict) -> dict:
    '''
    :returns {'carts': [{'id': <cart_id>, 'total': <cart_price>}]}
    '''
    try:
        delivery_fees = DeliveryFees().deserialize(data.pop('delivery_fees'))
        result = level1.price(L1InputDataDesc().deserialize(data))
    except colander.Invalid as exc:
        raise level1.BadDataFormat(exc.msg)
    else:
        cost_function = fee_data_to_cost_table(delivery_fees)
        return ResponseDesc().serialize({'carts': [
            plus_fees(cart, cost_function)
            for cart in result['carts']
        ]})


def plus_fees(cart: dict, cost_function: PriceRange):
    '''
    :returns: price + fees for a given
    '''
    total = cart['total']
    return {
        'id': cart['id'],
        'total': total + interpolate_fees(total, cost_function)
    }
