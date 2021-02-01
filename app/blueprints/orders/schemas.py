from marshmallow import Schema, EXCLUDE, fields, post_load
import datetime
from .models import *

class SerializableDateTime(fields.DateTime):
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, datetime.datetime):
            return value
        return super()._deserialize(value, attr, data)

class OrderItemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    OrderHeaderID = fields.Integer(description='order id', dump_only=True)
    ProductName = fields.String(description='the product name')
    Quantity = fields.Integer(description='the item quantity', missing=1)
    UnitPrice = fields.Float(description='the price for the item', missing=0)
    ItemTotal = fields.Float(description='the total base cost (unit cost * quantity)', missing=0, dump_only=True)

    @post_load
    def make_object(self, data, **kwargs):
        return OrderItem(**data)

class OrderHeaderSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    OrderHeaderID = fields.Integer(description='the order id', dump_only=True)
    CustomerID = fields.Integer(description='the customer id', dump_only=True)
    CreationDate = SerializableDateTime(description='the order date')
    Product = fields.String(description='the product label')
    ItemTotal = fields.Float(description='the total base cost for order', dump_only=True)
    TaxTotal = fields.Float(description='total tax for this order', dump_only=True)
    ShippingTotal = fields.Float(description='the shipping total', missing=0)
    GrandTotal = fields.Float(description='the grand total for order, includes tax and shipping costs', dump_only=True)

    Items = fields.List(fields.Nested(OrderItemSchema), attribute='orderItems', many=True, missing=[])

    @post_load
    def make_object(self, data, **kwargs):
        order = OrderHeader(**data)

        # create items
        for itemAsJson in data.get('Items', []):
            item = OrderItemSchema().load(itemAsJson)

            # append child order item
            order.orderItems.append(item)

        return order


class CustomerSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    CustomerID = fields.Integer(description='the customer id', dump_only=True)
    FirstName = fields.String(description='customer first name')
    LastName = fields.String(description='customer last name')
    FullName = fields.String(description='customer full name', dump_only=True)
    ShipToState = fields.String(description='state for shipping')

    Orders = fields.List(fields.Nested(OrderHeaderSchema), many=True, missing=[])

    @post_load
    def make_object(self, data, **kwargs):
        customer = Customer(**{k: data.get(k) for k in data.keys() if k != 'Orders'})

        return customer

class BaseResourceMutationSchema(Schema):
    id = fields.Integer(description='the resource id', default=1)
    status = fields.String(description='the operation status (success|error)', default="success")

class CreateResourceSchema(BaseResourceMutationSchema):
    message = fields.String(description='the create message', default="Successfully Created Resource")

class UpdateResourceSchema(BaseResourceMutationSchema):
    message = fields.String(description='the update message', default="Successfully Updated Resource")

class DeleteResourceSchema(BaseResourceMutationSchema):
    message = fields.String(description='the delete message', default="Successfully Deleted Resource")