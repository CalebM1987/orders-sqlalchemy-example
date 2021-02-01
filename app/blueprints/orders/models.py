# we can use a module called sqlalchemy to act as our ORM
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from typing import List, Dict
import datetime

# create context
Base = declarative_base()

TAX_RATE = 0.075
 
# create classes and inherit from our declarative base context
class Customer(Base):
    __tablename__ = 'Customer'
    # make sure we set our PK, setting autoincrement to True will ensure future records increment properly
    CustomerID = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String(50))
    LastName = Column(String(50))
    ShipToState = Column(String(2))
    
    # reference OrderHeader relationship
    # also can set cascade to remove all child orders if this is deleted
    orders = relationship('OrderHeader', back_populates='customer', cascade='all, delete-orphan')

    @property
    def FullName(self):
        return f'{self.FirstName} {self.LastName}'
    
class OrderItem(Base):
    __tablename__ = 'OrderItem'
    OrderItemID = Column(Integer, Sequence('OrderItem_aid_seq', start=100, increment=1), primary_key=True)
    # reference foreign keys
    OrderHeaderID = Column(Integer, ForeignKey('OrderHeader.OrderHeaderID'))
    ProductName = Column(String(100))
    Quantity = Column(Integer, default=1)
    UnitPrice = Column(Float, default=0)
    ItemTotal = Column(Float, default=0)

    @property
    def _itemTotal(self):
        return self.UnitPrice * self.Quantity

    def updateItem(self):
        self.ItemTotal = self._itemTotal
    
    # reference parent OrderHeader
    orderHeader = relationship('OrderHeader', back_populates='orderItems')


# OrderHeader ORM object
class OrderHeader(Base):
    __tablename__ = 'OrderHeader'
    # set PK 
    OrderHeaderID = Column(Integer, primary_key=True, autoincrement=True)
    # create a foreign key reference to our Customer Table
    CustomerID = Column(Integer, ForeignKey('Customer.CustomerID'))
    Product = Column(String(100))
    # default creation date to UTC time at creation
    CreationDate = Column(DateTime, default=datetime.datetime.utcnow())
    ItemTotal = Column(Float, default=0)
    TaxTotal = Column(Float, default=0)
    ShippingTotal = Column(Float, default=0)
    GrandTotal = Column(Float, default=0)

    @property
    def _orderItemsTotal(self):
        # loop through orderItems to compute the grand total
        return sum([item._itemTotal for item in self.orderItems])

    @property
    def _taxTotal(self):
        return (self._orderItemsTotal + self.ShippingTotal) * TAX_RATE 

    # computed property for grand total
    @property
    def _grandTotal(self):
        return self._orderItemsTotal + self.ShippingTotal + self.TaxTotal

    def updateOrder(self):
        self.ItemTotal = self._orderItemsTotal
        self.TaxTotal = self._taxTotal
        self.GrandTotal = self._grandTotal

    def addItem(self, item: OrderItem):
        item.updateItem()
        self.orderItems.append(item)
        self.updateOrder()

    def removeItem(self, item: OrderItem):
        print('removing item? ', item)
        try:
            self.orderItems.remove(item)
        except Exception as e:
            self.updateOrder()

    def __iter__(self):
        for item in self.orderItems:
            yield item

    def __repr__(self):
        return f'<Order ID {self.OrderHeaderID}: Product "{self.Product}", ItemTotal: ${self.ItemTotal:.2f}, ShippingTotal: ${self.ShippingTotal:.2f}, TaxTotal: ${self.TaxTotal:.2f}, Grand Total: ${self.GrandTotal:.2f} >'

    def __str__(self):
        return repr(self)

    def __len__(self):
        return len(self.orderItems)
    

    # create relationship to find parent Customer object
    # can also add a back_populates to make reference to orders
    # from the Customer table
    customer = relationship('Customer', back_populates='orders')
    
    # create relationship to child OrderItems, set cascade to remove child order items when order is deleted
    orderItems = relationship('OrderItem', back_populates='orderHeader', cascade='all, delete-orphan')


# ORM level triggers, calculate ItemTotal before insert and update based on values
@event.listens_for(OrderItem, 'before_insert')
def update_item(mapper, connection, item):
    item.updateItem()

@event.listens_for(OrderHeader, 'before_insert')
def grand_total(mapper, connection, order):
    order.updateOrder()

