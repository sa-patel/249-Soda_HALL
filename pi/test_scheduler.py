from customObjects import Queue, Order, RobotStatus
from orderScheduler import OrderScheduler

kobuki_state = [(RobotStatus.IDLE, [], 0), (RobotStatus.IDLE, [], 0)] # 2-tuple (STATE, Order) for each robot
scheduler = OrderScheduler(2, kobuki_state)

scheduler.create("Amit",1,"Gin",0)
scheduler.create("Zak",2,"Rum",0)
scheduler.create("Sagar",3,"Beer",0)
scheduler.create("Max",4,"Vodka",0)
scheduler.create("Amit",1,"Whiskey",0)
scheduler.create("Zak",2,"Tequila",0)
scheduler.create("Sagar",3,"Seltzer",0)
scheduler.create("Max",4,"Pop",0)

scheduler.queue.print_queue()


scheduler.allocate()
print("First kobuki: ", kobuki_state[0])
print("Second kobuki: ", kobuki_state[1])

scheduler.queue.print_queue()

#once we return to idle from delivered drinks, must clear out scheduler class variables
kobuki_state = [(RobotStatus.IDLE, [], 0), (RobotStatus.IDLE, [], 0)] # 2-tuple (STATE, Order) for each robot
scheduler.__init__(2,kobuki_state)
scheduler.allocate()
print("First kobuki: ", kobuki_state[0])
print("Second kobuki: ", kobuki_state[1])

scheduler.queue.print_queue()

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




