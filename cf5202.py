#!/usr/bin/python3
# -*- coding:utf-8 -*-

import sys
import crcmod # sudo pip3 install crcmod
import serial
import struct
import binascii
import logging as l
import codecs

from argparse import ArgumentParser


l.basicConfig(level=l.INFO)
#l.basicConfig(level=l.DEBUG)

class RU5202:
    def __init__(self, dev='/dev/ttyUSB0', baud=57600):
        self.ser = serial.Serial(dev, baud)
        
        # This module provides a function factory mkPredefinedCrcFun() and a class PredefinedCrc
        # for calculating CRCs of byte strings using common predefined CRC algorithms.
        # The function factory and the class are very similar to those defined in crcmod,
        # except that the CRC algorithm is specified by a predefined name, 
        # rather than the individual polynomial, reflection, and initial and final-XOR parameters.
        self.crc_func = crcmod.predefined.mkPredefinedCrcFun('crc-16-mcrf4xx')
        

    def command(self, cmd, outData='', addr=0x0):
        """  Send hex command . Return response in hex bytearray
            cmd - command int hex
            addr - address int hex
            outdata - data to write - hex string i.e. '1f2eaacc11'
        """
        outData = bytearray.fromhex(outData)
        l.debug('outData %s' % outData)
        outDataLength = len(outData)

        length = 4 + outDataLength
        length = '%02X' % length
        l.debug('length %s' % length)

        addr = str(addr).zfill(2)
        l.debug('address %s' % addr)

        l.debug('command %s' % hex(cmd))
        cmd = '{:x}'.format(cmd).zfill(2)

        packet = bytearray.fromhex(length+addr+cmd)+outData
        l.debug('packet %s' % packet)

        crc = self.crc_func(packet)
        l.debug('crc %s' % crc)

        packet = packet + struct.pack('<H', crc)
        l.debug('packet %s' % packet)
        
        self.ser.write(packet)
        
        response_length = ord(self.ser.read())
        l.debug('Response length %s' % response_length)
        
        response = self.ser.read(response_length)
        l.debug('Response %s' % response)
        
        response_hexlify = binascii.hexlify(response)
        l.debug('Response hexlify %s' % response_hexlify)

        
        response_array = bytearray(response)
        
        for x in range(len(response_array)):
            l.debug(str(x)+':'+hex(response_array[x]))
        return response_array
        
    def inventory(self, outData):
        l.debug('# inventory %s' % outData)
        """outData :
        1 qvalue: 0-15
        2 session: 0-3
        3 maskmem: 0-255
        4 maskadr-byte1:0-16383 
        5 maskadr-byte2:
        6 masklen:0-255
        7 maskdata - variable (length_in_bytes=masklen/8)
        8 adrtid:
        9 lentid:
        10 target: optional 0x00 or 0x01
        11ant: optional 0x80
        12 scantime: optionalscantime*100ms
        
        ''0e00010000''
        """
        
        
        re = self.command(0x01, outData)
        response = {'addr':re[0], 'cmd':re[1], 'sts':re[2], 'ant':re[3], 'num': re[4], 'epc_len':re[5], 'epc_id':binascii.hexlify(re[6:-3])}
        return response

    def read_data(self):
        l.debug('# read_data')        
        re = self.command(0x02)
        response = {'addr':re[0], 'cmd':re[1], 'data':binascii.hexlify(re[2:])}
        return response

    def write_data(self, outData):
        l.debug('# write_data %s' % outData)        
        WNum = 0 # 1 byte number of words = word length (Wdt)
        ENum = 0 # 1 byte length indicator in word unit (1 word = 2 bytes)
        EPC = 0 # https://en.wikipedia.org/wiki/Electronic_Product_Code
        Mem = 0 # 1 byte 0x00 - password memory, 0x01 epc memory, 0x02 TID memory, 0x03 User memory
        WordPtr = 0 # 1 byte starting word address (0x00 first word, 0x01 second word ...)
        Wdt = 0 # data to be written into tag. Word length equal to Wnum, data arranged with most significant word first and most significant byte in the word first
        Pwd = 0 # 4 bytes access password. 0000 if not used
        MaskMem = 0 # 1 byte target memory for mask pattern - 0x01 EPC memory, 0x02 TID memory, 0x03 User memory
        MaskAdr = 0 # 2 bytes start bit address in target memory when applying mask pattern 0-16383
        MaskLen = 0 # 1 byte bit length of the mask pattern
        MaskData = 0 # mask pattern data. Length = MaskLen/8 or int(MaskLen/8)+1 with 0 padding in the LSB of last byte of MaskData
        
        return self.command(0x03, outData)
    
       
    def single_tag_inventory(self):
        l.debug('# single_tag_inventory')
        re = self.command(0x0f)
        response = {'addr':re[0], 'cmd':re[1], 'sts':re[2], 'ant':re[3], 'num':re[4], 'epc_len':re[5], 'epc_id':binascii.hexlify(re[6:-3])}
        return response
        
    def get_buffer_data(self):
        l.debug('# get_buffer_data')
        return self.command(0x72)

    
    def get_reader_information(self):
        l.debug('# get_reader_information')
        re = self.command(0x21)
        response = {'addr':re[0], 'cmd':re[1], 'sts':re[2], 'version':re[3:5], 'type':re[5], 'tr_type': re[6], 'dmaxfre':re[7], 'dminfre':re[8], 'power':re[9], 'scntm':re[10], 'ant':re[11], 'beepen':re[12], 'reserved':re[13], 'checkant':re[14]}
        return response
        
    def clear_buffer(self):
        l.debug('# clear_buffer')
        return self.command(0x73)

    def set_rf_power(self, power):
        """ min 0 max 1a """
        l.debug('# set_rf_power %s' % power)
        return self.command(0x2f, outData=power)
        
    def extension_read(self):
        l.debug('# extension_read')
        re = self.command(0x15)
        response = {'addr':re[0], 'cmd':re[1], 'data':re[2:]}
        return response

    def beep_setting(self, outData):
        """0 - off, 1 - on"""
        l.debug('# beep_setting %s' % outData)
        re = self.command(0x40, outData)
        response = {'addr':re[0], 'cmd':re[1], 'sts':re[3], 'data':re[3:]}
        return response        
        
    def buffer_inventory(self):
        l.debug('# buffer_inventory')
        re = self.command(0x18)
        response = {'addr':re[0], 'cmd':re[1], 'sts':re[3], 'data':binascii.hexlify(re[3:])}
        return response                
        
    def write_epc(self, wepc, pwd='00000000'):
        """epc - string to be converted together with enum and pwd into string of hex digits
        string should be even or space will be added
        """
        l.debug('# write_epc %s' % wepc)
        wepc = codecs.encode(bytes(wepc, 'utf-8'), 'hex').decode("utf-8")
        if len(wepc)%2 == 1:
            wepc = wepc + ' '
        l.debug('wepc %s, len(wepc)= %s' % (wepc, len(wepc)))
        #enum = len(wepc)//4 + int((len(wepc) / 2) % 2) # if odd add 1
        enum = (3+len(wepc))//4
        l.debug('enum %s', enum)
        if enum > 15:
            enum = 15
        if enum < 0:
            enum = 0
        enum = ('%02X' % enum)
        l.debug('enum (length in words) %s' % enum)
        epc = enum + pwd + wepc
        l.debug('epc %s' % epc)
        return self.command(0x04, epc)


