
'''
Level 2 costing: Compute delivery fees
'''
import numbers
from typing import List, Tuple, NewType
import bisect
from collections import namedtuple

import colander

from zenmarket.algo import level1
from zenmarket.model import (
    L1InputDataDesc, DeliveryFees, ResponseDesc, L2InputDataDesc)

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


class L2CartProcessor:
    '''
    '''
    input_validator = L2InputDataDesc()

    class DeliveryFeeFunction(namedtuple('CostFunction', ['x', 'y'])):
        '''
        '''

        def __call__(self, aprice):
            '''
            :returns
            '''
            try:
                value = self.y[bisect.bisect_right(self.x, aprice)]
            except:
                raise InterpolationError('Unknown error')
            else:
                return value

        @classmethod
        def from_list(cls, fee_data: List[dict]):
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

            :returns cls(
                x=[1000, 2000, float('+Inf')],
                y=[800, 400, 0],
            )
            '''
            def gen_prices():
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
                [(max_price, cost) for _, max_price, cost in gen_prices()],
                key=lambda z: z[0]
            )
            prices = [x for x, _ in sorted_data]
            fees = [y for _, y in sorted_data]
            return cls(x=prices, y=fees)

    def __init__(self, data: dict) -> None:
        try:
            self.input_validator.deserialize(data)
            fee_data = DeliveryFees().deserialize(data.pop("delivery_fees"))
        except colander.Invalid as exc:
            raise level1.BadDataFormat(exc.msg)
        else:
            self.l1_processor = level1.L1CartProcessor(data)
            self.fee_function = self.DeliveryFeeFunction.from_list(fee_data)

    def price(self):
        '''
        Computes carts prices including delivery fees
        '''
        resp = self.l1_processor.price()
        output_validator = self.l1_processor.output_validator
        return output_validator.deserialize({'carts': [
            dict(
                id=cart['id'],
                total=cart['total'] + self.fee_function(cart['total']))
            for cart in resp['carts']
        ]})


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
    try:
        fee_data = DeliveryFees().deserialize(fee_data)
    except colander.Invalid as exc:
        raise level1.BadDataFormat(exc.msg)
    else:
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
    return L2CartProcessor(data).price()


def plus_fees(cart: dict, cost_function: PriceRange):
    '''
    :returns: price + fees for a given
    '''
    total = cart['total']
    return {
        'id': cart['id'],
        'total': total + interpolate_fees(total, cost_function)
    }
