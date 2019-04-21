import time
from threading import Thread
from math import sqrt
import numpy as np
from queue import Queue


list_of_primes = set([2, 3])
upper_limit = 5
verbose = False

def is_prime(n):
    if n < 2:
        return 0;
    if n == 2:
        if verbose:
            print(n, 'is prime')
        return(1)
    if n % 2 == 0:
        if verbose:
            print(n, 'is divisible by', 2)
        return 0;
    if len(list_of_primes) != 0:
        if n in list_of_primes:
            return(1)
        for i in list_of_primes:
            if n % i == 0:
                if verbose:
                    print(n, 'is divisible by', i)
                return(i)
        for i in range(list(list_of_primes)[-1], int(sqrt(n) + 1), 2):
            if n % i == 0:
                if verbose:
                    print(n, 'is divisible by', i)
                return(i) 
    else:
        for i in range(3, int(sqrt(n) + 1), 2):
            if n % i == 0:
                if verbose:
                    print(n, 'is divisible by', i)
                return(i)
    if verbose:
        print(n, 'is prime')
    list_of_primes.add(n)
    return(1)

for i in range(upper_limit):
    is_prime(i)

if verbose:
    print(list_of_primes)

class PrimeQueue(Queue):
    # Multithread Safe Queue.
    callback_function = None
    def __init__(self, callback_function, **kwargs):
        super().__init__(self, **kwargs)
        self.maxsize = 0
        self.callback_function = callback_function
    def put(self, val):
        Queue.put(self, val, False)
        self.callback_function()
    def get(self):
        return Queue.get(self, False)

class prime:
    def __init__(self, n):
        self.primes = list(list_of_primes)
        self.powers = []
        self.quotients = []
        for i in range(len(self.primes)):
            self.powers.append(0)
            self.quotients.append(0)
        
        self.result = 1
        
        x = n
        while n > self.primes[0]:
            if verbose:
                print('n =', n)
            self.workers = []
            self.worker_queue = []
            self.input_queue = []
             # create worker queues
            for i in range(len(self.primes)):
                self.worker_queue.append(PrimeQueue(self.dummy_callback))
            # create input threads for worker
            for i in range(len(self.primes)):
                self.input_queue.append(PrimeQueue(self.dummy_callback))
                self.input_queue[i].put(n)
            # create worker threads
            for i in range(len(self.primes)):
                worker = Thread(target= self.godchild, args=(self.input_queue[i], self.worker_queue[i], self.primes[i]))
                worker.daemon = True
                self.workers.append(worker)
            # start worker threads
            for i in range(len(self.primes)):
                self.workers[i].start()
            # do the magic
            self.sunborn(n)
            # stop worker threads
            for i in range(len(self.primes)):
                self.input_queue[i].put(-1)
            # time.sleep(0.1)
            self.result = 1
            for i in range(len(self.primes)):
                if self.powers[i] != 0:
                    self.result *= self.primes[i]**self.powers[i]
            n = x // self.result
            if n == self.primes[0]:
                self.powers[0] += 1
                break

        # stop worker threads
        for i in range(len(self.primes)):
            self.input_queue[i].put(-1)
        time.sleep(0.1)
        # print the primes
        if True:
            self.result = 1
            for i in range(len(self.primes)):
                if self.powers[i] != 0:
                    print(self.primes[i])
                    self.result *= self.primes[i]**self.powers[i]
            print(self.powers, 'x=', x)
            print('Result =', self.result, 'Error =', ( 1- self.result/x) * 100)

    def get_result(self):
        self.result = 1
        for i in range(len(self.primes)):
            if self.powers[i] != 0:
                self.result *= self.primes[i]**self.powers[i]
        return(self.result)

    def get_powers(self):
        return(np.array(self.powers))

    def sunborn(self, n):
        while n > self.primes[0]:
            # wait for all workers to finish their work
            for i in range(len(self.primes)):
                while self.worker_queue[i].empty():
                    # build some kind of list and skip thread checking that have finished.
                    time.sleep(0.000000000001)
                self.quotients[i] = int(self.worker_queue[i].get())
                self.powers[i] += self.quotients[i]
            # check if we get any new factors
            quotients_sum = 0
            for i in range(len(self.primes)):
                quotients_sum += self.quotients[i]
            # retry with n-1 if no factors were found
            if quotients_sum == 0:
                n -= 1
                for i in range(len(self.primes)):
                    self.input_queue[i].put(n)
                continue
            # calculate new value of n
            self.result = 1
            for i in range(len(self.primes)):
                self.result *= self.primes[i]**self.powers[i]
            n = n // self.result
            # feed new value of n to workers
            for i in range(len(self.primes)):
                self.input_queue[i].put(n)

    def godchild(self, n_q, p_q, p):
        if verbose:
            print('Starting thread for p =', p)
        while True:
            while n_q.empty():
                time.sleep(.05)
            n = int(n_q.get())
            if n == -1 or n == 1:
                if verbose:
                    print('Stopping thread for p =', p)
                break
            power = 0
            if verbose:
                x = n
            while n % p == 0:
                power += 1
                n /= p
            if verbose:
                print('For n =',x ,',putting', power, 'for p =', p)
            p_q.put(power)

    def dummy_callback(self):
        pass

s = time.time()
a = prime(33)
print(a.primes)
print(a.powers)
print(str(a.get_result()))
print('Time =', time.time()- s)
while True:
    n = int(input('Input : '))
    s = time.time()
    a = prime(n)
    print(a.primes)
    print(a.powers)
    print(str(a.get_result()))
    print('Time =', time.time()- s)

