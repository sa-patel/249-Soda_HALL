from customObjects import Queue, Order, RobotStatus
from orderScheduler import OrderScheduler
# from bluetooth import BluetoothController 
import time 
from navigation import *
from customObjects import Waypoint
from waiter import KobukiRobot


waypoints = [Waypoint(i, (100.0, 100.0)) for i in range(NUM_WAYPOINTS)]
nav_graph = NavGraph()

waiter1 = KobukiRobot(1, nav_graph)
waiter2 = KobukiRobot(2, nav_graph)

scheduler = OrderScheduler([waiter1, waiter2], waypoints)

# bt1 = BluetoothController(1) 
# bt2 = BluetoothController(2) 
# bt1.connect()
# bt2.connect() 

#kobuki_state = [(RobotStatus.IDLE, [], 0), (RobotStatus.IDLE, [], 0)] # 2-tuple (STATE, Order) for each robot
#kobuki_state = [[RobotStatus.IDLE, [], 0], [RobotStatus.IDLE, [], 0]] # 3-list [STATE, Orders, NUM_DRINKS] for each robot

scheduler.create("Amit",1,"Gin",0)
scheduler.create("Zak",2,"Rum",0)
scheduler.create("Sagar",5,"Beer",0)
scheduler.create("Max",4,"Vodka",0)
scheduler.create("Amit",1,"Whiskey",0)
scheduler.create("Zak",2,"Tequila",0)
scheduler.create("Sagar",5,"Seltzer",0)
scheduler.create("Max",4,"Pop",0)

scheduler.queue.print_queue()


scheduler.allocate()
print("First kobuki: ", waiter1.drinks)
print("Second kobuki: ", waiter2.drinks)

scheduler.queue.print_queue()

#Drinks are loaded now keep waiting until button is pressed 
# waiter1.push_button()
# waiter2.push_button()

waiter1.state = RobotStatus.MOVING
waiter1.state = RobotStatus.MOVING

scheduler.create("Zak",2,"Baileys",0)
scheduler.allocate() # shouldnt do anything 
scheduler.queue.print_queue() # shouldnt do anything 

waiter1.state = RobotStatus.UNLOADING
waiter2.state = RobotStatus.UNLOADING
waiter1.destinations.pop(0) # TODO this will not work for unordered deliveries.
drink_name = waiter1.drinks.pop(0)
waiter2.destinations.pop(0) # TODO this will not work for unordered deliveries.
drink_name = waiter2.drinks.pop(0)

print("First kobuki: ", waiter1.drinks)
print("Second kobuki: ", waiter2.drinks)

waiter1.state = RobotStatus.MOVING
waiter1.state = RobotStatus.MOVING

scheduler.allocate() # shouldnt do anything 
scheduler.queue.print_queue() # shouldnt do anything 

waiter1.state = RobotStatus.LOADING
waiter2.state = RobotStatus.LOADING


scheduler.allocate()
print("First kobuki: ", waiter1.drinks)
print("Second kobuki: ", waiter2.drinks)

scheduler.queue.print_queue()

# while(kobuki_state[0][0] == RobotStatus.LOADING):
#     scheduler.allocate()
#     print("First kobuki:", kobuki_state[0][0])
#     time.sleep(1)

# kobuki_state[0] = [RobotStatus.IDLE, [], 0]
# scheduler.allocate()

# scheduler.queue.print_queue()

""""
same_table_order = scheduler.queue.search_items_queue(4,2)

for item in same_table_order:
    print("Found drink for same table",item.table)

scheduler.queue.print_queue()
print(scheduler.queue.size)


same_table_order = scheduler.queue.search_item_queue(4)
if same_table_order: 
    print("Found drink for same table",same_table_order.table)
else: 
    print("no other drink at that table")

scheduler.queue.print_queue()
print(scheduler.queue.size)


same_table_order = scheduler.queue.search_item_queue(4)
if same_table_order: 
    print("Found drink for same table",same_table_order.table)
else: 
    print("no other drink at that table")

scheduler.queue.print_queue()
print(scheduler.queue.size)

print(scheduler.queue.data[scheduler.queue.head - 1].name)
print(scheduler.queue.dequeue().order)

scheduler.queue.print_queue()
"""




