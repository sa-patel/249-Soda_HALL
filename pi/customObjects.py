"""customObjects.py
Various classes for this project.
"""
from math import atan2
from enum import Enum

class Segment:
    def __init__(self, x0, y0, xf, yf):
        self.x0 = x0
        self.y0 = y0
        self.xf = xf
        self.yf = yf
    def __str__(self):
        return "({}, {}) -> ({}, {})".format(self.x0, self.y0, self.xf, self.yf)
    def segment_angle(self):
        """Calculate and return the angle of the vector from x0,y0 to xf, yf.
        Angle 0 is up. Positive values go clockwise and negative values go 
        counterclockwise.
        """
        return atan2(self.xf - self.x0, self.yf - self.y0)
    def length_squared(self):
        return (self.xf-self.x0)**2 + (self.yf-self.y0)**2

class Queue:
    data = []
    head = 0
    tail = 0
    size = 0
    def enqueue(self, item):
        self.data.append(item)
        self.head += 1
        self.size += 1
    
    def dequeue(self):
        if self.tail < self.head:
            result = self.data[self.tail]
            self.tail += 1
            self.size -= 1
            return result
        
        # List is empty.
        return None
    
    def remove_queue_item(self): 
        pass

class Order:
    def __init__(self, name, table, priority, order, order_id):
        self.name = name
        self.table = table
        self.priority = priority
        self.order = order
        self.order_id = order_id

class RobotStatus(Enum):
    IDLE = 0
    RETURNING = 1 # Going to the base station to wait for next order
    DELIVERING_ORDER = 2 # Bringing order to customer
    LOADING_UNLOADING = 3 # Order is being loaded onto or unloaded from robot
    PLAN_PATH_TO_BASE = 4
    PLAN_PATH_TO_TABLE = 5

class Waypoint:
    type = None # "PREDEFINED" or "XY"
    value = None
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __str__(self):
        return "{} {};".format(self.type, self.value)