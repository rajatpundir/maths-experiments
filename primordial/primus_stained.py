import time
from math import sqrt
from queue import Queue
from threading import Thread
import numpy as np

list_of_primes = set([2, 3, 5])
upper_limit = 5
verbose = True
# store and load from file
power_vals = {}

def is_prime(n):
    if n < 2:
        return 0;
    if n == 2:
        return(1)
    if n % 2 == 0:
        return 0;
    if len(list_of_primes) != 0:
        if n in list_of_primes:
            return(1)
        for i in list_of_primes:
            if n % i == 0:
                return(i)
        for i in range(list(list_of_primes)[-1], int(sqrt(n) + 1), 2):
            if n % i == 0:
                return(i)
    else:
        for i in range(3, int(sqrt(n) + 1), 2):
            if n % i == 0:
                return(i)
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
        for i in range(len(self.primes)):
            self.powers.append(0)
            power_vals[self.primes[i]] = list()
        
        z = n
        while n >= self.primes[0]:
            x = n
            for i in range(len(self.primes) - 1, -1, -1):
                power = self.diff_prime(x, self.primes[i])
                print(n, x, self.primes[i], power)
                self.powers[i] += power
                if power != 0:
                    x = x // power_vals[self.primes[i]][power - 1]
            self.result = 1
            for i in range(len(self.primes)):
                if self.powers[i] != 0:
                    self.result *= self.primes[i]**self.powers[i]
            n = n // self.result
            print(n)

        print(self.powers)
        print('Result =', self.result, 'for n =', z, 'and Error =', 100-(self.result/z*100))

    def dummy_callback(self):
        pass

    def diff_prime(self, n, p):
        if len(power_vals[p]) == 0:
            power_vals[p].append(p)
        if n <= power_vals[p][-1]:
            power = 0
            for x in power_vals[p]:
                if x <= n:
                    power += 1
                else:
                    break
        else:
            x = power_vals[p][-1]
            power = len(power_vals[p])
            while True:
                x = x * p
                power_vals[p].append(x)
                if x <= n:
                    power += 1
                else:
                    break
        return(power)


s = time.time()
a = prime(74)
print('Time =', time.time()- s)
while True:
    n = int(input('Input : '))
    s = time.time()
    a = prime(n)
    print('Time =', time.time()- s)
