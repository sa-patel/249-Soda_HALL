"""customObjects.py
Various classes for this project.
"""

class Segment:
    x0 = 0
    y0 = 0
    xf = 1
    yf = 1
    def segment_angle(self):
        """Calculate and return the angle of the vector from x0,y0 to xf, yf."""
        pass # TODO

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