# BlackBeanControl - Broadlink RM 3 Mini (aka Black Bean) control script

This is the successor of Davorf's original BlackBeanControl script, which can be found under [this link](https://github.com/davorf/BlackBeanControl).

This is a simple Python script, which can be used for both, learning and sending IR commands utilizing several Broadlink devices within the local network.

## New features

This version features some improvements from the original BlackBeanControl script. Those are:
* discovery mode to automatically discover new devices within the local network and add them to the BlackBeanControl.ini file automatically
* support for command chains to send multiple commands in a row, including idle times in-between
* command repeatition to send entire command chains multiple times in a row
* Python 3 compatibility
* support for the newest package versions, especially python-broadlink

The new script however features a slightly different command-line interface, which breaks backwards compatibility. See below to get more information.

## Installation

After cloning/downloading the script, you should install all dependencies. Just run pip install -r requirements.txt.

## Configuration

All required configuration is held within BlackBeanControl.ini file. It consists of the following parameters: 

[General]
- IPAddress - an IP address of RM 3 Mini (RM 3 Mini must have local IP address)
- Port - a port used for UDP communication (in most cases, 80)
- MACAddress - a MAC address of RM 3 Mini (should be in format: MM:MM:MM:SS:SS:SS)
- Timeout - a time in seconds script should wait for an answer after starting a learn process (should be less then 60 seconds)
- Type - the device type specified as hex code (this is a value introduced in python-broadlink, the easiest way is to let the script determine it by using the new discovery mode, or search for the list of supported devices within the python-broadlink package under [this link](https://github.com/mjg59/python-broadlink))

[Commands]
- This section should be populated by using the script, not manually

Configuration file could optionally contain multiple device sections (with a custom names, must not contain any blanks). The device section must have all the parameters General section has. It allows user to control multiple RM 3 Minis without passing all the parameters separately. Instead, only -d (--device) parameter should be passed, with a section name containing connection parameters for the specific device. It is recommended to use the discovery mode to properly add such device sections into the configuration file.

### Example of a custom device section:
```
[RM3LivingRoom]
IPAddress = 192.168.0.1
Port = 80
MACAddress = AA:BB:CC:DD:EE:FF
Timeout = 30
Type = 0x27a9 # RM Pro 3+
```

## Syntax and usage

### sub-command overview
```
usage: BlackBeanControl.py [-h] {command,discover} ...

optional arguments:
  -h, --help          show this help message and exit

sub-commands:
  available commands

  {command,discover}  action to be performed by the script
    command           learn or send an IR command
    discover          discover all supported devices in your local network
```

Parameters explanation: 
- command - learn or send a specific command
- discover - discover all supported devices within the local network and add them to the configuration file

### command mode
```
usage: BlackBeanControl.py command [-h] [-d DEVICE] [-i IPADDRESS] [-p PORT]
                                   [-m MAC] [-y TYPE] [-t TIMEOUT] [-e REPEAT]
                                   command [command ...]

positional arguments:
  command               commands which should be learned/sent

optional arguments:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
                        name of the device to use
  -i IPADDRESS, --ipaddress IPADDRESS
                        ip address of the device which should be used
  -p PORT, --port PORT  port to use when connecting to the device
  -m MAC, --mac MAC     mac address of the device
  -y TYPE, --type TYPE  device type (see either discovery results or python-
                        broadlink package)
  -t TIMEOUT, --timeout TIMEOUT
                        timeout for device actions
  -e REPEAT, --repeat REPEAT
                        repeat sending the given commands a given number of
                        times
```

Parameters explanation: 
- command - at least one command must be specified. If a command with that name is known, this command will be sent to the RM device. If the command is unknown, the device will enter learning mode to read it. Multiple commands can be specified after another to be sent in a command chain. Sleep times can be added in-between as numbers, representing the milliseconds to wait between the consecutive commands.
- device - optional parameter. If the script is called with Device name parameter, all parameters found in the General section of the configuration file will be ignored, and a script will use parameters found in a device section of the configuration file. Device name parameter can not be used in conjunction with IP Address, MAC Address and Type command line parameters. If no device is specified, the General device will be used instead.
- IP Address - optional parameter. If the script is called with IP Address parameter, IP address found in the configuration file will be ignored, and a script will use IP address from this parameter.
- Port - optional parameter. If the script is called with Port parameter, port found in the configuration file will be ignored, and a script will use port from this parameter.
- MAC Address - optional parameter. If the script is called with MAC address parameter, MAC address found in the configuration file will be ignored, and a script will use MAC address from this parameter.
- Timeout - optional parameter. If the script is called with Timeout parameter, Timeout found in the configuration file will be ignored, and a script will use Timeout from this parameter.
- Type - optional parameter. If the script is called with Type parameter, type found in the configuration file will be ignored, and a script will use type from this parameter.
- repeat - optional parameter. This parameter allows to send the entire command chain a given amount of times. Default is 1.
- Re-Key - optional parameter. This will re-key existing IR data to a new format that does not use the device key for storage. If the data was stored previously with a specific Broadlink device that device name will need to be provided for re-keying by providing a device name using -d parameter.

IP Address, Port, MAC Address and Timeout command line parameters can not be used separately.

### discovery mode
```
usage: BlackBeanControl.py discover [-h] timeout

positional arguments:
  timeout     timeout when waiting for available devices to show up

optional arguments:
  -h, --help  show this help message and exit
```

Parameters explanation: 
- timeout - time to wait for the devices to respond, default is 10 seconds

### License

Software licensed under GPL version 3 available on http://www.gnu.org/licenses/gpl.txt.
