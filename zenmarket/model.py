'''
This module is devised to describe input data using colander schema.
That is supposed to ease data validation and streamline algorithms.
'''

from colander import SchemaNode, Int, String, SequenceSchema, MappingSchema


class Article(MappingSchema):
    '''
    {"id": 1, "name": "water", "price": 100}
    '''
    article_id = SchemaNode(Int(), name='id')
    name = SchemaNode(String())
    price = SchemaNode(Int())


class Articles(SequenceSchema):
    '''
    [
        {"id": 1, "name": "water", "price": 100},
        {"id": 2, "name": "honey", "price": 200},
    ]
    '''
    article = Article()


class CartItem(MappingSchema):
    '''
    {"article_id": 1, "quantity": 6}
    '''
    article_id = SchemaNode(Int())
    quantity = SchemaNode(Int())


class CartItems(SequenceSchema):
    '''
    [
        {"article_id": 1, "quantity": 6},
    ]
    '''
    cart_item = CartItem()


class Cart(MappingSchema):
    '''
    {
      "id": 1,
      "items": [
        { "article_id": 1, "quantity": 6 },
      ]
    },
    '''
    cart_id = SchemaNode(Int(), name='id')
    items = CartItems()


class Carts(SequenceSchema):
    '''
    [
        {
          "id": 1,
          "items": [
            { "article_id": 1, "quantity": 6 },
            { "article_id": 2, "quantity": 2 },
            { "article_id": 4, "quantity": 1 }
          ]
        },
    ]
    '''
    cart = Cart()


class L1InputDataDesc(MappingSchema):
    '''
    {
        "articles": [
            {"id": 1, "name": "water", "price": 100},
            {"id": 2, "name": "honey", "price": 200},
        ],
        "carts": [
            {
                "id": 1,
                "items": [
                    {"article_id": 1, "quantity": 6},
                ]
            },
            {
                "id": 2,
                "items": [
                    {"article_id": 2, "quantity": 1},
                ]
            },
            {
                "id": 3,
                "items": []
            }
        ],
    }

    '''
    articles = Articles()
    carts = Carts()


class CartTotal(MappingSchema):
    '''
    {'id': <cart_id>, 'total': <cart_total>}
    '''
    cart_id = SchemaNode(Int(), name='id')
    total = SchemaNode(Int())


class CartTotals(SequenceSchema):
    '''
    [
        {'id': <cart_id>, 'total': <cart_total>},
    ]
    '''
    carts = CartTotal()


class ResponseDesc(MappingSchema):
    '''
    {'carts': [
        {'id': <cart_id>, 'total': <cart_total>},

    ]}
    '''
    carts = CartTotals(missing=[])
