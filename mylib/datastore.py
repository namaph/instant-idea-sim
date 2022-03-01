from dataclasses import dataclass
from typing import Any, Dict, List
import requests

@dataclass
class Store:
  base: str
  hash: str
  chash: Dict[str, str]
  cval: Dict[str, Any]

  def __init__(self, url:str='https://cityio.media.mit.edu/api/table/namaph', auto_update=True):
    self.base = url
    self.hash = ""
    self.cval = {}

    contr = requests.get(f"{self.base}/meta")
    cont = contr.json()['hashes']
    self.chash = {k: '' for k in cont.keys()}

    if auto_update:
      self.run()
  
  def check_update(self) -> List[str]:
    hr = requests.get(f"{self.base}/meta/hash")
    assert hr.status_code == 200, 'ConnectionError'
    h = hr.json()
    if self.hash == h:
      return []
    
    contr = requests.get(f"{self.base}/meta")
    assert contr.status_code == 200, 'ConnectionError'
    cont = contr.json()['hashes']
    ret = [k for k, v in cont.items() if self.chash[k] != v]

    self.hash = h
    self.chash = cont
    return ret
  
  def update(self, target: List[str]):
    for i in target:
      temp = requests.get(f'{self.base}/{i}')
      assert temp.status_code == 200, 'ConnectionError'
      self.cval[i] = temp.json()
  
  def run(self):
      self.update(self.check_update())