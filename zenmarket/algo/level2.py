
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


def delivery_fees(price: Price, cost_function: PriceRange):
    '''
    :returns
    '''
    x, fx = cost_function
    return price + fx[bisect.bisect_right(x, price)]


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
    return prices, fees


def price_plus_fees(data: dict) -> dict:
    '''
    '''
    result = level1.price(data)
    cost_function = fee_data_to_cost_table(data["delivery_fees"])
    for cart in result['carts']:
        cart['total'] = delivery_fees(cart['total'], cost_function)
    return result
