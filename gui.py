import simpy
import random as rand
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import tkinter as GUI

'''Core'''

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

def total_link_load(link):
    total_load = 0
    for i in link:
        total_load += len(i.queue) + i.count
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
    packet_generated += 1
    generation_time = float(env.now)
    if total_link_load(link) < (BUFFER_CAPACITY + 1) * len(link):
        port = port_to_request(REQUEST_METHOD, link, pk)
        if len(port.queue) < BUFFER_CAPACITY or total_link_load(link) == 0:
            with port.request(priority = generate_priority(ACCOUNTING_METHOD, pk)) as request:
                yield request
                transmission_start_time = env.now
                total_queuing_delay += transmission_start_time - generation_time
                print('Packet %d begin to transmit at %s on port %d' % (pk, env.now, link.index(port)))
                yield env.timeout(size)
                total_transmission_delay += size
                print('Packet %d ended transmission at %s, cost %s' %(pk, env.now, size))
        else:
            packet_lost += 1
            print('Packet %d lost at %s' % (pk, env.now))
    else:
        packet_lost += 1
        print('Packet %d lost at %s' % (pk, env.now))

def transmit(env, link):
    global packet_generated
    global packet_lost
    global total_queuing_delay
    global total_transmission_delay

    packet_generated = 0
    packet_lost = 0
    total_queuing_delay = 0.0
    total_transmission_delay = 0.0

    pk = 1
    while True:
        env.process(packet(env, pk, link))
        yield env.timeout(generate_interval(PACKET_GENERATION_DISTRIBUTION, P_PARAMETER_ONE, P_PARAMETER_TWO, P_PARAMETER_THREE))
        pk += 1

'''GUI'''

##
# Main Frame
##

main = GUI.Tk()
main.wm_title('Network Simulator')

bandwidth_frame = GUI.Frame(main)
frequency_frame = GUI.Frame(main)
parameter_frame = GUI.Frame(main)
button_frame    = GUI.Frame(main)
message_frame   = GUI.Frame(main)
accounting_method_frame = GUI.Frame(main)
request_method_frame = GUI.Frame(main)

##
# Distributions
##

BANDWIDTH_DISTRIBUTION = 0
B_PARAMETER_ONE = 0.0
B_PARAMETER_TWO = 0.0
B_PARAMETER_THREE = 0.0

PACKET_GENERATION_DISTRIBUTION = 0
P_PARAMETER_ONE = 0.0
P_PARAMETER_TWO = 0.0
P_PARAMETER_THREE = 0.0

temp_packet_generation_distribution = GUI.IntVar()
temp_bandwidth_distribution = GUI.IntVar()

DISTRIBUTION_TYPE = [
    '(0) Uniform',
    '(1) Triangular',
    '(2) Beta',
    '(3) Exponential',
    '(4) Gamma',
    '(5) Gaussian',
    '(6) Log-normal',
    '(7) Normal',
    '(8) von Mises',
    '(9) Pareto',
    '(10) Weibull',
]

def p_check_distribution():
    global temp_packet_generation_distribution
    global p_parameter_two_input
    global p_parameter_three_input
    if temp_packet_generation_distribution.get() in [0, 2, 4, 5, 6, 7, 8, 10]:
        p_parameter_two_input.configure(state = 'normal')
        p_parameter_three_input.configure(state = 'disabled')
    elif temp_packet_generation_distribution.get() == 1:
        p_parameter_two_input.configure(state = 'normal')
        p_parameter_three_input.configure(state = 'normal')
    elif temp_packet_generation_distribution.get() in [3, 9]:
        p_parameter_two_input.configure(state = 'disabled')
        p_parameter_three_input.configure(state = 'disabled')

def b_check_distribution():
    global temp_bandwidth_distribution
    global b_parameter_two_input
    global b_parameter_three_input
    if temp_bandwidth_distribution.get() in [0, 2, 4, 5, 6, 7, 8, 10]:
        b_parameter_two_input.configure(state = 'normal')
        b_parameter_three_input.configure(state = 'disabled')
    elif temp_bandwidth_distribution.get() == 1:
        b_parameter_two_input.configure(state = 'normal')
        b_parameter_three_input.configure(state = 'normal')
    elif temp_bandwidth_distribution.get() in [3, 9]:
        b_parameter_two_input.configure(state = 'disabled')
        b_parameter_three_input.configure(state = 'disabled')

