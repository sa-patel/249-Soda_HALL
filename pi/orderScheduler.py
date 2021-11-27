from customObjects import Queue, Order

class OrderScheduler:
    SUCCESS = 0
    ID_NOT_FOUND = 1
    queue = Queue()

    def __init__(self):
        self.next_id = 0
    def create(self, customer, table, order, priority):
        """Create an order with the given paramters. Add to queue.
        Returns SUCCESS, order_id if the order was added, where order_id is a
        unique order identifier.
        """
        id = self.next_id
        self.next_id += 1
        order = Order(customer, table, priority, order, id)
        self.queue.enqueue(order)
        print("next id create", self.next_id)
        return id

    def cancel(order_id):
        """Cancel the order with the given order_id.
        Returns SUCCESS on success, ID_NOT_FOUND if order_id is not found in the
        task list.
        """
        return self.SUCCESS
    
    def get_next_order(self):
        """Gets the next order to fulfill."""
        print("next id get", self.next_id)
        return self.queue.dequeue()
