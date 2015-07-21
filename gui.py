import simpy
import random
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
import tkinter as GUI

##
# Parameters needed
# 
# Choose:
# - Probability distribution type of the bandwidth
# - Probability distribution type of the packet generation frequency
# - Accounting method
# - Request method
#
# Input:
# - Six parameters of two distributions
# - Simulation time
# - Buffer capacity (integer)
# - Resource pool capacity (integer)
##

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
    '0) uniform',
    '1) triangular',
    '2) betavariate',
    '3) expovariate',
    '4) gammavariate',
    '5) gauss',
    '6) lognormvariate',
    '7) normalvariate',
    '8) vonmisesvariate',
    '9) paretovariate',
    '10) weibullvariate',
]

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
        ).grid(column = 0, sticky = GUI.W)

GUI.Label(bandwidth_frame, text = 'Parameter 1 (Required)').grid(column = 0)
b_parameter_one_input = GUI.Entry(bandwidth_frame)
b_parameter_one_input.insert(0, 0.0)
b_parameter_one_input.grid(column = 0)
GUI.Label(bandwidth_frame, text = 'Parameter 2 (Optional)').grid(column = 0)
b_parameter_two_input = GUI.Entry(bandwidth_frame)
b_parameter_two_input.insert(0, 0.0)
b_parameter_two_input.grid(column = 0)
GUI.Label(bandwidth_frame, text = 'Parameter 3 (Optional)').grid(column = 0)
b_parameter_three_input = GUI.Entry(bandwidth_frame)
b_parameter_three_input.insert(0, 0.0)
b_parameter_three_input.grid(column = 0)

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
        ).grid(column = 1, sticky = GUI.W)

GUI.Label(frequency_frame, text = 'Parameter 1 (Required)').grid(column = 1)
p_parameter_one_input = GUI.Entry(frequency_frame)
p_parameter_one_input.insert(0, 0.0)
p_parameter_one_input.grid(column = 1)
GUI.Label(frequency_frame, text = 'Parameter 2 (Optional)').grid(column = 1)
p_parameter_two_input = GUI.Entry(frequency_frame)
p_parameter_two_input.insert(0, 0.0)
p_parameter_two_input.grid(column = 1)
GUI.Label(frequency_frame, text = 'Parameter 3 (Optional)').grid(column = 1)
p_parameter_three_input = GUI.Entry(frequency_frame)
p_parameter_three_input.insert(0, 0.0)
p_parameter_three_input.grid(column = 1)

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

accounting_methods = ['0) FIFO', '1) LIFO', '2) RO']

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

request_methods = ['0) Lowest Load', '1) Random', '2) Order', '3) Orderly loop']

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
# Control Buttons
##

def apply_changes():
    global temp_packet_generation_distribution
    global temp_bandwidth_distribution
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

    temp = [temp_packet_generation_distribution, temp_bandwidth_distribution]
    no_check = [PACKET_GENERATION_DISTRIBUTION, BANDWIDTH_DISTRIBUTION]
    for i in range(len(no_check)):
        no_check[i] = temp[i].get()

    check_integer = [BUFFER_CAPACITY, ACCOUNTING_METHOD, REQUEST_METHOD]
    check_float = [P_PARAMETER_ONE, P_PARAMETER_TWO, P_PARAMETER_THREE, B_PARAMETER_ONE, B_PARAMETER_TWO, B_PARAMETER_THREE]

GUI.Button(button_frame, text = 'Apply Changes').grid(column = 0, row = 0)
GUI.Button(button_frame, text = 'Start').grid(column = 1, row = 0)
GUI.Button(button_frame, text = 'Pause').grid(column = 2, row = 0)
button_frame.grid(row = 4, columnspan = 2, pady = 10)

##
# Matplotlib
##

f = plt.Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)
x = range(10)
y = range(10)
a.plot(x, y)

canvas = mpl.backends.backend_tkagg.FigureCanvasTkAgg(f, master= main)
canvas.show()
canvas.get_tk_widget().grid(row = 1, column = 2, padx = 20)

##
# Start Main loop
##
main.mainloop()