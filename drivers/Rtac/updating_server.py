#!/usr/bin/env python
"""
Pymodbus Server With Updating Thread
--------------------------------------------------------------------------

This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::

    from threading import Thread

    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
"""
# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
import yaml
import random
import argparse
from struct import *

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #

def write_float(context_in,register,address,value,slave_id=0x0):
    """ A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")

    context = context_in[0]
    slave_id = 0x00

    # Floating point to two integers
    i1, i2 = unpack('<HH',pack('f',value))

    values = [i1,i2]
    log.debug("new values: " + str(values))
    context[slave_id].setValues(register, address, values)

def write_32int(context_in,register,address,value,slave_id=0x0):
    """ A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")

    context = context_in[0]
    #register = 3
    slave_id = 0x00
    print(value)
    # 32 bit integer to two 16 bit short integers for writing to registers
    i1, i2 = unpack('<HH',pack('i',value))
    values = [i1,i2]
    print(values)
    context[slave_id].setValues(register, address, values)

def initialize_registers(a,slave_id,holding_float_dict,holding_int32_dict,
    holding_int16_dict,input_float_dict,input_int32_dict,input_int16_dict,
    coil_dict, discrete_dict):
    #TODO update context stuff
    context = a[0]


    for key, reg_list in holding_float_dict.items():
        # Go through each float register and set to initial value
        write_float(a,3,reg_list[0],reg_list[1])

    for key, reg_list in holding_int32_dict.items():
        # Go through each int32 register and set to initial value
        write_32int(a,3,reg_list[0],reg_list[1])

    for key, reg_list in holding_int16_dict.items():
        # Go through each int16 register and set to initial value
        context[slave_id].setValues(3, reg_list[0], [reg_list[1]])

    for key, reg_list in input_float_dict.items():
        # Go through each float register and set to initial value
        write_float(a,4,reg_list[0],reg_list[1])

    for key, reg_list in input_int32_dict.items():
        # Go through each int32 register and set to initial value
        write_32int(a,4,reg_list[0],reg_list[1])

    for key, reg_list in input_int16_dict.items():
        # Go through each int16 register and set to initial value
        context[slave_id].setValues(4, reg_list[0], [reg_list[1]])

    for key1, reg_list_coil in coil_dict.items():
        context[slave_id].setValues(1, reg_list_coil[0], [reg_list_coil[1]])

    for key2, reg_list_discrete in discrete_dict.items():
        context[slave_id].setValues(2, reg_list_discrete[0], [reg_list_discrete[1]])

def update_float_registers(a,register,slave_id,register_dict_float,
    random_range, ramp_slope):
    #TODO figure out the context situation
    context = a[0]
    slope = ramp_slope
    for key, reg_list in register_dict_float.items():
        # Go through each float register and apply the function specified by the
        # config file.

        if(reg_list[2] == 'random'):

            new_val = random.uniform(random_range[0],random_range[1])
            write_float(a,register,reg_list[0],new_val)


        elif (reg_list[2] == 'ramp'):
            # get previous values from the two registers which combine to the
            # float value
            values = context[slave_id].getValues(register, (reg_list[0]), count=2)
            #convert two short integers from register into a float value
            previous_float_val = unpack('f',pack('<HH',values[0],values[1]))[0]
            #Add in slope to previous value
            newval = previous_float_val + 1*slope
            write_float(a,register,reg_list[0],newval)
            print(newval)

        elif (reg_list[2] == 'none'):
            print("value unchanged")
        else:
            raise e
        print(key, 'corresponds to', reg_list[0])

def update_int32_registers(a,register,slave_id,register_dict_int32,
    random_range, ramp_slope):
    slope = ramp_slope
    context = a[0]
    for key, reg_list in register_dict_int32.items():
        # Go through each float register and apply the function specified by the
        # config file.

        if(reg_list[2] == 'random'):
            new_val = random.randint(random_range[0],random_range[1])
            print(new_val)
            write_32int(a,3,reg_list[0],new_val)
        elif (reg_list[2] == 'ramp'):

            # Get previous values that represent the 32 bit integer as two
            # short integers
            values  = context[slave_id].getValues(register, reg_list[0], count=2)
            print(values)
            #change short integers to 32 bit integer

            previous_integer_val = unpack('i',pack('<HH',int(values[0]),int(values[1])))[0]

            # Add previous value to slope
            new_val = previous_integer_val + 1*slope

            #write value back to register
            print(new_val)

            write_32int(a,register,reg_list[0],int(new_val))
        elif (reg_list[2] == 'none'):
            print("value unchanged")
        else:
            raise e
        print(key, 'corresponds to', reg_list[0])

