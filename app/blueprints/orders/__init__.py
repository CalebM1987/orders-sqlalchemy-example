from flask_restx import Api
from .controller import orders_blueprint, namespaces

# create swagger api
orders_swagger_api = Api(
    orders_blueprint,
    title="Customer Orders API",
    description="API Methods for managing Customer Orders",
    doc="/orders/help" #/orders/help
)

# register all namespaces
for ns in namespaces:
    orders_swagger_api.add_namespace(ns)