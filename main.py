import time, random
from threading import Thread, currentThread, Condition

class sharedCell(object):
    
    def __init__(self, consumerCount):
        self._data = -1
        self._consumerCount = consumerCount
        self._consumerNames = []
        self._writeable = True
        self._condition = Condition()
    
    def setData(self, data):
        self._condition.acquire()
        while not self._writeable:
            self._condition.wait()
            
        print("%s setting data to %d" % (currentThread().getName(), data))
        
        self._data = data
        self._writeable = False
        self.initialiseConsumers()
        self._condition.notify()
        self._condition.release()
        
    def getData(self):
        self._condition.acquire()
        
        while self._writeable:
            self._condition.wait()
            
        print("%s accessing data %d" % (currentThread().getName(), self._data))
        
        index = -1
        currentCounter = 0
        for c in self._consumerNames:
            if c == currentThread().getName():
                index = currentCounter
            currentCounter += 1
            
        if index != -1:
            self._consumerNames.pop(index)
                
        if len(self._consumerNames) == 0:
            self._writeable = True
        self._condition.notify()
        self._condition.release()
        return self._data
    
    def initialiseConsumers(self):
        index = 1
        while index <= self._consumerCount:
            name = "Consumer" + str(index)
            self._consumerNames.append(name)
            index += 1
    
class Producer(Thread):
    
    def __init__(self, cell, accessCount, sleepMax, pName):
        
        Thread.__init__(self, name = pName)
        self._accessCount = accessCount
        self._cell = cell
        self._sleepMax = sleepMax
        
    def run(self):
        
        print("%s starting up" % self.getName())
        for count in range(self._accessCount):
            time.sleep(random.randint(1, self._sleepMax))
            self._cell.setData(count + 1)
        print("%s is done producing" % self.getName())
        
class Consumer(Thread):
    
    def __init__(self,cell, accessCount, sleepMax, cName):
        Thread.__init__(self, name = cName)
        self._accessCount = accessCount
        self._cell = cell
        self._sleepMax = sleepMax
        
    def run(self):
        print("%s starting up" % self.getName())
        for count in range(self._accessCount):
            time.sleep(random.randint(1, self._sleepMax))
            value = self._cell.getData()
        print("%s is done consuming" % self.getName())
        
def main():
    
    accessCount = int(input("Enter the number of accesses : "))
    sleepMax = 4
    consumerCount = int(input("Please enter the number of consumers : "))
    cell = sharedCell(consumerCount)
    producer = Producer(cell, accessCount, sleepMax, "Producer")
    
    print("Starting the threads")
    for c in range(consumerCount):
        if c < consumerCount:
            name = "Consumer" + str(c + 1)
            consumer = Consumer(cell, accessCount, sleepMax,name)
            consumer.start()
    producer.start()
    
main()
    
            
        
    
