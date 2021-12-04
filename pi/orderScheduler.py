"""orderScheduler.py
Implements scheduling algorithm to receive and schedule customer orders
"""

# Project modules
from customObjects import Queue, Order

class OrderScheduler:
    SUCCESS = 0
    ID_NOT_FOUND = 1
    queue = Queue()

    def __init__(self, num_kobukis, kobuki_state):
        self.next_id = 0
        self.num_kobukis = num_kobukis
        self.kobuki_state = kobuki_state

    def allocate(self):
        orders = [None, None]
        for i in range(len(self.kobuki_state)):
            state, order_id = self.kobuki_state[i]
            if state == RobotStatus.IDLE:
                # Assign next order to robot
                order = self.get_next_order()
                if order is not None:
                    self.kobuki_state[i] = (RobotStatus.GETTING_ORDER, order)
                    orders[i] = order
            elif state == RobotStatus.GETTING_ORDER:
                # TODO option to preempt if a higher priority order arrives.
                pass
            else:
                # The scheduler does not operate on other states.
                pass
        return orders

    def create(self, customer, table, order, priority):
        """Create an order with the given paramters. Add to queue.
        Returns SUCCESS, order_id if the order was added, where order_id is a
        unique order identifier.
        """
        id = self.next_id
        self.next_id += 1
        order = Order(customer, table, priority, order, id)
        self.queue.enqueue(order)
        return id

    def cancel(order_id):
        """Cancel the order with the given order_id.
        Returns SUCCESS on success, ID_NOT_FOUND if order_id is not found in the
        task list.
        """
        return self.SUCCESS
    
    def get_next_order(self):
        """Gets the next order to fulfill."""
        return self.queue.dequeue()
