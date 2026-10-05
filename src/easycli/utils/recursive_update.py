def recursive_update(
    dest: dict,
    src: dict,
    *,
    discard: bool,
    fallback: bool,
    path=[]):
  """
  In-place recursive update:

  'dest' will be modified, in general
  None values in 'src' will remove corresponding keys in 'a' if discard == True
  None values in 'src' will be ignored if fallback = True

  """
  if discard and fallback:
    raise ValueError("setting both 'discard_none' and 'fallback_none' to True is unsupported")
  elif discard == True:
    action = _discard    
  elif fallback == True:    
    action = _fallback
  else:
    # import pdb; pdb.set_trace()
    action = _assign

  for key in src:
    if key in dest:
      if isinstance(dest[key], dict) and isinstance(src[key], dict):
        recursive_update(
          dest[key], src[key],
          discard = discard,
          fallback = fallback,
          path = path + [str(key)]
        )
      else:
        apply(action, dest, src, key)

    else:
      apply(action, dest, src, key)
       
  return dest

def apply(action, dest, src, key):
  if src[key] is None:
    action(dest,key)
  else:
    dest[key] = src[key]

def _discard(d: dict, key):
  d.pop(key, None)

def _fallback(d: dict, key):
  pass

def _assign(d: dict, key):
  d[key] = None
