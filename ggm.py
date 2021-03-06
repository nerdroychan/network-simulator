import simpy
import random as rand
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

###
# Consider that the bandwidth is always 0.2
# The sender generate a packet with a random size (follow some distribution rule)
# While the packet size is around 0.2p
# So that the deliver time is (packet size / 0.2)
# This can simulate a continuous changing bandwidth in a discrete way
#
# Parameters needed:
#   1. Average Queuing Delay & Average Transmission Delay & Total
#   2. Packet Generated & Packet Lost Rate
#   3. Throughput
###
# Now, define some variables
###
# 0 = rand.uniform(a, b) [default]
# 1 = rand.triangular(low, high, mode)
# 2 = rand.betavariate(alpha, beta)
# 3 = rand.expovariate(lambd)
# 4 = rand.gammavariate(alpha, beta)
# 5 = rand.gauss(mu, sigma)
# 6 = rand.lognormvariate(mu, sigma)
# 7 = rand.normalvariate(mu, sigma)
# 8 = rand.vonmisesvariate(mu, kappa)
# 9 = rand.paretovariate(alpha)
# 10 = rand.weibullvariate(alpha, beta)
###

PACKET_GENERATION_DISTRIBUTION = 0
P_PARAMETER_ONE = 0.0
P_PARAMETER_TWO = 0.0
P_PARAMETER_THREE = 0.0

BANDWIDTH_DISTRIBUTION = 0
B_PARAMETER_ONE = 0.0
B_PARAMETER_TWO = 0.0
B_PARAMETER_THREE = 0.0

###
# 0 = FIFO [default]
# 1 = LIFO
# 2 = RO
###

ACCOUNTING_METHOD = -1

###
# Input the distributions
###

def distribution_choose_menu():
    print('0) uniform *2')
    print('1) triangular *3')
    print('2) betavariate *2')
    print('3) expovariate *2')
    print('4) gammavariate *2')
    print('5) gauss *2')
    print('6) lognormvariate *2')
    print('7) normalvariate *2')
    print('8) vonmisesvariate *2')
    print('9) paretovariate *1')
    print('10) weibullvariate *2')

def check_set_number(must = True, is_float = True):
    while True:
        tmp = input()
        if tmp == '':
            if must:
                print('not a valid number, please try again')
            else:
                return 0.0
            continue
        else:
            try:
                if is_float:
                    var = float(tmp)
                else:
                    var = int(tmp)
                break
            except ValueError:
                print('not a valid number, please try again')
                continue
    return var

def set_distribution(name):
    retry = False
    while True:
        if not retry:
            print('What kind of probability distribution of %s do you want?' % name)
            print('Input nothing if you want to keep the default value 0.')
            print('Check https://docs.python.org/3/library/random.html for more information')
            distribution_choose_menu()
        tmp = input()
        if tmp == '':
            var = 0
            break
        else:
            try:
                var = int(tmp)
            except ValueError:
                print('not a valid number, please try again')
                retry = True
                continue
            if var not in range(11):
                print('not a valid number, please try again')
                retry = True
                continue
        break
    return var

PACKET_GENERATION_DISTRIBUTION = set_distribution('packet generation interval')
print('Set paramater one (must)')
P_PARAMETER_ONE = check_set_number()
print('Set parameter two (optional)')
P_PARAMETER_TWO = check_set_number(must = False)
print('Set parameter three (optional)')
P_PARAMETER_THREE = check_set_number(must = False)

BANDWIDTH_DISTRIBUTION = set_distribution('the bandwidth')
print('Set paramater one (must)')
B_PARAMETER_ONE = check_set_number()
print('Set parameter two (optional)')
B_PARAMETER_TWO = check_set_number(must = False)
print('Set parameter three (optional)')
B_PARAMETER_THREE = check_set_number(must = False)

###
# Input the accounting method
###

def set_accounting_method():
    retry = False
    while True:
        if not retry:
            print('What kind of accounting method do you want?')
            print('0) FIFO')
            print('1) LIFO')
            print('2) RO')
        tmp = input()
        if tmp == '':
            return 0
        else:
            try:
                var = int(tmp)
            except ValueError:
                print('not a valid number, please try again')
                retry = True
                continue
            if var not in range(3):
                print('not a valid number, please try again')
                retry = True
                continue
        break
    return var