if __name__ == "__main__":
    reader = RU5202()

    parser = ArgumentParser()
    parser.add_argument("-bs", "--beep_setting", choices = ['00', '01'], help="Beep setting 00,01.")
    parser.add_argument("-we", "--write_epc", help="Write EPC - max 20 characters.")
    parser.add_argument("-i", "--inventory", help="Print EPC inventory.", action="store_true")
    parser.add_argument("-srp", "--set_rf_power", help="Set RF power - 00-1e",)
    parser.add_argument("-cb", "--clear_buffer", action="store_true")
    parser.add_argument("-rd", "--read_data", action="store_true")
    parser.add_argument("-bi", "--buffer_inventory", action="store_true")
    parser.add_argument("-er", "--extension_read", action="store_true")
    parser.add_argument("-sti", "--single_tag_inventory", action="store_true")
    parser.add_argument("-gbd", "--get_buffer_data", action="store_true")
    parser.add_argument("-gri", "--get_reader_information", action="store_true")
    parser.add_argument("-con", "--continuous_reading", action="store_true")
    
    args = parser.parse_args()
    
    if args.beep_setting:
        reader.beep_setting(args.beep_setting)
        
    if args.write_epc:
        reader.write_epc(args.write_epc)
        
    if args.inventory:
        odp = reader.inventory(outData='0e00000000')
        print(odp)
        print(odp['epc_id'])
        print(codecs.decode(odp['epc_id'], 'hex'))
        
    if args.set_rf_power:
        reader.set_rf_power(args.set_rf_power)

    if args.clear_buffer:
        reader.clear_buffer()
        
    if args.read_data:
        print(reader.read_data())
    
    if args.buffer_inventory:
        print(reader.buffer_inventory())
    
    if args.extension_read:
        print(reader.extension_read())
  
    if args.single_tag_inventory:
        print(reader.single_tag_inventory()) #['epc_id'])
        
    if args.get_buffer_data:
        print(reader.get_buffer_data())
        
    if args.get_reader_information:
        print(reader.get_reader_information())

    if args.continuous_reading:
        while 1:
            odp = reader.inventory(outData='0e00000000')
            print(odp)
            print(odp['epc_id'])
            try:
                print(codecs.decode(odp['epc_id'], 'hex').decode('utf-8'))
            except:
                print('Non UTF-8 characters in string!')