def update_int16_registers(a,register,slave_id,register_dict_int16,
    random_range, ramp_slope):

    #TODO FIX ISSUE IN RAMP FOR INPUT REG
    context = a[0]
    slope = ramp_slope
    for key, reg_list in register_dict_int16.items():
        # Go through each float register and apply the function specified by the
        # config file.

        if(reg_list[2] == 'random'):
            new_val = random.randint(random_range[0],random_range[1])
            context[slave_id].setValues(register, reg_list[0], [new_val])

        elif (reg_list[2] == 'ramp'):
            # Get previous values that represent the 32 bit integer as two
            # short integers
            values  = context[slave_id].getValues(register, reg_list[0], count=1)
            new_val = values[0] + slope*1
            context[slave_id].setValues(register, reg_list[0], [int(new_val)])
        elif (reg_list[2] == 'none'):
            print("value unchanged")
        else:
            raise e
        print(key, 'corresponds to', reg_list[0])

def update_coil_registers(a,slave_id,coil_dict):
    context = a[0]
    for key1, reg_list_coil in coil_dict.items():
        # Go through each coil register and set the value to the opposite of the
        # curent value if the third item of the list is set to true in the config
        if reg_list_coil[2] == 'True':
            print("FLIP COILS!!!")
            value = context[slave_id].getValues(1, reg_list_coil[0], count=1)
            print(value[0])
            if (value[0] == 1):
                value[0] = 0
            else:
                value[0]  = 1
            print(value[0])
            context[slave_id].setValues(1, reg_list_coil[0], [value[0]])

def update_discrete_register(a,slave_id,discrete_dict):
    print("We are in the update of discrete registers")
    context = a[0]
    for key2, reg_list_discrete in discrete_dict.items():
        # Go through each coil register and set the value to the opposite of the
        # curent value if the third item of the list is set to true in the config
        if reg_list_discrete[2] == 'True':
            print("FLIP DISCRETE!!!")
            value = context[slave_id].getValues(2, reg_list_discrete[0], count=1)
            print(value[0])
            if (value[0] == 1):
                value[0] = 0
            else:
                value[0]  = 1
            print(value[0])
            context[slave_id].setValues(2, reg_list_discrete[0], [value[0]])



def updating_writer(a,holding_float_dict,holding_int32_dict,holding_int16_dict,
    input_float_dict,input_int32_dict,input_int16_dict,
    coil_dict,discrete_dict,random_range,ramp_slope):
    #TODO automatically size the context and check for the size being too large

    """ A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    """
    #log.debug("updating the context")
    context = a[0]
    slave_id = 0x00
    address = 0x0

    # Update the coil register according to the flip boolean in the coil_dict
    update_coil_registers(a,slave_id,coil_dict)

    # # Update the discrete register according to the flip boolean in the discrete_dict
    update_discrete_register(a,slave_id,discrete_dict)

    # Update each holding register type according to function specified in config
    update_float_registers(a,3,slave_id,holding_float_dict,
        random_range, ramp_slope)

    update_int32_registers(a,3,slave_id,holding_int32_dict,
        random_range, ramp_slope)

    update_int16_registers(a,3,slave_id,holding_int16_dict,
        random_range, ramp_slope)


    # Update each input register type according to function specified in config
    update_float_registers(a,4,slave_id,input_float_dict,
        random_range, ramp_slope)

    update_int32_registers(a,4,slave_id,input_int32_dict,
        random_range, ramp_slope)

    update_int16_registers(a,4,slave_id,input_int16_dict,
        random_range, ramp_slope)


