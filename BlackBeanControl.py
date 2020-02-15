#!/usr/bin/python

import broadlink
import sys
import time, binascii
import netaddr
import string
from os import path
from Crypto.Cipher import AES

from blackbeancontrol import (
  ArgumentParser,
  Configuration,
  Device,
  pprint)

Settings = Configuration()
ReKeyCommand = False

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
    pprint('\tdevice type: {type}'.format(type = hex(dev.devtype)))
    pprint('\ttimeout: {timeout}'.format(timeout = dev.timeout))

    known = Settings.find_device(host = dev.host[0], port = dev.host[1], mac = str(devmac))

    if known:
      pprint("\talready known as '{name}'".format(name = known.name))
      continue

    pprint('\tnew device!')

    pprint('if you want to add this device to the configuration file, enter a ' +
           'new name for it now'
    )
    
    name = input('name of the device:')
    
    if not name.strip():
      continue
    
    if Settings.device_exists(name):
      pprint('a device or configuration section with that name already exists')
      continue
    
    Settings.add_device(Device(
      name = name,
      port = dev.host[1],
      host = dev.host[0],
      timeout = dev.timeout,
      mac = str(devmac),
      type = dev.devtype
    ))

    pprint("added as new device '{name}'".format(name = name))

# parsing command line arguments
parser = ArgumentParser()
result = parser.run()

if result['mode'] == 'discover':
  discover_action(result['timeout'])
  sys.exit()

ReKeyCommand = False
#    elif Option in ('-r', '--rekey'):
#        ReKeyCommand = True
#        SentCommand = Argument

if result['device'] and not Settings.device_exists(result['device']):
  print("Device '{name}' does not exist in BlackBeanControl.ini or contains invalid fields".format(name = result['device']))
  sys.exit(2)

device = None

if result['device']:
  device = Settings.get_device(result['device'])
else:
  try:
    device = Device(
      name = 'temporary',
      port = result['port'],
      timeout = result['timeout'],
      mac = result['mac'],
      host = result['ipaddress'],
      type = result['type']
    )
  except AttributeError as exc:
    pprint(exc.message)
    sys.exit(2)

RM3Device = broadlink.rm((device.host, device.port), device.mac, device.type)
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

"""
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
"""

# validate if all commands are unknown
# following situations are possible:
# 1. all string commands are known: send command chain as requested
# 2. at least one string command is unknown, and more than one command are given: abort with an error message
# 3. at least one string command is unknown, and only one string command is available: learn that command

cmd_count = 0
cmd_unknown = []

for i, cmd in enumerate(result['commands']):

  if isinstance(cmd, str):

    cmd_count += 1

    if not Settings.command_exists(cmd):
      cmd_unknown.append(cmd)

# everything is fine, run the command chain
if len(cmd_unknown) == 0 and cmd_count > 0:

  for i, cmd in enumerate(result['commands']):

    pprint('command {i}'.format(i = i + 1))
    if isinstance(cmd, str):

      pprint("\tsending '{name}'...".format(name = cmd))

      decoded_command = bytes.fromhex(Settings.get_command(cmd))
      RM3Device.send_data(decoded_command)
    elif isinstance(cmd, int):

      pprint('\tsleeping {time} milliseconds...'.format(time = cmd))

      time.sleep(cmd / 1000)

  pprint('finished sending commands. exiting.')

# more than one command is unknown and multiple commands are specified
elif len(cmd_unknown) > 0 and cmd_count > 1:

  pprint('the following commands are unknown and cannot be sent: {commands}'.format(commands = ', '.join(cmd_unknown)))
  sys.exit(2)

elif len(cmd_unknown) == 1 and cmd_count == 1:

  pprint("learning '{cmd}' during the next {time} seconds...".format(cmd = cmd_unknown[0], time = device.timeout))

  RM3Device.enter_learning()
  time.sleep(device.timeout)
  learned_command = RM3Device.check_data()

  if learned_command is None:
    print('Command not received')
    sys.exit()

  encoded_command = learned_command.hex()

  Settings.add_command(cmd_unknown[0], encoded_command)

  pprint('command learned')
