import json
from typing import (
  Dict,
  Iterator,
  Optional,
)

#
# > TrieNode
#
class TrieNode(object):
  def __init__(self, prefix):
    self.children: Dict[str, "TrieNode"]   = dict()
    self.prefix     = '_'.join(prefix)
    self.source     = set()

  def reprJSON(self):
    return {
      'prefix' : self.prefix,
      'source' : list(self.source),
      'children': self.children
    }
    
  def __getitem__(self, key):
    return self.children[key]

class TrieNodeEncoder(json.JSONEncoder):
  def default(self, obj):
    if hasattr(obj, 'reprJSON'):
      return obj.reprJSON()
    else:
      return super().default(obj)

#
# > Trie
#
class Trie:
  def __init__(self):
    self.root = TrieNode('')

  def insert(self, word):
    trie = self.root
   
    source   = '.'.join(word)
    word    = '_'.join(word).upper().split('_')

    for i in range(len(word)):
      letter    = word[i]
      prefix    = word[0:(i+1)]
      
      if letter not in trie.children:
        trie.children.setdefault(letter, TrieNode(prefix))
      trie = trie.children[letter]
    
    trie.source.add(source)

  def visit(self, root = None) -> Iterator[TrieNode]:
    if root is None:
      root = self.root
    else:
      yield root

    for node in root.children.values():
      for subnode in self.visit(node):
        yield subnode

  def search(self, prefix) -> Optional[TrieNode]:
    trie    = self.root
    word    = prefix.split('_')
    result  = None

    try:
      for letter in word:
        trie = trie.children[letter]
    except KeyError:
      result = None
    else:
      result = trie

    return result

  def __getitem__(self, key):
    return self.root[key]


