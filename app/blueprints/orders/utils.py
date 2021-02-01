from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import HTTPException
from flask import jsonify

def create_session(conn_str, Base):
    """ creates a database session

    Args:
        conn_str (str): the connection string
        Base (declarative_base): the sqlalchemy declarative_base
    """
    engine = create_engine(conn_str)

    # create all tables
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    return scoped_session(sessionmaker(bind=engine))


def success(message='success', **kwargs):
    """ returns a Response() object as JSON
    :param msg: message to send
    :param kwargs: additional key word arguments to add to json response
    :return: Response() object as JSON
    """
    kwargs['message'] = message
    kwargs['status'] = 'success'
    return jsonify(kwargs)

def json_exception_handler(error):
    """ Returns an HTTPException Object into JSON Response
    :param error: error to convert to JSON response
    :return: flask.Response() object
    """
    response = jsonify({
        'status': 'error',
        'details': {
            'code': error.code,
            'name': error.description,
            'message': error.message
        }
    })

    response.status_code = error.code
    return response

def dynamic_error(**kwargs):
    """ creates a dynamic error defined at runtime
    :param **kwargs: keyword arguments for custom error name, code, description, and message
    """
    defaults = {
        'code': 400,
        'status': 'error',
        'description': 'Runtime Error',
        'message': 'A runtime error has occured'
    }
    defaults.update(kwargs)
    
    # create HTTPException Subclass Error dynamically with type()
    errName = kwargs.get('name', 'FlaskRuntimeError')
    de = type(errName, (HTTPException,), defaults)
    return json_exception_handler(de)