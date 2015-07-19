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

##
# Distributions
##

PACKET_GENERATION_DISTRIBUTION = GUI.IntVar()
P_PARAMETER_ONE = GUI.DoubleVar()
P_PARAMETER_TWO = GUI.DoubleVar()
P_PARAMETER_THREE = GUI.DoubleVar()

BANDWIDTH_DISTRIBUTION = GUI.IntVar()
B_PARAMETER_ONE = GUI.DoubleVar()
B_PARAMETER_TWO = GUI.DoubleVar()
B_PARAMETER_THREE = GUI.DoubleVar()

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
        variable = BANDWIDTH_DISTRIBUTION, 
        value = i,
        ).grid(column = 0, sticky = GUI.W)

GUI.Label(bandwidth_frame, text = 'Parameter 1').grid(column = 0)
GUI.Entry(bandwidth_frame).grid(column = 0)
GUI.Label(bandwidth_frame, text = 'Parameter 2').grid(column = 0)
GUI.Entry(bandwidth_frame).grid(column = 0)
GUI.Label(bandwidth_frame, text = 'Parameter 3').grid(column = 0)
GUI.Entry(bandwidth_frame).grid(column = 0)

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
        variable = PACKET_GENERATION_DISTRIBUTION, 
        value = i,
        ).grid(column = 1, sticky = GUI.W)

GUI.Label(frequency_frame, text = 'Parameter 1').grid(column = 1)
GUI.Entry(frequency_frame).grid(column = 1)
GUI.Label(frequency_frame, text = 'Parameter 2').grid(column = 1)
GUI.Entry(frequency_frame).grid(column = 1)
GUI.Label(frequency_frame, text = 'Parameter 3').grid(column = 1)
GUI.Entry(frequency_frame).grid(column = 1)

frequency_frame.grid(column = 1, row = 1, padx = 15, pady = 5)

##
# Other Parameters
##

GUI.Label(parameter_frame, text = 'Simulation Time').grid(column = 1)
GUI.Entry(parameter_frame).grid(column = 1)
GUI.Label(parameter_frame, text = 'Buffer Capacity').grid(column = 1)
GUI.Entry(parameter_frame).grid(column = 1)
GUI.Label(parameter_frame, text = 'Resource Pool Capacity').grid(column = 1)
GUI.Entry(parameter_frame).grid(column = 1)

parameter_frame.grid(row = 2, pady = 5)

##
# Control Buttons
##

GUI.Button(button_frame, text = 'Start Simulation').grid(row = 3, column = 0)
GUI.Button(button_frame, text = 'Pause Simulation').grid(row = 3, column = 1)
button_frame.grid(row = 3, column = 0, columnspan = 2, pady = 5)

##
# Messages
##

textbox = GUI.Text(message_frame, height=8, width=25)
textbox.grid(row = 3, column = 1)
message_frame.grid(row = 2, column = 1, padx = 15)
textbox.insert(GUI.END, "Network Simulator\n prototype")

##
# Matplotlib
##

textbox2 = GUI.Text(main, height=10, width=100)
textbox2.grid(row = 1, column = 2, padx = 20)


main.mainloop()