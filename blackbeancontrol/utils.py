import os.path
from textwrap import wrap

def pprint(text):

  if isinstance(text, list):
    for t in text:
      print(t)
  else:
    pprint(wrap(text))

def get_application_directory():
  return os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))

def get_configuration_file():
  return os.path.join(get_application_directory(), 'BlackBeanControl.ini')
