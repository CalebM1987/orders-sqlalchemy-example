from flask import Flask
from flask_cors import CORS
from .blueprints.orders import orders_blueprint

app = Flask(__name__)
cors = CORS(app)

# register orders blueprint to add all orders endpoints
app.register_blueprint(orders_blueprint)