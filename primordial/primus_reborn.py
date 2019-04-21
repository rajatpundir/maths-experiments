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
        # construct another object for another number.
        self.primes = list(list_of_primes)
        self.powers = []
        for i in range(len(self.primes)):
            self.powers.append(0)
            power_vals[self.primes[i]] = list()
        self.result = 1
        self.workers = []
        self.worker_master_in_channel = []
        self.worker_master_out_channel = []
        self.worker_cluster_channel = []
        self.worker_ring_channel = []
        self.worker_antiring_channel = []
        # creating attributes for a worker node
        for i in range(len(self.primes)):
            self.worker_master_in_channel.append(PrimeQueue(self.dummy_callback))
            self.worker_master_out_channel.append(PrimeQueue(self.dummy_callback))
            self.worker_cluster_channel.append(PrimeQueue(self.dummy_callback))
            self.worker_ring_channel.append(PrimeQueue(self.dummy_callback))
            self.worker_antiring_channel.append(PrimeQueue(self.dummy_callback))
        # create worker threads
        for i in range(len(self.primes)):
            if i == 0:
                left = len(self.primes) - 1
                if len(self.primes) == 1:
                    right = left
                else:
                    right = 1
            elif i == len(self.primes) - 1:
                right = 0
                if len(self.primes) == 1:
                    left = right
                else:
                    left = len(self.primes) - 2
            else:
                right = i + 1
                left = i - 1
            # create worker
            worker = Thread(target= self.peerless, args=(self.primes[i], i, len(self.primes), self.worker_master_in_channel[i], self.worker_master_out_channel[i], self.worker_cluster_channel, self.worker_ring_channel, self.worker_antiring_channel, right, left))
            worker.daemon = True
            self.workers.append(worker)
        # start worker threads
        for i in range(len(self.primes)):
            self.workers[i].start()
        # feed input to workers on worker_master_in_channel
        for i in range(len(self.primes)):
            self.worker_master_in_channel[i].put(n)
        # wait for powers on master_out_channel
        for i in range(len(self.primes)):
            while self.worker_master_out_channel[i].empty():
                time.sleep(0.5)
            self.powers[i] = int(self.worker_master_out_channel[i].get())
        # compute result
        self.result = 1
        for i in range(len(self.primes)):
            if self.powers[i] != 0:
                self.result *= self.primes[i]**self.powers[i]
        print(self.powers)
        print('Result =', self.result, 'for n =', n, 'and Error =', (n/self.result*100))

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
        diff = n - power_vals[p][power - 1]
        return(diff, power)

    def stained(self):
        pass

    # maybe write a recursive function, sync var divisible by len(self.primes)?
    def peerless(self, p, node_id, node_count, mstr_in, mstr_out, cluster, clockwise_ring, anticlockwise_ring, r, l):
        print('Starting thread for p =', p)
        # wait on master_input channel
        while mstr_in.empty():
            time.sleep(0.01)
        n = int(mstr_in.get())
        print('Working for p =', p, 'and n =', n)
        accumulated_power = 0
        while n >= 2:
            diff, power = self.diff_prime(n, p)
            print('Working for p =', p, 'n=', n, 'power=', power, 'accumulated_power =', accumulated_power, 'diff=', diff)
            # declare difference on the ring channels
            if self.primes[0] == p:
                clockwise_ring[r].put(diff)
                anticlockwise_ring[l].put(diff)
            # logic for the clockwise_ring
            while clockwise_ring[l].empty():
                print('p=', p, 'is waiting on clockwise_ring')
                time.sleep(0.01)
            diff_clockwise_ring = int(clockwise_ring[l].get())
            print('p=', p,'got', diff_clockwise_ring, 'on clockwise_ring')
            if self.primes[0] != p:
                if diff_clockwise_ring < diff:
                    clockwise_ring[r].put(diff_clockwise_ring)
                else:
                    clockwise_ring[r].put(diff)
            # logic for anticlockwise_ring
            while anticlockwise_ring[r].empty():
                time.sleep(0.01)
                print('p=', p, 'is waiting on anticlockwise_ring')
            diff_anticlockwise_ring = int(anticlockwise_ring[r].get())
            print('p=', p,'got', diff_anticlockwise_ring, 'on anticlockwise_ring')
            if self.primes[0] != p:
                if diff_anticlockwise_ring < diff:
                    anticlockwise_ring[l].put(diff_anticlockwise_ring)
                else:
                    anticlockwise_ring[l].put(diff)
            print('p =', p,'diff=', diff, 'diff_clockwise_ring = ', diff_clockwise_ring, 'diff_anticlockwise_ring', diff_anticlockwise_ring)
            
            # announce the difference that created a leader
            leader_diff = 0
            if p == self.primes[0]:
                clockwise_ring[r].put(diff)
                anticlockwise_ring[l].put(diff)
                leader_diff = diff_clockwise_ring
                for i in range(node_count):
                    if i != node_count:
                        cluster[i].put(diff_clockwise_ring)
            else:
                # wait for the announcement of leader
                while cluster[node_id].empty():
                    print(p, 'is waiting for leader announcement')
                    time.sleep(0.01)
                leader_diff = int(cluster[node_id].get())
            if diff == leader_diff:
                print('leader =', p)
                # declare new value of n to other nodes
                accumulated_power += 1
                # n = n // power_vals[p][power - 1]
                n = n // p
                print('new value of n=', n)
                for i in range(node_count):
                    if i != node_id:
                        cluster[i].put(n)
            else:
                # wait for the new value of n from leader
                while cluster[node_id].empty():
                    time.sleep(0.01)
                    print(p,'is waiting for a value of n, old =', n)
                n = int(cluster[node_id].get())
                print('slave =', p, 'n =', n)
        print('Thread p=', p, 'finished working.')
        # for i in range(node_count):
        #         if i != node_id:
        #             cluster[i].put(-1)
        # send computed powers to master
        mstr_out.put(accumulated_power)

# the one who has minimum difference gets a first-go at the number
# maybe cluster_in and cluster_out for all nodes
prime(60)
