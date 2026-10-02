def lookahead(iterable):
  it = iter(iterable)
  try:
    last = next(it)
  except StopIteration:
    return
  
  for val in it:
    yield last, False
    last = val

  yield last, True
