"""customObjects.py
Various classes for this project.
"""
from math import atan2
from enum import Enum

class Segment:
    x0 = 0
    y0 = 0
    xf = 1
    yf = 1
    def __init__(self, x0, y0, xf, yf):
        self.x0 = x0
        self.y0 = y0
        self.xf = xf
        self.yf = yf
    def segment_angle(self):
        """Calculate and return the angle of the vector from x0,y0 to xf, yf.
        Angle 0 is up. Positive values go clockwise and negative values go 
        counterclockwise.
        """
        return atan2(self.xf - self.x0, self.yf - self.y0)

class Queue:
    data = []
    head = 0
    tail = 0
    def enqueue(self, item):
        self.data.append(item)
        self.head += 1
    
    def dequeue(self):
        # print("tail head", self.tail, self.head)
        if self.tail < self.head:
            result = self.data[self.tail]
            self.tail += 1
            return result
        
        # List is empty.
        return None

class Order:
    def __init__(self, name, table, priority, order, order_id):
        self.name = name
        self.table = table
        self.priority = priority
        self.order = order
        self.order_id = order_id

class RobotStatus(Enum):
    IDLE = 0
    GETTING_ORDER = 1 # Going to the base station to pick up the order
    DELIVERING_ORDER = 2 # Bringing order to customer
    LOADING_UNLOADING = 3 # Order is being loaded onto or unloaded from robot
