"""orderScheduler.py
Implements scheduling algorithm to receive and schedule customer orders
"""

# Project modules
from customObjects import Queue, Order, RobotStatus

class OrderScheduler:
    SUCCESS = 0
    ID_NOT_FOUND = 1
    queue = Queue()
    MAX_DRINK_CAPACITY = 3

    def __init__(self, num_kobukis, kobuki_state):
        self.next_id = 0
        self.num_kobukis = num_kobukis
        self.kobuki_state = kobuki_state

    def allocate(self):
        for i in range(len(self.kobuki_state)):
            state, k_order, drink_num = self.kobuki_state[i]
            if state == RobotStatus.IDLE:
                # Assign next order to robot
                order = self.get_next_order()
                if order is not None and drink_num < self.MAX_DRINK_CAPACITY: 
                    cur_table = order.table
                    drink_num += 1
                    k_order.append(order)

                same_table_orders = self.queue.search_items_queue(cur_table,self.MAX_DRINK_CAPACITY - drink_num)
                for item in same_table_orders:
                    drink_num += 1
                    k_order.append(item)
                       
                self.kobuki_state[i] = (RobotStatus.DELIVERING_ORDER, k_order, drink_num)
            elif state == RobotStatus.DELIVERING_ORDER or state == RobotStatus.PLAN_PATH_TO_TABLE:
                # TODO option to preempt if a higher priority order arrives. 
                
                pass
            elif state == RobotStatus.DELIVERED_DRINKS:
                # The scheduler does not operate on other states.
                pass
            else:
                # The scheduler does not operate on other states.
                pass
                
        return None

    def create(self, customer, table, order, priority):
        """Create an order with the given paramters. Add to queue.
        Returns SUCCESS, order_id if the order was added, where order_id is a
        unique order identifier.        """
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
