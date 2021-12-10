"""orderScheduler.py
Implements scheduling algorithm to receive and schedule customer orders
"""

# Project modules
from customObjects import Queue, Order, RobotStatus
from bluetooth import BluetoothController
import time

class OrderScheduler:
    SUCCESS = 0
    ID_NOT_FOUND = 1
    queue = Queue()
    MAX_DRINK_CAPACITY = 3

    def __init__(self, num_kobukis, kobuki_state, bt1, bt2):
        self.next_id = 0
        self.num_kobukis = num_kobukis
        self.kobuki_state = kobuki_state
        self.bt1 = bt1
        self.bt2 = bt2


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
                       
                    self.display(i, k_order)
                    self.kobuki_state[i][0] = RobotStatus.LOADING
                else:
                    # No orders in queue. Remain idle.
                    pass
            elif state == RobotStatus.LOADING: 
                self.wait_for_delivery_press(i)
            elif state == RobotStatus.UNLOADING:
                self.wait_for_delivery_press(i)
            # TODO make 2 states loading and unloading
            elif state == RobotStatus.DELIVERING_ORDER or state == RobotStatus.PLAN_PATH_TO_TABLE:
                # TODO option to preempt if a higher priority order arrives. 
                
                pass
            else:
                # The scheduler does not operate on other states.
                pass
                
        return None

    def create(self, customer, seat, order, priority):
        """Create an order with the given paramters. Add to queue.
        Returns SUCCESS, order_id if the order was added, where order_id is a
        unique order identifier.        """
        id = self.next_id
        self.next_id += 1
        table = 0 if seat < 4 else 1
        order = Order(customer, seat, table, priority, order, id)
        self.queue.enqueue(order)
        return id

    def cancel(self, order_id):
        """Cancel the order with the given order_id.
        Returns SUCCESS on success, ID_NOT_FOUND if order_id is not found in the
        task list.
        """
        #TODO
        return self.SUCCESS
    
    def get_next_order(self):
        """Gets the next order to fulfill."""
        return self.queue.dequeue()
    
    def wait_for_delivery_press(self, kobuki_num): 
        if kobuki_num == 0:
            bt = self.bt1
        else:
            bt = self.bt2
        if bt.receive_button_press():
            # print("received press")
            # Button was pressed. Update the state.
            state, orders, _ = self.kobuki_state[kobuki_num]
            if state == RobotStatus.LOADING and len(orders) > 0:
                state = RobotStatus.PLAN_PATH_TO_TABLE
            elif state == RobotStatus.UNLOADING:
                if len(orders) > 0:
                    # Deliver the next order.
                    state = RobotStatus.PLAN_PATH_TO_TABLE
                else:
                    # Return to base.
                    state = RobotStatus.PLAN_PATH_TO_BASE
            self.kobuki_state[kobuki_num][0] = state

    def display(self,kobuki_num, order_list):
        drink_list = []
        for item in order_list: 
            #print(item.order)
            if not kobuki_num: 
                self.bt1.display_drink(item.order)
            else: 
                self.bt2.display_drink(item.order)
            # time.sleep(2)

        
        
        
