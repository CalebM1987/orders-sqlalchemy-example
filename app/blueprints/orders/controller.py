import os
import flask_accepts
from flask import Blueprint, request
from flask_restx import Resource, Namespace
from .data import sample_data
from .models import *
from .schemas import *
from .utils import *

thisDir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(thisDir, 'data', 'Orders.db')

# create database session
session = create_session(f'sqlite:///{db_path}?check_same_thread=False', Base)

# create blueprint
orders_blueprint = Blueprint('orders_api', __name__)

# create naemspaces
orders_ns = Namespace('orders', 'Operations for managing orders', path='/orders')
items_ns = Namespace('items', 'Operations for managing order items', path='/items')
customers_ns = Namespace('customers', 'Operations for managing customers', path='/customers')
namespaces = [customers_ns, orders_ns, items_ns]

# create sample data function
def create_sample_data():
    # drop all tables to clean and recreate
    Base.metadata.drop_all(session.get_bind())
    Base.metadata.create_all(session.get_bind())

    # build data
    for customerAsJson in sample_data['customers']:
        customer = CustomerSchema().load(customerAsJson)

        # create orders
        for orderAsJson in customerAsJson.get('Orders', []):
            order = OrderHeaderSchema().load(orderAsJson)

            # append child order
            customer.orders.append(order)
   
        # add to database
        session.add(customer)
    session.commit()


# create sample data before first request
@orders_blueprint.before_app_first_request
def check_sample_data():
    orders = session.query(OrderHeader).all()
    if not orders:
        create_sample_data()
        

#***********************************************************************************************************##
#  ORDERS                                                                                                   ##
#***********************************************************************************************************##
@orders_ns.route('') # will already be /orders
class GetOrders(Resource):
    parser = orders_ns.parser()
    # add query uri args to limit records
    parser.add_argument('Product', type=str, help='product name to search for')
    parser.add_argument('CustomerID', type=int, help='a specific customer id to search for')

    @orders_ns.expect(parser)
    @flask_accepts.responds(schema=OrderHeaderSchema(many=True), api=orders_ns)
    def get(self):
        """ fetches all orders """
        res = session.query(OrderHeader)
        args = self.parser.parse_args()
        product = args.get('Product')
        customerId = args.get('CustomerID')
        if product:
            res = res.filter_by(Product=product)
        if customerId:
            res = res.filter_by(CustomerID=customerId)

        # marshmallow and flask_accepts will serialize to json automatically
        return res.all()


@orders_ns.route('/<int:id>')
class OrderHandler(Resource):

    @flask_accepts.responds(schema=OrderHeaderSchema, api=orders_ns)
    def get(self, id):
        """ fetch a specific order by id """
        order = session.query(OrderHeader).get(id)
        if not order:
            return dynamic_error(message=f'No Order found with ID: {id}')
        return order

    @flask_accepts.accepts(schema=OrderHeaderSchema, api=orders_ns)
    @flask_accepts.responds(schema=UpdateResourceSchema, api=orders_ns)
    def put(self, id):
        """ update an order """
        order = session.query(OrderHeader).get(id)
        if not order:
            return dynamic_error(message=f'No Order found with ID: {id}')
        payload = request.json
        for k,v in payload.items():
            setattr(order, k, v)
        session.commit()

        return success(message='Successfully Updated Order', id=id)

    @flask_accepts.responds(schema=DeleteResourceSchema, api=orders_ns)
    def delete(self, id):
        """ removes an order """
        order = session.query(OrderHeader).get(id)
        if not order:
            return dynamic_error(message=f'No Order found with ID: {id}')
        session.delete(order)
        session.commit()

        return success('Successfully Removed Order', id=id)

@orders_ns.route('/<int:id>/create-item')
class CreateItem(Resource):
    @flask_accepts.accepts(schema=OrderItemSchema, api=orders_ns)
    def post(self, id):
        """ creates an item for an order """
        order = session.query(OrderHeader).get(id)
        if not order:
            raise RuntimeError('Invalid Order ID')

        # create OrderItem from json payload
        payload = request.json
        item = OrderItem(**payload)

        # append child item to order and commit to db
        order.addItem(item)
        session.commit()

        return success(message='Successfully Created Order Item', id=item.OrderItemID)


@orders_ns.route('/recreate-database')
class CreateSampleData(Resource):
    @flask_accepts.responds(schema=CreateResourceSchema, api=orders_ns)
    def post(self):
        """ convenience option to clean and recreate sample database """
        create_sample_data()
        return success('Successfully Recreated Database')



#***********************************************************************************************************##
#  ITEMS                                                                                                   ##
#***********************************************************************************************************##
@items_ns.route('') # will already be /items
class GetItems(Resource):
    parser = items_ns.parser()
    # add query uri args to limit records
    parser.add_argument('Product', type=str, help='product name to search for')
    parser.add_argument('OrderHeaderID', type=int, help='a specific order id to search for')

    @items_ns.expect(parser)
    @flask_accepts.responds(schema=OrderItemSchema(many=True), api=items_ns)
    def get(self):
        """ fetches all items """
        res = session.query(OrderItem)
        args = self.parser.parse_args()
        product = args.get('ProductName')
        orderId = args.get('OrderHeaderID')
        if product:
            res = res.filter_by(Product=product)
        if orderId:
            res = res.filter_by(OrderHeaderID=orderId)

        # marshmallow and flask_accepts will serialize to json automatically
        return res.all()