ACCOUNTING_METHOD = set_accounting_method()

###
# Define other parameters
###

packet_generated = 0
packet_lost = 0
total_queuing_delay = 0.0
total_transmission_delay = 0.0

TOTAL_TIME = 0.0
BUFFER_CAPACITY = 0

###
# Input simulation time
###

print('Input the simulation time')
TOTAL_TIME = check_set_number()
print('Input the buffer capacity (must be an integer)')
BUFFER_CAPACITY = check_set_number(is_float = False)

###
# Resource Pool
###

print('Input the resource pool capacity')
RESOURCE_POOL_CAPACITY = check_set_number(must = True, is_float = False)

###
# Reuqest Method
###

def set_request_method():
    retry = False
    while True:
        if not retry:
            print('Choose the request method')
            print('0) Request the port with the lowest load')
            print('1) Request the port randomly')
            print('2) Request the port in order')
            print('3) Reuqest the port in order loop')
        tmp = input()
        if tmp == '':
            return 0
        else:
            try:
                var = int(tmp)
            except ValueError:
                print('not a valid number, please try again')
                retry = True
                continue
            if var not in range(4):
                print('not a valid number, please try again')
                retry = True
                continue
        break
    return var

REQUEST_METHOD = set_request_method()

###
# Start simulation
###

def generate_interval(num, parameter_one, parameter_two = 0.0, parameter_three = 0.0):
    rand_intervals = [
        rand.uniform,
        rand.triangular,
        rand.betavariate,
        rand.expovariate,
        rand.gammavariate,
        rand.gauss,
        rand.lognormvariate,
        rand.normalvariate,
        rand.vonmisesvariate,
        rand.paretovariate,
        rand.weibullvariate,
    ]
    try:
        result = rand_intervals[num](parameter_one, parameter_two, parameter_three)
    except TypeError:
        try:
            result = rand_intervals[num](parameter_one, parameter_two)
        except TypeError:
            result = rand_intervals[num](parameter_one)
    return result

def generate_priority(accounting_method, pk):
    if accounting_method == 0:
        return pk
    elif accounting_method == 1:
        return -pk
    elif accounting_method == 2:
        return rand.randint(1, 65535)

def total_queue_load(link):
    total_load = 0
    for i in link:
        total_load += len(i.queue)
    return total_load

def port_to_request(method, link, pk):
    global BUFFER_CAPACITY
    global RESOURCE_POOL_CAPACITY
    port = None
    if method == 0:
        for i in link:
            if port == None:
                port = i
            else:
                if len(i.queue) + i.count < len(port.queue) + port.count:
                    port = i
        return port
    elif method == 1:
        port = link[rand.randint(0, len(link) - 1)]
    elif method == 2:
        for i in link:
            if len(i.queue) < BUFFER_CAPACITY:
                port = i
                break
            else:
                continue
    elif method == 3:
        port = link[(pk - 1) % RESOURCE_POOL_CAPACITY]
    return port

def packet(env, pk, link):
    global PACKET_GENERATION_DISTRIBUTION
    global P_PARAMETER_ONE
    global P_PARAMETER_TWO
    global P_PARAMETER_THREE
    global BANDWIDTH_DISTRIBUTION
    global B_PARAMETER_ONE
    global B_PARAMETER_TWO
    global B_PARAMETER_THREE
    global BUFFER_CAPACITY
    global ACCOUNTING_METHOD
    global REQUEST_METHOD
    global packet_generated
    global packet_lost
    global total_queuing_delay
    global total_transmission_delay
    size = 1 / generate_interval(BANDWIDTH_DISTRIBUTION, B_PARAMETER_ONE, B_PARAMETER_TWO, B_PARAMETER_THREE)
    print('Packet %d generated at %s, size = %s' % (pk, env.now, size))
    generation_time = float(env.now)
    if total_queue_load(link) < BUFFER_CAPACITY * len(link):
        port = port_to_request(REQUEST_METHOD, link, pk)
        if len(port.queue) < BUFFER_CAPACITY:
            with port.request(priority = generate_priority(ACCOUNTING_METHOD, pk)) as request:
                yield request
                transmission_start_time = env.now
                total_queuing_delay += transmission_start_time - generation_time
                print('Packet %d begin to transmit at %s on port %d' % (pk, env.now, link.index(port)))
                yield env.timeout(size)
                packet_generated += 1
                total_transmission_delay += size
                print('Packet %d ended transmission at %s, cost %s' %(pk, env.now, size))
        else:
            packet_lost += 1
            print('Packet %d lost at %s' % (pk, env.now))
    else:
        packet_lost += 1
        print('Packet %d lost at %s' % (pk, env.now))

