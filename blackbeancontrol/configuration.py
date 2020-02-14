import configparser
import netaddr

from .device import Device
from .utils import get_configuration_file

class Configuration:

  def __init__(self):
  
    self._parser = configparser.ConfigParser()
    self._parser.optionxform = str
    
    self._parser.read(get_configuration_file())

  def get_device_names(self):
    return [sec for sec in self._parser.sections() if sec not in ['Commands']]
  
  def get_devices(self):
  
    devs = []
    
    for dev in self.get_device_names():
    
      try:
        devs.append(self.get_device(dev))
      except (AttributeError, ValueError):
        continue
      
    return devs
  
  def get_commands(self):
  
    try:
      return dict(self._parser['Commands'])
    except KeyError:
      return {}

  def get_device(self, name):
    
    dev = self._parser[name]

    return Device(
      name = name,
      host = dev.get('IPAddress', ''),
      mac = dev.get('MACAddress', ''),
      port = dev.getint('Port', 80),
      timeout = dev.getint('Timeout', 10),
      type = int(dev.get('Type', '0x0'), 16)
    )
  
  def device_exists(self, name):
  
    try:
      dev = self.get_device(name)
      return True
    except (KeyError, AttributeError, ValueError):
      return False

  def add_device(self, device):
  
    try:
      dev = self.get_device(device.name)
      
      return False
    except (KeyError, AttributeError):
    
      self._parser.remove_section(device.name)
      
      self._parser.add_section(device.name)
      
      self._parser.set(device.name, 'IPAddress', device.host)
      self._parser.set(device.name, 'MACAddress', device.mac)
      self._parser.set(device.name, 'Port', str(device.port))
      self._parser.set(device.name, 'Timeout', str(device.timeout))
      self._parser.set(device.name, 'Type', hex(device.type))

      self.save()

      return True

  def command_exists(self, name):
    return name in self.get_commands()

  def add_command(self, name, code):
  
    if self.command_exists(name):
      return False
    
    try:
      self._parser.add_section('Commands')
    except configparser.DuplicateSectionError:
      pass
    
    self._parser['Commands'].set(name, code)

    self.save()
    
  def save(self):
    with open(get_configuration_file(), 'w') as f:
      self._parser.write(f)

  def remove_command(self, name):
  
    if self.command_exists(name):
      self._parser.remove_option('Commands', name)
      self.save()
      return True
    
    return False
  
  def remove_device(self, name):
  
    if self.device_exists(name):
      self._parser.remove_section(name)
      self.save()
      return True
    return False
  
  def find_device(self, mac, host, port = 80):

    for sec in self._parser.sections():

      if sec == 'Commands':
        continue

      try:
        secmac = netaddr.EUI(self._parser[sec]['MACAddress'])
      except netaddr.core.AddrFormatError:
        secmac = netaddr.EUI('00:00:00:00:00:00')

      secmac.dialect = netaddr.mac_unix

      if self._parser[sec].get('IPAddress', '') == host and \
         str(secmac) == mac and \
         self._parser[sec].getint('Port', 80) == port:

        return self.get_device(sec)
    return False