@items_ns.route('/<int:id>')
class ItemHandler(Resource):
    def getItem(self, id):
        item = session.query(OrderItem).get(id)
        if item:
            return item
        raise RuntimeError('No Item Found')

    @flask_accepts.responds(schema=OrderItemSchema, api=items_ns)
    def get(self, id):
        """ fetch a specific item by id """
        return self.getItem(id)

    @flask_accepts.accepts(schema=OrderItemSchema, api=items_ns)
    @flask_accepts.responds(schema=UpdateResourceSchema, api=items_ns)
    def put(self, id):
        """ update an item """
        item = self.getItem(id)
        payload = request.json
        for k,v in payload.items():
            setattr(item, k, v)

        # now update parent
        item.updateItem()
        item.orderHeader.updateOrder()
        session.commit()

        return success(message='Successfully Updated Item', id=id)

    @flask_accepts.responds(schema=DeleteResourceSchema, api=items_ns)
    def delete(self, id):
        """ removes an item """
        item = self.getItem(id)
        order = item.orderHeader
        # remove from parent to trigger orm 
        order.removeItem(item)
        order.updateOrder()
        session.commit()

        return success('Successfully Removed Item', id=id)



#***********************************************************************************************************##
#  CUSTOMERS                                                                                                ##
#***********************************************************************************************************##
@customers_ns.route('') # will already be /customers
class GetCustomers(Resource):
    parser = customers_ns.parser()
    # add query uri args to limit records
    parser.add_argument('FirstName', type=str, help='customer first name')
    parser.add_argument('LastName', type=int, help='customer last name')

    @customers_ns.expect(parser)
    @flask_accepts.responds(schema=CustomerSchema(many=True, exclude=['Orders']), api=customers_ns)
    def get(self):
        """ fetches all customers """
        res = session.query(Customer)
        args = self.parser.parse_args()
        firstName = args.get('FirstName')
        lastName = args.get('LastName')
        if firstName:
            res = res.filter_by(FirstName=firstName)
        if lastName:
            res = res.filter_by(LastName=lastName)

        # marshmallow and flask_accepts will serialize to json automatically
        return res.all()

    @flask_accepts.accepts(schema=CustomerSchema(exclude=['Orders']), api=customers_ns)
    def post(self):
        """ create a new customer """
        payload = request.json
        customer = CustomerSchema(exclude=['Orders']).load(payload)
        session.add(customer)
        session.commit()
        return success(message='Successfully Added New Customer', id=customer.CustomerID)


@customers_ns.route('/<int:id>')
class CustomerHandler(Resource):

    @flask_accepts.responds(schema=CustomerSchema, api=customers_ns)
    def get(self, id):
        """ fetch a specific customer by id """
        customer = session.query(Customer).get(id)
        if not customer:
            return dynamic_error(message=f'No Customer found with ID: {id}')
        return customer

    @flask_accepts.accepts(schema=CustomerSchema, api=customers_ns)
    @flask_accepts.responds(schema=UpdateResourceSchema, api=customers_ns)
    def put(self, id):
        """ update a customer """
        customer = session.query(Customer).get(id)
        if not customer:
            return dynamic_error(message=f'No Customer found with ID: {id}')
        payload = request.json
        for k,v in payload.orders():
            setattr(customer, k, v)
        session.commit()

        return success(message='Successfully Updated Customer', id=id)

    @flask_accepts.responds(schema=DeleteResourceSchema, api=customers_ns)
    def delete(self, id):
        """ removes an customer """
        customer = session.query(Customer).get(id)
        if not customer:
            return dynamic_error(message=f'No Customer found with ID: {id}')
        session.delete(customer)
        session.commit()

        return success('Successfully Removed Customer', id=id)

@customers_ns.route('/<int:id>/orders')
class GetCustomerOrders(Resource):
    @flask_accepts.responds(schema=OrderHeaderSchema(many=True), api=customers_ns)
    def get(self, id):
        """ fetches orders for customer """
        customer = session.query(Customer).get(id)
        if not customer:
            return dynamic_error(message=f'Invalid Customer ID: {id}')
        return customer.orders


@customers_ns.route('/<int:id>/create-order')
class CreateItem(Resource):
    @flask_accepts.accepts(schema=OrderHeaderSchema, api=customers_ns)
    def post(self, id):
        """ creates an order for a customer """
        customer = session.query(Customer).get(id)
        if not customer:
            return dynamic_error(message=f'Invalid Customer ID: {id}')

        # create OrderHeader from json payload
        payload = request.json

        # get items and remove from initial payload
        items = payload.get('Items', [])
        if items:
            del payload['Items']

        # create order
        order = OrderHeaderSchema().load(**payload)
        session.commit()

        return success(message='Successfully Created Order', id=order.OrderHeaderID)