
'''
Level 2 costing: Compute delivery fees
'''
import numbers
from typing import List, Tuple, NewType
import bisect

from zenmarket.algo import level1

# pylint: disable=C0103

Price = NewType('Price', numbers.Number)
PriceRange = Tuple[List[Price], List[Price]]


class DeliveryFeeKeyError(KeyError):
    '''
    Exception raised when infortmation is missing
    '''
    pass


class DeliveryFeeValueError(ValueError):
    '''
    Exception raised when infortmation is missing
    '''
    pass


def interpolate_fees(price: Price, cost_function: PriceRange):
    '''
    :returns
    '''
    x, fx = cost_function
    return fx[bisect.bisect_right(x, price)]


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
            try:
                min_price = info['eligible_transaction_volume']['min_price']
                max_price = info['eligible_transaction_volume']['max_price']
                cost = info['price']
                min_price, max_price, cost = [
                    float('+Inf') if x is None else int(x)
                    for x in (min_price, max_price, cost)
                ]
            except KeyError:
                raise DeliveryFeeKeyError(
                    'Incomplete fee info: {}'.format(info))
            except ValueError:
                raise DeliveryFeeValueError(
                    'Price value error: {}'.format(info))
            else:
                yield min_price, max_price, cost
    prices = [
        [max_price, float('+Inf')][max_price is None]
        for _, max_price, _ in iter_price_info()
    ]
    fees = [cost for _, _, cost in iter_price_info()]
    sorted_data = sorted(zip(prices, fees), key=lambda z: z[0])
    prices = [x for x, _ in sorted_data]
    fees = [y for _, y in sorted_data]
    return prices, fees


def price(data: dict) -> dict:
    '''
    :returns {'carts': [{'id': <cart_id>, 'total': <cart_price>}]}
    '''
    result = level1.price(data)
    cost_function = fee_data_to_cost_table(data['delivery_fees'])
    return {'carts': [
        plus_fees(cart, cost_function)
        for cart in result['carts']
    ]}


def plus_fees(cart: dict, cost_function: PriceRange):
    '''
    :returns: price + fees for a given
    '''
    total = cart['total']
    return {
        'id': cart['id'],
        'total': total + interpolate_fees(total, cost_function)
    }