def transmit(env, link):
    pk = 1
    while True:
        env.process(packet(env, pk, link))
        yield env.timeout(generate_interval(PACKET_GENERATION_DISTRIBUTION, P_PARAMETER_ONE, P_PARAMETER_TWO, P_PARAMETER_THREE))
        pk += 1

def graph(env, graph_dict):
    global packet_generated
    global packet_lost
    global total_queuing_delay
    global total_transmission_delay
    global TOTAL_TIME
    while True:
        try:
            graph_dict['average_queuing_delay'].append(total_queuing_delay / (packet_generated - packet_lost))
        except ZeroDivisionError:
            graph_dict['average_queuing_delay'].append(0)
        try:
            graph_dict['average_transmission_delay'].append(total_transmission_delay / (packet_generated - packet_lost))
        except ZeroDivisionError:
            graph_dict['average_transmission_delay'].append(0)
        try:
            graph_dict['packet_lost_rate'].append(packet_lost / packet_generated * 100)
        except ZeroDivisionError:
            graph_dict['packet_lost_rate'].append(0)
        try:
            graph_dict['throughput'].append((packet_generated - packet_lost) / env.now)
        except ZeroDivisionError:
            graph_dict['throughput'].append(0)
        yield env.timeout(1)

def draw(graph_dict):
    plt.title('Network Data')
    plt.subplot(2, 2, 1)
    plt.plot(range(1, int(TOTAL_TIME + 1)), graph_dict['average_queuing_delay'])
    plt.ylabel('Average Queuing Delay')
    plt.xlabel('Time')
    plt.subplot(2, 2, 2)
    plt.plot(range(1, int(TOTAL_TIME + 1)), graph_dict['average_transmission_delay'])
    plt.ylabel('Average Transmission Delay')
    plt.xlabel('Time')
    plt.subplot(2, 2, 3)
    plt.plot(range(1, int(TOTAL_TIME + 1)), graph_dict['packet_lost_rate'])
    plt.ylabel('Packet Lost Rate')
    plt.xlabel('Time')
    plt.subplot(2, 2, 4)
    plt.plot(range(1, int(TOTAL_TIME + 1)), graph_dict['throughput'])
    plt.ylabel('Throughput')
    plt.xlabel('Time')
    plt.show()

if __name__ == '__main__':
    env = simpy.Environment()
    link = []
    for i in range(RESOURCE_POOL_CAPACITY):
        link.append(simpy.PriorityResource(env, capacity = 1))
    env.process(transmit(env, link))
    graph_dict = {
        'average_queuing_delay': [],
        'average_transmission_delay': [],
        'packet_lost_rate': [],
        'throughput': []
    }
    env.process(graph(env, graph_dict))
    env.run(until = TOTAL_TIME)
    print('Total packet generated', packet_generated)
    print('Total packet lost', packet_lost)
    print('Total Queuing Delay', total_queuing_delay)
    print('Total Transmission Delay', total_transmission_delay)
    print('Average Queuing Dealy', str(total_queuing_delay / (packet_generated - packet_lost)))
    print('Average Transmission Dealy', str(total_transmission_delay / (packet_generated - packet_lost)))
    print('Packet lost rate', str(packet_lost / packet_generated * 100), '%')
    print('Average Throughput', str((packet_generated - packet_lost) / TOTAL_TIME))
    draw(graph_dict)