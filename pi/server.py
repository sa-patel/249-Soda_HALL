"""server.py
Flask server for processing customer orders.

Installing flask:
pip3 install flask
"""

from flask import Flask, render_template, request
from orderScheduler import OrderScheduler

scheduler = None

x = None

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/place-order", methods=["GET"])
def place_order():
    customer = request.args.get('name')
    order = request.args.get('order')
    table = request.args.get('table-num')
    print(customer, order, table)
    priority = 0 # TODO: lookup priorities by name or login paramter
    # global scheduler
    scheduler.create(customer, table, order, priority)
    return "order placed"

def start(sched):
    global scheduler
    scheduler = sched
    app.run(host = "0.0.0.0", use_reloader = False)
    