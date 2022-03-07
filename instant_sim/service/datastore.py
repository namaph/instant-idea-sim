from dataclasses import dataclass
from typing import List

import requests

from . import types as T


@dataclass
class Store:
    base: str
    cont: T.store.CityioResp

    def __init__(
        self,
        url: str = "https://cityio.media.mit.edu/api/table/namaph/",
    ) -> None:
        self.base = url
        resp = requests.get(self.base)
        assert resp.status_code == 200, "ConnectionError"
        self.cont = T.store.CityioResp(**resp.json())

    def check_update(self) -> List[str]:
        meta = requests.get(f"{self.base}/meta")
        assert meta.status_code == 200, "ConnectionError"
        cont = meta.json()
        if self.cont.hash == cont["hash"]:
            return []

        ret = [k for k, v in cont.items() if self.cont.__dict__[k] != v]
        return ret

    def update(self, target: List[str]):
        meta = requests.get(f"{self.base}/meta")
        self.cont.meta = T.store.MetaCityioResp(**meta)
        for i in target:
            temp = requests.get(f"{self.base}/{i}")
            assert temp.status_code == 200, "ConnectionError"
            self.cont.__dict__[i] = temp.json()

    def run(self):
        self.update(self.check_update())
