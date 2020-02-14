import netaddr

class Device:

  def __init__(self, name, host = '', mac = '', port = 80, timeout = 10, ignore_errors = False):
  
    if not host or not mac or not port:
      raise AttributeError('not all important attributes supplied')

    self.name = name
    self.host = host
    self.port = port

    try:
      mac = netaddr.EUI(mac)
      mac.dialect = netaddr.mac_unix
      self.mac = str(mac)
    except netaddr.core.AddrFormatError:
      if ignore_errors:
        self.mac = '00:00:00:00:00:00'
      else:
        raise AttributeError('invalid mac address')

    self.timeout = timeout
