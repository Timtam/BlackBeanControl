#!/usr/bin/python

import broadlink, configparser
import sys
import time, binascii
import Settings
import netaddr
import string
from os import path
from Crypto.Cipher import AES

from blackbeancontrol import (
  ArgumentParser,
  pprint)

SettingsFile = configparser.ConfigParser()
SettingsFile.optionxform = str
SettingsFile.read(Settings.BlackBeanControlSettings)

SentCommand = ''
ReKeyCommand = False
RealCommand = ''
DeviceName=''
DeviceIPAddress = ''
DevicePort = ''
DeviceMACAddres = ''
DeviceTimeout = ''
AlternativeIPAddress = ''
AlternativePort = ''
AlternativeMACAddress = ''
AlternativeTimeout = ''

def discover_action(timeout):

  pprint('waiting {seconds} seconds for devices to be discovered...'.format(seconds = timeout))
  devices = broadlink.discover(timeout)

  pprint('found {amount} devices in your local network'.format(amount = len(devices)))
  
  if len(devices) == 0:
    return
  
  for i, dev in enumerate(devices):
  
    pprint('device {i}:'.format(i = i + 1))

    # that seems incredibly hackish
    # I just didn't get the hang of how to transform a byte array into a string representation
    # guess I will change that later on
    devmac = netaddr.EUI(':'.join(list(reversed([hex(b)[2:] for b in dev.mac]))))
    devmac.dialect = netaddr.mac_unix

    pprint('\tip address: {ipaddress}'.format(ipaddress = dev.host[0]))
    pprint('\tmac address: {macaddress}'.format(macaddress = str(devmac)))
    pprint('\tport: {port}'.format(port = dev.host[1]))
    pprint('\ttimeout: {timeout}'.format(timeout = dev.timeout))

    known = False

    # check if this device is already known to us
    for sec in SettingsFile.sections():

      if sec == 'Commands':
        continue

      try:
        secmac = netaddr.EUI(SettingsFile[sec]['MACAddress'])
      except netaddr.core.AddrFormatError:
        secmac = netaddr.EUI('00:00:00:00:00:00')

      secmac.dialect = netaddr.mac_unix

      if SettingsFile[sec]['IPAddress'] == dev.host[0] and \
         secmac == devmac and \
         SettingsFile[sec].getint('Port') == dev.host[1]:

        pprint("\talready known as '{name}'".format(name = sec))
        known = True
        break
    
    if known:
      continue

    pprint('\tnew device!')

    pprint('if you want to add this device to the configuration file, enter a ' +
           'new name for it now'
    )
    
    name = input('name of the device:')
    
    if not name.strip():
      continue
    
    if name.strip() in SettingsFile.sections():
      pprint('a device or configuration section with that name already exists')
      continue
    
    SettingsFile.add_section(name)
    SettingsFile.set(name, 'MACAddress', str(devmac))
    SettingsFile.set(name, 'IPAddress', dev.host[0])
    SettingsFile.set(name, 'Port', str(dev.host[1]))
    SettingsFile.set(name, 'Timeout', str(dev.timeout))

    pprint("added as new device '{name}'".format(name = name))

  with open(path.join(Settings.ApplicationDir, 'BlackBeanControl.ini'), 'w') as f:
    SettingsFile.write(f)

# parsing command line arguments
parser = ArgumentParser()
result = parser.run()

RealCommand = result['mode']

if RealCommand == 'discover':
  discover_action(result['timeout'])
  sys.exit()

SentCommand = result['command']

DeviceName = result['device']
#    elif Option in ('-r', '--rekey'):
#        ReKeyCommand = True
#        SentCommand = Argument
AlternativeIPAddress = result['ipaddress']
AlternativePort = result['port']
AlternativeMACAddress = result['mac']
AlternativeTimeout = result['timeout']

if DeviceName.strip() != '':
    if SettingsFile.has_section(DeviceName.strip()):
        if SettingsFile.has_option(DeviceName.strip(), 'IPAddress'):
            DeviceIPAddress = SettingsFile.get(DeviceName.strip(), 'IPAddress')
        else:
            DeviceIPAddress = ''

        if SettingsFile.has_option(DeviceName.strip(), 'Port'):
            DevicePort = SettingsFile.get(DeviceName.strip(), 'Port')
        else:
            DevicePort = ''

        if SettingsFile.has_option(DeviceName.strip(), 'MACAddress'):
            DeviceMACAddress = SettingsFile.get(DeviceName.strip(), 'MACAddress')
        else:
            DeviceMACAddress = ''

        if SettingsFile.has_option(DeviceName.strip(), 'Timeout'):
            DeviceTimeout = SettingsFile.get(DeviceName.strip(), 'Timeout')
        else:
            DeviceTimeout = ''        
    else:
        print('Device does not exist in BlackBeanControl.ini')
        sys.exit(2)

if (DeviceName.strip() != '') and (DeviceIPAddress.strip() == ''):
    print('IP address must exist in BlackBeanControl.ini for the selected device')
    sys.exit(2)

if (DeviceName.strip() != '') and (DevicePort.strip() == ''):
    print('Port must exist in BlackBeanControl.ini for the selected device')
    sys.exit(2)

if (DeviceName.strip() != '') and (DeviceMACAddress.strip() == ''):
    print('MAC address must exist in BlackBeanControl.ini for the selected device')
    sys.exit(2)

