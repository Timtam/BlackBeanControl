from textwrap import wrap

def pprint(text):

  if isinstance(text, list):
    for t in text:
      print(t)
  else:
    pprint(wrap(text))