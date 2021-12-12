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

    def search_item_queue(self,table):
        iter = self.tail
        while iter != self.head:
            if self.data[iter].table == table: 
                order_return = self.remove_item_queue(iter)
                return order_return
            iter += 1
        return None

    def search_items_queue(self,table,capacity):
        iter = self.tail
        items = []
        while iter != self.head and len(items) < capacity:
            if self.data[iter].table == table: 
                order_return = self.remove_item_queue(iter)
                items.append(order_return)
                iter -= 1
            iter += 1
        return items
    
    def remove_item_queue(self,index_table):
        self.head -=1
        self.size -=1
        return self.data.pop(index_table)

    def print_queue(self):
        iter = self.tail
        print("Tail ",end="")
        while iter != self.head:
            print(" -> {",self.data[iter].order, "for", self.data[iter].name,"on Table", self.data[iter].table,"}",end="")
            iter += 1
        print("\n")

class Order:
    def __init__(self, name, seat, table, priority, order, order_id):
        self.name = name
        self.seat = seat
        self.table = table
        self.priority = priority
        self.order = order
        self.order_id = order_id

class RobotStatus(Enum):
    DELIVERYING = 1 # Bringing order to customer
    UNLOADING = 2 # Order is being loaded onto or unloaded from robot
    LOADING = 3
    RETURNING = 4 # Nothing on tray, going back to the base station

class Waypoint:
    def __init__(self, ident, coords):
        self.ident = ident
        self.coords = coords
        self.lock_holder = None

    def try_lock(self, robot_id):
        if self.lock_holder is None:
            self.lock_holder = robot_id
            return True
        else:
            return False

    def __repr__(self):
        return "Waypoint {}: coords={}; lock_holder={}".format(self.ident, \
            self.coords, self.lock_holder)