if (DeviceName.strip() != '') and (DeviceTimeout.strip() == ''):
    print('Timeout must exist in BlackBeanControl.ini for the selected device')
    sys.exit(2)    

if DeviceName.strip() != '':
    RealIPAddress = DeviceIPAddress.strip()
elif AlternativeIPAddress.strip() != '':
    RealIPAddress = AlternativeIPAddress.strip()
else:
    RealIPAddress = Settings.IPAddress

if RealIPAddress.strip() == '':
    print('IP address must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)

if DeviceName.strip() != '':
    RealPort = DevicePort.strip()
elif AlternativePort.strip() != '':
    RealPort = AlternativePort.strip()
else:
    RealPort = Settings.Port

if RealPort.strip() == '':
    print('Port must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)
else:
    RealPort = int(RealPort.strip())

if DeviceName.strip() != '':
    RealMACAddress = DeviceMACAddress.strip()
elif AlternativeMACAddress.strip() != '':
    RealMACAddress = AlternativeMACAddress.strip()
else:
    RealMACAddress = Settings.MACAddress

if RealMACAddress.strip() == '':
    print('MAC address must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)
else:
    RealMACAddress = netaddr.EUI(RealMACAddress)

if DeviceName.strip() != '':
    RealTimeout = DeviceTimeout.strip()
elif AlternativeTimeout.strip() != '':
    RealTimeout = AlternativeTimeout.strip()
else:
    RealTimeout = Settings.Timeout

if RealTimeout.strip() == '':
    print('Timeout must exist in BlackBeanControl.ini or it should be entered as a command line parameter')
    sys.exit(2)
else:
    RealTimeout = int(RealTimeout.strip())    

RM3Device = broadlink.rm((RealIPAddress, RealPort), RealMACAddress)
RM3Device.auth()

if ReKeyCommand:
    if SettingsFile.has_option('Commands', SentCommand):
        CommandFromSettings = SettingsFile.get('Commands', SentCommand)

        if CommandFromSettings[0:4] != '2600':
            RM3Key = RM3Device.key
            RM3IV = RM3Device.iv

            DecodedCommand = binascii.unhexlify(CommandFromSettings)
            AESEncryption = AES.new(str(RM3Key), AES.MODE_CBC, str(RM3IV))
            EncodedCommand = AESEncryption.encrypt(str(DecodedCommand))
            FinalCommand = EncodedCommand[0x04:]
            EncodedCommand = FinalCommand.encode('hex')

            BlackBeanControlIniFile = open(path.join(Settings.ApplicationDir, 'BlackBeanControl.ini'), 'w')
            SettingsFile.set('Commands', SentCommand, EncodedCommand)
            SettingsFile.write(BlackBeanControlIniFile)
            BlackBeanControlIniFile.close()
            sys.exit()
        else:
            print("Command appears to already be re-keyed.")
            sys.exit(2)
    else:
        print("Command not found in ini file for re-keying.")
        sys.exit(2)

if RealCommand == 'n':
    if (len(SentCommand) != 8) or (not all(c in string.hexdigits for c in SentCommand)):
        print('Command must be 4-byte hex number.')
        sys.exit(2)

    BinStr = "".join('%s' % bin(int(SentCommand[i: i + 2], 16))[2:].zfill(8)[::-1] for i in xrange(0, 7, 2))
    
    # start sequence + NEC start + bits + end pulse with long pause + end sequence
    EncodedCommand = '26002e01' + '00012b96' + "".join(('1440' if c == '1' else '1414') for c in BinStr) + '1400072a' + '000d05'
    
    RM3Device.send_data(EncodedCommand.decode('hex'))

    sys.exit()

if RealCommand == 's':
    if (len(SentCommand) != 12) or (not all(c in string.hexdigits for c in SentCommand)):
        print('Command must be 6-byte hex number.')
        sys.exit(2)

    BinStr = "".join('%s' % bin(int(SentCommand[i: i + 2], 16))[2:].zfill(8)[::-1] for i in xrange(0, 11, 2))
    
    # start sequence + Samsung start + data + end pulse + (here the copy)Samsung start + data + end pulse with long pause + end sequence
    EncodedBinStr = "".join(('1434' if (c == '1') else '1414') for c in BinStr)
    EncodedCommand = '2600ca00' + '9494' + EncodedBinStr + '1494' + '9494' + EncodedBinStr + '1400072a' + '000d05'
 
    RM3Device.send_data(EncodedCommand.decode('hex'))
    sys.exit()


if SettingsFile.has_option('Commands', SentCommand):
    CommandFromSettings = SettingsFile.get('Commands', SentCommand)
else:
    CommandFromSettings = ''

if CommandFromSettings.strip() != '':
    DecodedCommand = CommandFromSettings.decode('hex')
    RM3Device.send_data(DecodedCommand)
else:
    RM3Device.enter_learning()
    time.sleep(RealTimeout)
    LearnedCommand = RM3Device.check_data()

    if LearnedCommand is None:
        print('Command not received')
        sys.exit()

    EncodedCommand = LearnedCommand.encode('hex')

    BlackBeanControlIniFile = open(path.join(Settings.ApplicationDir, 'BlackBeanControl.ini'), 'w')    
    SettingsFile.set('Commands', SentCommand, EncodedCommand)
    SettingsFile.write(BlackBeanControlIniFile)
    BlackBeanControlIniFile.close()
    
