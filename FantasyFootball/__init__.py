"""
The flask application package.
"""

from functools import wraps
from flask import Flask, session, request, redirect, url_for

app = Flask(__name__)


# decorator to ensure login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('showLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

import FantasyFootball.views