"""orderScheduler.py
Implements scheduling algorithm to receive and schedule customer orders
"""

# Project modules
from customObjects import Queue, Order, RobotStatus
from bluetooth import BluetoothController
import time
from waiter import KobukiRobot
from navigation import SEAT_NO_TO_WAYPOINT_ID

class OrderScheduler:
    SUCCESS = 0
    ID_NOT_FOUND = 1
    MAX_DRINK_CAPACITY = 3

    def __init__(self, kobukis, waypoints):
        self.kobukis = kobukis
        self.queue = Queue()
        self.waypoints = waypoints

    def allocate(self):
        for k in self.kobukis:
            if k.get_status() == RobotStatus.LOADING:
                # # Without table prioritization
                # while k.get_num_drinks() < KobukiRobot.MAX_DRINK_CAPACITY:
                #     next_order = self.get_next_order()
                #     if next_order:
                #         wid = SEAT_NO_TO_WAYPOINT_ID[next_order.seat]
                #         k.place_drink(next_order.order, self.waypoints[wid])
                while k.get_num_drinks() < KobukiRobot.MAX_DRINK_CAPACITY:
                    next_order = self.get_next_order()
                    if next_order is None:
                        break
                    
                    wid = SEAT_NO_TO_WAYPOINT_ID[next_order.seat]
                    k.place_drink(next_order.order, self.waypoints[wid])
                    cur_table = next_order.table
                    # Find additional orders
                    same_table_orders = self.queue.search_items_queue(cur_table,self.MAX_DRINK_CAPACITY - k.get_num_drinks())
                    for order in same_table_orders:
                        wid = SEAT_NO_TO_WAYPOINT_ID[order.seat]
                        k.place_drink(order.order, self.waypoints[wid])

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
        # TODO move this logic to KobukiRobot
        drink_list = []
        drinks_string = " ".join(order_list)
        if kobuki_num == 0: 
            self.bt1.display_drink(drinks_string)
        else: 
            self.bt2.display_drink(drinks_string)
        # time.sleep(2)

        
        
        
