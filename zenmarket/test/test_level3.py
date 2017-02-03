'''
Level 3 pricing tests
'''
from zenmarket.algo.level3 import discount

def test_discount():
    assert discount(100, 'amount', 10) == 90
    assert discount(300, 'percentage', 10) == 270