GUI.Label(
    bandwidth_frame,
    text = 'Bandwidth:',
    justify = GUI.LEFT,
    padx = 20,
    ).grid(column = 0)

for i in range(len(DISTRIBUTION_TYPE)):
    GUI.Radiobutton(
        bandwidth_frame,
        text = DISTRIBUTION_TYPE[i],
        padx = 20, 
        variable = temp_bandwidth_distribution, 
        value = i,
        command = b_check_distribution,
        ).grid(column = 0, sticky = GUI.W)

GUI.Label(bandwidth_frame, text = 'Parameter 1').grid(column = 0)
b_parameter_one_input = GUI.Entry(bandwidth_frame)
b_parameter_one_input.insert(0, 0.0)
b_parameter_one_input.grid(column = 0)
GUI.Label(bandwidth_frame, text = 'Parameter 2').grid(column = 0)
b_parameter_two_input = GUI.Entry(bandwidth_frame)
b_parameter_two_input.insert(0, 0.0)
b_parameter_two_input.grid(column = 0)
GUI.Label(bandwidth_frame, text = 'Parameter 3').grid(column = 0)
b_parameter_three_input = GUI.Entry(bandwidth_frame)
b_parameter_three_input.insert(0, 0.0)
b_parameter_three_input.grid(column = 0)

b_check_distribution()

bandwidth_frame.grid(column = 0, row = 1, padx = 15, pady = 5)

GUI.Label(
    frequency_frame,
    text = 'Frequency:',
    justify = GUI.LEFT,
    padx = 20,
    ).grid(column = 1)

for i in range(len(DISTRIBUTION_TYPE)):
    GUI.Radiobutton(
        frequency_frame,
        text = DISTRIBUTION_TYPE[i],
        padx = 20, 
        variable = temp_packet_generation_distribution, 
        value = i,
        command = p_check_distribution,
        ).grid(column = 1, sticky = GUI.W)

GUI.Label(frequency_frame, text = 'Parameter 1').grid(column = 1)
p_parameter_one_input = GUI.Entry(frequency_frame)
p_parameter_one_input.insert(0, 0.0)
p_parameter_one_input.grid(column = 1)
GUI.Label(frequency_frame, text = 'Parameter 2').grid(column = 1)
p_parameter_two_input = GUI.Entry(frequency_frame)
p_parameter_two_input.insert(0, 0.0)
p_parameter_two_input.grid(column = 1)
GUI.Label(frequency_frame, text = 'Parameter 3').grid(column = 1)
p_parameter_three_input = GUI.Entry(frequency_frame)
p_parameter_three_input.insert(0, 0.0)
p_parameter_three_input.grid(column = 1)

p_check_distribution()

frequency_frame.grid(column = 1, row = 1, padx = 15, pady = 5)

##
# Other Parameters
##

packet_generated = 0
packet_lost = 0
total_queuing_delay = 0.0
total_transmission_delay = 0.0
throughput = 0.0

BUFFER_CAPACITY = 0
RESOURCE_POOL_CAPACITY = 0

GUI.Label(parameter_frame, text = 'Buffer Capacity').grid(column = 0, row = 0, padx = 20, sticky = GUI.N)
buffer_capacity_input = GUI.Entry(parameter_frame)
buffer_capacity_input.insert(0, 0)
buffer_capacity_input.grid(column = 0, row = 1, padx = 20, sticky = GUI.W)
GUI.Label(parameter_frame, text = 'Resource Pool Capacity').grid(column = 1, row = 0, padx = 20, sticky = GUI.N)
resource_pool_capacity_input = GUI.Entry(parameter_frame)
resource_pool_capacity_input.insert(0, 0)
resource_pool_capacity_input.grid(column = 1, row = 1, padx = 20, sticky = GUI.W)

parameter_frame.grid(row = 2, columnspan = 2, pady = 5)

##
# Accounting Method
##

ACCOUNTING_METHOD = 0
temp_accounting_method = GUI.IntVar()

GUI.Label(
    accounting_method_frame,
    text = 'Accounting Method',
    justify = GUI.LEFT,
    padx = 20,
    ).grid(column = 0)

accounting_methods = ['(0) FIFO', '(1) LIFO', '(2) RO']

for i in range(len(accounting_methods)):
    GUI.Radiobutton(
        accounting_method_frame,
        text = accounting_methods[i],
        padx = 20, 
        variable = temp_accounting_method,
        value = i,
        ).grid(column = 0, sticky = GUI.W)

accounting_method_frame.grid(column = 0, row = 3)

##
# Request Method
##

