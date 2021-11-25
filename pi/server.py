"""server.py
Flask server for processing customer orders.

Running:
pip3 install flask
export FLASK_APP=server
flask run
"""

from flask import Flask, render_template, request
from orderScheduler import OrderScheduler

scheduler = OrderScheduler()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/place-order", methods=["GET"])
def place_order():
    customer = request.form['name']
    order = request.form['order']
    table = request.form['table']
    priority = 0 # TODO: lookup priorities by name or login paramter
    scheduler.create(customer, table, order, priority)