def run_updating_server(config_in, config_section=None):
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #
    if (config_section==None):
        modbus_section = 'server'


    with open(config_in) as f:
        # use safe_load instead load
        modbusConfig = yaml.safe_load(f)

    PORT = modbusConfig[modbus_section]['port']
    DEFINED_BLOCK = modbusConfig[modbus_section]['use_block_size']

    random_range = modbusConfig[modbus_section]['random_range']
    ramp_slope = modbusConfig[modbus_section]['ramp_slope']

    holding_float_dict = modbusConfig[modbus_section]['float_holding']
    holding_int32_dict = modbusConfig[modbus_section]['int32_holding']
    holding_int16_dict = modbusConfig[modbus_section]['int16_holding']

    input_float_dict = modbusConfig[modbus_section]['float_input']
    input_int32_dict = modbusConfig[modbus_section]['int32_input']
    input_int16_dict = modbusConfig[modbus_section]['int16_input']

    coil_dict = modbusConfig[modbus_section]['coil_registers']
    discrete_dict = modbusConfig[modbus_section]['discrete_registers']

    if (DEFINED_BLOCK == True):
        # User has defined a custom block and offset, read the settings
        # from the config file.

        print("block size is user defined")
        coil_block_size = modbusConfig[modbus_section]['coil_block_size']
        coil_block_offset = modbusConfig[modbus_section]['coil_block_offset']

        discrete_block_size = modbusConfig[modbus_section]['discrete_block_size']
        discrete_block_offset = modbusConfig[modbus_section]['discrete_block_offset']

        holding_block_size = modbusConfig[modbus_section]['holding_block_size']
        holding_block_offset = modbusConfig[modbus_section]['holding_block_offset']

        input_block_size = modbusConfig[modbus_section]['holding_block_size']
        input_block_offset = modbusConfig[modbus_section]['holding_block_offset']
    else:
        print("use auto calulcator")
        # Calculate size needed for each register type
        holding_block_size = len(holding_float_dict)*2
        holding_block_size += len(holding_int32_dict)*2
        holding_block_size += len(holding_int16_dict)*1

        input_block_size = len(input_float_dict)*2
        input_block_size += len(input_int32_dict)*2
        input_block_size += len(input_int16_dict)*1

        discrete_block_size = len(discrete_dict)
        coil_block_size = len(coil_dict)

        coil_block_offset = 0
        discrete_block_offset = 0
        holding_block_offset = 0
        input_block_offset = 0


    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(discrete_block_offset, [0]*discrete_block_size),
        co=ModbusSequentialDataBlock(coil_block_offset, [0]*coil_block_size),
        hr=ModbusSequentialDataBlock(holding_block_offset, [0]*holding_block_size),
        ir=ModbusSequentialDataBlock(input_block_offset, [0]*input_block_size))
    context = ModbusServerContext(slaves=store, single=True)


    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    #initialize_registers(context,holding_float_dict,holding_int32_dict)

    slave_id = 0x00

    initialize_registers([context],slave_id,holding_float_dict,holding_int32_dict,
        holding_int16_dict,input_float_dict,input_int32_dict,input_int16_dict,
        coil_dict, discrete_dict)

    time = 5
    loop = LoopingCall(f=updating_writer, a=(context,),
        holding_float_dict=(holding_float_dict),
        holding_int32_dict=(holding_int32_dict),
        holding_int16_dict=(holding_int16_dict),
        input_float_dict=(input_float_dict),
        input_int32_dict=(input_int32_dict),
        input_int16_dict=(input_int16_dict),
        coil_dict=(coil_dict),
        discrete_dict=(discrete_dict),
        random_range=(random_range),
        ramp_slope=(ramp_slope))
    loop.start(time, now=False) # initially delay by time
    # Setting address to 127.0.0.1 allows only the local machine to access the
    # Server. Changing to 0.0.0.0 allows for other hosts to connect.
    StartTcpServer(context, identity=identity, address=("0.0.0.0", 5020))

if __name__ == "__main__":
    # read arguments passed at .py file call
    # only argument is the yaml config file which specifies all the details
    # for connecting to the modbus device as well the local and remote
    # influx databases
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="config file")

    args = parser.parse_args()
    config_file = args.config
    #print(config_file)

    run_updating_server(config_in=config_file)