REQUEST_METHOD = 0
temp_request_method = GUI.IntVar()

GUI.Label(
    request_method_frame,
    text = 'Request Method',
    justify = GUI.LEFT,
    padx = 20,
    ).grid(column = 0)

request_methods = ['(0) Lowest Load', '(1) Random', '(2) Order', '(3) Orderly loop']

for i in range(len(request_methods)):
    GUI.Radiobutton(
        request_method_frame,
        text = request_methods[i],
        padx = 20,
        variable = temp_request_method,
        value = i,
        ).grid(column = 0, sticky = GUI.W)

request_method_frame.grid(column = 1, row = 3)

##
# Matplotlib
##

graph_dict = {
    'average_queuing_delay': [],
    'average_transmission_delay': [],
    'packet_lost_rate': [],
    'throughput': []
}

for i in range(10000):
    for key in graph_dict:
        graph_dict[key].append(0)

figure = plt.Figure(figsize = (8,6), dpi = 100)

aqd = figure.add_subplot(2, 2, 1)
atd = figure.add_subplot(2, 2, 2)
plr = figure.add_subplot(2, 2, 3)
tp = figure.add_subplot(2, 2, 4)

canvas = mpl.backends.backend_tkagg.FigureCanvasTkAgg(figure, master= main)
canvas.show()
canvas.get_tk_widget().grid(row = 1, column = 2, rowspan = 4, padx = 20, pady = 20)

##
# Control
##

def graph(env, graph_dict):
    global packet_generated
    global packet_lost
    global total_queuing_delay
    global total_transmission_delay
    for i in range(10000):
        try:
            graph_dict['average_queuing_delay'][i] = (total_queuing_delay / (packet_generated - packet_lost))
        except ZeroDivisionError:
            graph_dict['average_queuing_delay'][i] = 0
        try:
            graph_dict['average_transmission_delay'][i] = (total_transmission_delay / (packet_generated - packet_lost))
        except ZeroDivisionError:
            graph_dict['average_transmission_delay'][i] = 0
        try:
            graph_dict['packet_lost_rate'][i] = (packet_lost / packet_generated * 100)
        except ZeroDivisionError:
            graph_dict['packet_lost_rate'][i] = 0
        try:
            graph_dict['throughput'][i] = (packet_generated - packet_lost) / env.now
        except ZeroDivisionError:
            graph_dict['throughput'][i] = 0
        yield env.timeout(1)

def clear_graph():
    global aqd
    global atd
    global plr
    global tp
    global canvas

    aqd.cla()
    aqd.set_ylabel('Average Queuing Delay')
    aqd.set_xlabel('Time')

    atd.cla()
    atd.set_ylabel('Average Transmission Delay')
    atd.set_xlabel('Time')

    plr.cla()
    plr.set_ylabel('Packet Lost Rate')
    plr.set_xlabel('Time')

    tp.cla()
    tp.set_ylabel('Throughput')
    tp.set_xlabel('Time')
    
    canvas.show()
    canvas.get_tk_widget().grid(row = 1, column = 2, rowspan = 4, padx = 20, pady = 20)

def start_simulation():
    global graph_dict
    global figure
    global aqd
    global qtd
    global plr
    global tp
    global canvas
    env = simpy.Environment()
    link = []
    for i in range(RESOURCE_POOL_CAPACITY):
        link.append(simpy.PriorityResource(env, capacity = 1))
    env.process(transmit(env, link))
    env.process(graph(env, graph_dict))
    env.run(until = 10000)

    aqd.plot(range(10000), graph_dict['average_queuing_delay'])
    aqd.set_ylabel('Average Queuing Delay')
    aqd.set_xlabel('Time')

    atd.plot(range(10000), graph_dict['average_transmission_delay'])
    atd.set_ylabel('Average Transmission Delay')
    atd.set_xlabel('Time')

    plr.plot(range(10000), graph_dict['packet_lost_rate'])
    plr.set_ylabel('Packet Lost Rate')
    plr.set_xlabel('Time')

    tp.plot(range(10000), graph_dict['throughput'])
    tp.set_ylabel('Throughput')
    tp.set_xlabel('Time')

    canvas.show()
    canvas.get_tk_widget().grid(row = 1, column = 2, rowspan = 4, padx = 20, pady = 20)

    print('Total packet generated', packet_generated)
    print('Total packet lost', packet_lost)
    print('Total Queuing Delay', total_queuing_delay)
    print('Total Transmission Delay', total_transmission_delay)
    print('Average Queuing Dealy', str(total_queuing_delay / (packet_generated - packet_lost)))
    print('Average Transmission Dealy', str(total_transmission_delay / (packet_generated - packet_lost)))
    print('Packet lost rate', str(packet_lost / packet_generated * 100), '%')
    print('Average Throughput', str((packet_generated - packet_lost) / 10000))

