
#low priority gets poppped first
class PriorityQueue:

    def __init__(self):
        self.__queue = []
        self.__priorities = {}
    
    def put(self, elem, priority):
        if elem in self.__queue:
            if self.__priorities.get(elem) == priority:
                return
            else:
                self.__queue.remove(elem)

        for other_elem in self.__queue:
            if self.__priorities[other_elem] < priority:
                self.__queue.insert(self.__queue.index(other_elem), elem)
                self.__priorities[elem] = priority
                return

        #if we get to end of queue, just add the elem there.
        self.__queue.append(elem)
        self.__priorities[elem] = priority

    def pop(self, index = None):
        if index == None: index = len(self.__queue) - 1
        elem = self.__queue.pop(index)
        self.__priorities[elem] = None
        return elem

    def is_empty(self):
        return len(self.__queue) == 0

    def __str__(self):
        return self.__queue.__str__()