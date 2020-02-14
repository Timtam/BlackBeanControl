import argparse
import sys

from .utils import pprint

class ArgumentParser:
  def __init__(self):
  
    self._parser = argparse.ArgumentParser()
    
    subparsers = self._parser.add_subparsers(
      title = 'sub-commands',
      description = 'available commands',
      dest = 'subparser_name',
      help = 'action to be performed by the script'
    )
    
    command_parser = subparsers.add_parser(
      'command',
      help='learn or send an IR command'
    )
    
    command_parser.add_argument(
      'command',
      type=str,
      help='name of the command which should be learned/sent'
    )
    
    command_parser.add_argument(
      '-d',
      '--device',
      type=str,
      default='General',
      help='name of the device to use'
    )
    
    command_parser.add_argument(
      '-i',
      '--ipaddress',
      type=str,
      default='',
      help='ip address of the device which should be used'
    )
    
    command_parser.add_argument(
      '-p',
      '--port',
      type=int,
      default=-1,
      help='port to use when connecting to the device'
    )
    
    command_parser.add_argument(
      '-m',
      '--mac',
      type=str,
      default='',
      help='mac address of the device'
    )
    
    command_parser.add_argument(
      '-t',
      '--timeout',
      type=int,
      default=-1,
      help='timeout for device actions'
    )

    discovery_parser = subparsers.add_parser(
      'discover',
      help='discover all supported devices in your local network'
    )

    discovery_parser.add_argument(
      'timeout',
      type=int,
      help='timeout when waiting for available devices to show up'
    )

  def run(self):
  
    result = self._parser.parse_args()
    
    res = {
      'mode': '',
      'command': '',
      'device': '',
      'ipaddress': '',
      'mac': '',
      'port': -1,
      'timeout': -1,
    }

    if result.subparser_name == 'command':
      res['mode'] = 'command'
      
      res['command'] = result.command.strip()

      if result.device.strip():
        res['device'] = result.device.strip()
      
        if result.ipaddress.strip() or result.mac.strip() or result.port >= 0 or result.timeout >= 0:
          pprint('You can only provide either a device name from the ' +
                 'configuration file or host, mac, port and timeout of a device'
          )
        
          sys.exit(2)
        
      else:
      
        if not result.ipaddress.strip() or not result.mac.strip() or not result.port >= 0 or not result.timeout >= 0:
          pprint('you need to provide either a device name from the ' + 
                 'configuration file or host, mac address, port and timeout of a ' + 
                 'device to use'
          )
          
          sys.exit(2)
        
        res['ipaddress'] = result.ipaddress.strip()
        res['mac'] = result.mac.strip()
        res['port'] = result.port
        res['timeout'] = result.timeout
      
    elif result.subparser_name == 'discover':
      
      res['mode'] = 'discover'
      res['timeout'] = result.timeout

    else:
      result = self._parser.parse_args(('--help', ))
      sys.exit(2)

    return res