def apply_changes():
    global temp_packet_generation_distribution
    global temp_bandwidth_distribution
    global temp_accounting_method
    global temp_request_method
    global PACKET_GENERATION_DISTRIBUTION
    global P_PARAMETER_ONE
    global P_PARAMETER_TWO
    global P_PARAMETER_THREE
    global BANDWIDTH_DISTRIBUTION
    global B_PARAMETER_ONE
    global B_PARAMETER_TWO
    global B_PARAMETER_THREE
    global TOTAL_TIME
    global BUFFER_CAPACITY
    global ACCOUNTING_METHOD
    global REQUEST_METHOD
    global RESOURCE_POOL_CAPACITY
    global buffer_capacity_input
    global resource_pool_capacity_input
    global p_parameter_one_input
    global p_parameter_two_input
    global p_parameter_three_input
    global b_parameter_one_input
    global b_parameter_two_input
    global b_parameter_three_input

    def is_integer(value):
        try:
            int(value)
            return True
        except:
            return False

    def is_float(value):
        try:
            float(value)
            return True
        except:
            return False

    integer_input = [buffer_capacity_input, resource_pool_capacity_input]

    for i in range(len(integer_input)):
        if not is_integer(integer_input[i].get()):
            print('Something wrong, please check your input. 1')
            return

    float_input = [
        p_parameter_one_input, p_parameter_two_input, p_parameter_three_input,
        b_parameter_one_input, b_parameter_two_input, b_parameter_three_input,
    ]

    for i in range(len(float_input)):
        if not is_float(float_input[i].get()):
            print('Something wrong, please check your input. 2')
            return

    temp = [temp_packet_generation_distribution, temp_bandwidth_distribution, temp_accounting_method, temp_request_method]

    PACKET_GENERATION_DISTRIBUTION = int(temp[0].get())
    BANDWIDTH_DISTRIBUTION = int(temp[1].get())
    ACCOUNTING_METHOD = int(temp[2].get())
    REQUEST_METHOD = int(temp[3].get())

    P_PARAMETER_ONE = float(float_input[0].get())
    P_PARAMETER_TWO = float(float_input[1].get())
    P_PARAMETER_THREE = float(float_input[2].get())
    B_PARAMETER_ONE = float(float_input[3].get())
    B_PARAMETER_TWO = float(float_input[4].get())
    B_PARAMETER_THREE = float(float_input[5].get())

    BUFFER_CAPACITY = int(integer_input[0].get())
    RESOURCE_POOL_CAPACITY = int(integer_input[1].get())

    global_variables = {
        'PACKET_GENERATION_DISTRIBUTION': PACKET_GENERATION_DISTRIBUTION,
        'P_PARAMETER_ONE': P_PARAMETER_ONE,
        'P_PARAMETER_TWO': P_PARAMETER_TWO,
        'P_PARAMETER_THREE': P_PARAMETER_THREE,
        'BANDWIDTH_DISTRIBUTION': BANDWIDTH_DISTRIBUTION,
        'B_PARAMETER_ONE': B_PARAMETER_ONE,
        'B_PARAMETER_TWO': B_PARAMETER_TWO,
        'B_PARAMETER_THREE': B_PARAMETER_THREE,
        'BUFFER_CAPACITY': BUFFER_CAPACITY,
        'RESOURCE_POOL_CAPACITY': RESOURCE_POOL_CAPACITY,
        'ACCOUNTING_METHOD': ACCOUNTING_METHOD,
        'REQUEST_METHOD': REQUEST_METHOD,
    }

    for key in global_variables:
        print(key, '->', global_variables[key])

GUI.Button(button_frame, text = 'Apply', command = apply_changes).grid(column = 0, row = 0)
GUI.Button(button_frame, text = 'Start', command = start_simulation).grid(column = 1, row = 0, padx = 15)
GUI.Button(button_frame, text = 'Clear', command = clear_graph).grid(column = 2, row = 0)
button_frame.grid(row = 4, columnspan = 2, pady = 10)

##
# Start Main loop
##
print('Network Simulator')
print('- Console -')
main.mainloop()