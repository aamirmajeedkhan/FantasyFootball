"""
The flask application package.
"""
import os
from flask import Flask

app = Flask(__name__)

import FantasyFootball.views