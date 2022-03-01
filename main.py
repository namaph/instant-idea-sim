from mylib import const as C
from mylib.datastore import Store
from mylib.simulator import SimCon
from mylib import util as U
from mylib.visualizer import Grid

store = Store()
simcon = SimCon(**store.cval)
hist = simcon.run_sim(12*5, C.Economics)

U.plot_graph(hist[0])

U.plot_grid(hist[0], C.pos, C.NodeAttr.type)

for i in range(6):
    U.plot_grid(hist[10*i], C.pos, C.NodeAttr.value, f'valgrid_{i}.png')