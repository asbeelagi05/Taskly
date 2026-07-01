from functools import wraps
from flask_login import current_user
from flask import abort


def customer_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if current_user.role != "customer":
            abort(403)

        return func(*args, **kwargs)

    return wrapper


def labour_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        if current_user.role != "labour":
            abort(403)

        return func(*args, **kwargs)

    return wrapper