# coding: utf-8

# In[61]:


#!/usr/bin/env python
'''
Pymodbus Synchrnonous Client Test with Dynasonic DXN Energy Meter
--------------------------------------------------------------------------
The following is an example of how to use the synchronous modbus client
implementation from pymodbus. This has been adapted from a sample script
at https://pythonhosted.org/pymodbus/examples/synchronous-client.html
_Additional Note from sample script:
It should be noted that the client can also be used with
the guard construct that is available in python 2.5 and up::
    with ModbusClient('127.0.0.1') as client:
        result = client.read_coils(1,10)
        print result
***Created 2018-07-22 by Chris Weyandt
'''

#---------------------------------------------------------------------------#
# import the required server implementation
#---------------------------------------------------------------------------#
from pymodbus.client.sync import ModbusTcpClient
#from pymodbus.client.sync import ModbusUdpClient as ModbusClient
from pymodbus.client.sync import ModbusSerialClient

#additional imports for conversions
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
import configparser
import yaml
import logging


class Modbus_Driver(object):
    def __init__(self, config_file, config_section=None):
        # Use a config section if the config file is being shared with other
        # parts of a project.
        if (config_section==None):
            modbus_section = 'modbus'
        with open(config_file) as f:
            # use safe_load instead load for security reasons
            modbusConfig = yaml.safe_load(f)

        self.MODBUS_TYPE = modbusConfig[modbus_section]['modbus_type']
        self.UNIT_ID = modbusConfig[modbus_section]['UNIT_ID']

        # Start logging if enabled in config
        self.LOGGING_FLAG = modbusConfig[modbus_section]['enable_logging']
        if self.LOGGING_FLAG == True:
            #Start client logging for trouble shooting
            logging.basicConfig()
            log = logging.getLogger()
            log.setLevel(logging.DEBUG)

        # Start appropriate client based on the type specified in the config
        if self.MODBUS_TYPE == 'serial':
            print('serial')
            self.METHOD = modbusConfig[modbus_section]['method']
            self.SERIAL_PORT = modbusConfig[modbus_section]['serial_port']
            self.STOPBITS = modbusConfig[modbus_section]['stopbits']
            self.BYTESIZE = modbusConfig[modbus_section]['bytesize']
            self.PARITY = modbusConfig[modbus_section]['parity']
            self.BAUDRATE = modbusConfig[modbus_section]['baudrate']
        elif self.MODBUS_TYPE == 'tcp':
            self.IP_ADDRESS = modbusConfig[modbus_section]['ip']
            self.PORT = modbusConfig[modbus_section]['tcp_port']
        else:
            print("Invalid modbus type")
            exit()

        # Set the byte order as big or little endian
        if modbusConfig[modbus_section]['byte_order'] == 'big':
            self.BYTE_ORDER = Endian.Big
        elif modbusConfig[modbus_section]['byte_order'] == 'little':
            self.BYTE_ORDER = Endian.Little
        else:
            print("invalid byte order") # change to except later
            exit()

        # Set the word order as big or little endian
        if modbusConfig[modbus_section]['word_order'] == 'big':
            print("big")
            self.WORD_ORDER = Endian.Big
        elif modbusConfig[modbus_section]['word_order'] == 'little':
            self.WORD_ORDER = Endian.Little
        else:
            print("invalid byte order") # change to except later
            exit()

        # Read in all registers specified in the YAML config
        self.coil_register_dict = modbusConfig[modbus_section]['coil_registers']
        self.discrete_register_dict = modbusConfig[modbus_section]['discrete_registers']
        self.holding_register_dict = modbusConfig[modbus_section]['holding_registers']
        self.input_register_dict = modbusConfig[modbus_section]['input_registers']

        # Apply register offset if specified
        self.OFFSET_REGISTERS = modbusConfig[modbus_section]['OFFSET_REGISTERS']
        for key in self.holding_register_dict:
            self.holding_register_dict[key][0] -= self.OFFSET_REGISTERS


    def initialize_modbus(self):
        """
        initalize correct client according to type specified in config:
            'tcp' or 'serial'
        """
        if self.MODBUS_TYPE == 'serial':
            self.client= ModbusSerialClient(method = self.METHOD, port=self.SERIAL_PORT,stopbits = self.STOPBITS, bytesize = self.BYTESIZE, parity = self.PARITY, baudrate= self.BAUDRATE)
            connection = self.client.connect()

        if self.MODBUS_TYPE == 'tcp':
            self.client = ModbusTcpClient(self.IP_ADDRESS,port=self.PORT)



    def write_single_register(self,register,value):
        """
        :param register: address of reigster to write
        :param value: Unsigned short
        :returns: Status of write
        """
        response = self.client.write_register(register,value,unit= self.UNIT_ID)
        return response

    def write_register(self,register_name,value):
        """
        :param register_name: register key from holding register dictionary
            generated by yaml config
        :param value: value to write to register
        :returns: -- Nothing
        """
        builder = BinaryPayloadBuilder(byteorder=self.BYTE_ORDER,
            wordorder=self.WORD_ORDER)
        if (self.holding_register_dict[register_name][1] == '8int'):
            builder.add_8bit_int(value)
        elif (self.holding_register_dict[register_name][1] == '8uint'):
            builder.add_8bit_uint(value)
        elif (self.holding_register_dict[register_name][1] == '16int'):
            builder.add_16bit_int(value)
        elif (self.holding_register_dict[register_name][1] == '16uint'):
            builder.add_16bit_uint(value)
        elif (self.holding_register_dict[register_name][1] == '32int'):
            builder.add_32bit_int(value)
        elif (self.holding_register_dict[register_name][1] == '32uint'):
            builder.add_32bit_uint(value)
        elif (self.holding_register_dict[register_name][1] == '32float'):
            builder.add_32bit_float(value)
        elif (self.holding_register_dict[register_name][1] == '64int'):
            builder.add_64bit_int(value)
        elif (self.holding_register_dict[register_name][1] == '64uint'):
            builder.add_64bit_uint(value)
        elif (self.holding_register_dict[register_name][1] == '64float'):
            builder.add_64bit_float(value)
        else:
            print("Bad type")
            exit()
        payload = builder.build()
        self.client.write_registers(self.holding_register_dict[register_name][0], payload, skip_encode=True, unit = self.UNIT_ID)

    def write_coil(self,register,value):
        """
        :param register_name: register key from holding register dictionary
            generated by yaml config
        :param value: value to write to register
        :returns:
        """
        response = self.client.write_coil(register,value,unit= self.UNIT_ID)
        return response

    def read_coil(self,register):
        """
        :param register: coil register address to read
        :returns: value stored in coil register
        """
        rr = self.client.read_coils(register, 1, unit= self.UNIT_ID)
        return rr.bits[0]

    def read_discrete(self,register):
        """
        :param register: discrete register address to read
        :returns: value stored in coil register
        """
        rr = self.client.read_discrete_inputs(register, count=1,unit= self.UNIT_ID)
        return rr.bits[0]

    def read_register_raw(self,register,length):
        """
        :param register: base holding register address to read
        :param length: amount of registers to read to encompass all of the data necessary
            for the type
        :returns: A deferred response handle
        """
        response = self.client.read_holding_registers(register,length,unit= self.UNIT_ID)
        return response

    def read_input_raw(self,register,length):
        """
        :param register: base input register address to read
        :param length: amount of registers to read to encompass all of the data necessary
            for the type
        :returns: A deferred response handle
        """
        response = self.client.read_input_registers(register,length,unit= self.UNIT_ID)
        return response

    def decode_register(self,register,type):
        """
        :param register: holding register address to retrieve
        :param type: type to interpret the registers retrieved as
        :returns: data in the type specified

        Based on the type provided, this function retrieves the values contained
        in the register address specfied plus the amount necessary to encompass
        the the type. For example, if 32int is specified with an address of 200
        the registers accessed would be 200 and 201.

        The types accepted are listed in the table below along with their length
        |   Type          | Length (registers) |
        | ------------- |:------------------:|
        |        ignore |                  1 |
        |          8int |                  1 |
        |         8uint |                  1 |
        |         16int |                  1 |
        |        16uint |                  1 |
        |         32int |                  2 |
        |        32uint |                  2 |
        |       32float |                  2 |
        |         64int |                  4 |
        |        64uint |                  4 |
        |       64float |                  4 |
        """

        #omitting string for now since it requires a specified length
        if type == '8int':
            rr = self.read_register_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_8bit_int()

        elif type == '8uint':
            rr = self.read_register_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_8bit_uint()
        elif type == '16int':
            rr = self.read_register_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_16bit_int()
        elif type == '16uint':
            rr = self.read_register_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_16bit_uint()
        elif type == '32int':
            rr = self.read_register_raw(register,2)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_32bit_int()
        elif type == '32uint':
            rr = self.read_register_raw(register,2)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_32bit_uint()
        elif type == '32float':
            rr = self.read_register_raw(register,2)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_32bit_float()
        elif type == '64int':
            rr = self.read_register_raw(register,4)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_64bit_int()
        elif type == '64uint':
            rr = self.read_register_raw(register,4)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_64bit_uint()
        elif type == 'ignore':
            rr = self.read_register_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.skip_bytes(8)
        elif type == '64float':
            rr = self.read_register_raw(register,4)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_64bit_float()
        else:
            print("Wrong type specified")
            exit()

        return output

    def decode_input_register(self,register,type):
        """
        :param register: input register address to retrieve
        :param type: type to interpret the registers retrieved as
        :returns: data in the type specified

        Based on the type provided, this function retrieves the values contained
        in the register address specfied plus the amount necessary to encompass
        the the type. For example, if 32int is specified with an address of 200
        the registers accessed would be 200 and 201.

        The types accepted are listed in the table below along with their length
        |   Type          | Length (registers) |
        | ------------- |:------------------:|
        |        ignore |                  1 |
        |          8int |                  1 |
        |         8uint |                  1 |
        |         16int |                  1 |
        |        16uint |                  1 |
        |         32int |                  2 |
        |        32uint |                  2 |
        |       32float |                  2 |
        |         64int |                  4 |
        |        64uint |                  4 |
        |       64float |                  4 |
        """

        #omitting string for now since it requires a specified length
        if type == '8int':
            rr = self.read_input_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_8bit_int()

        elif type == '8uint':
            rr = self.read_input_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_8bit_uint()
        elif type == '16int':
            rr = self.read_input_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_16bit_int()
        elif type == '16uint':
            rr = self.read_input_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_16bit_uint()
        elif type == '32int':
            rr = self.read_input_raw(register,2)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_32bit_int()
        elif type == '32uint':
            rr = self.read_input_raw(register,2)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_32bit_uint()
        elif type == '32float':
            rr = self.read_input_raw(register,2)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_32bit_float()
        elif type == '64int':
            rr = self.read_input_raw(register,4)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_64bit_int()
        elif type == '64uint':
            rr = self.read_input_raw(register,4)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_64bit_uint()
        elif type == 'ignore':
            rr = self.read_input_raw(register,1)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.skip_bytes(8)
        elif type == '64float':
            rr = self.read_input_raw(register,4)
            decoder = BinaryPayloadDecoder.fromRegisters(
                    rr.registers,
                    byteorder=self.BYTE_ORDER,
                    wordorder=self.WORD_ORDER)
            output = decoder.decode_64bit_float()
        else:
            print("Wrong type specified")
            exit()

        return output


    def get_data(self):
        """
        :returns: Dictionary containing the value retrieved for each register
        contained in the YAML config file, register names cannot be repeated
        or the register will be overwritten
        """

        output = {}
        for key in self.coil_register_dict:
            output[key] = self.read_coil(self.coil_register_dict[key][0])

        for key in self.discrete_register_dict:
            output[key] = self.read_discrete(self.discrete_register_dict[key][0])

        for key in self.holding_register_dict:
            output[key] = self.decode_register(self.holding_register_dict[key][0],self.holding_register_dict[key][1])

        for key in self.input_register_dict:
            output[key] = self.decode_input_register(self.input_register_dict[key][0],self.input_register_dict[key][1])

        return output

    def kill_modbus(self):
        """
        Closes connection with Modbus Slave
        """
        self.client.close()
