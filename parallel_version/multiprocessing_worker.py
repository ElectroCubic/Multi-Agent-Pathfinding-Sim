# multiprocessing_worker.py
import numpy as np
from multiprocessing import shared_memory
from astar import astar

_WALLS = None
_SHM = None

def init_worker(shm_name, shape):
    """
    Called once per worker on start. Attaches to shared memory buffer
    created by the main process and builds a numpy view on it.
    shm_name: name of SharedMemory block
    shape: (grid_w, grid_h)
    """
    global _WALLS, _SHM
    _SHM = shared_memory.SharedMemory(name=shm_name)
    # walls stored as uint8 (0/1) in shared memory
    grid_w, grid_h = shape
    arr = np.ndarray((grid_w, grid_h), dtype=np.uint8, buffer=_SHM.buf)
    # Use a boolean view for convenience
    _WALLS = arr.view(dtype=np.uint8)

def compute_best_path(args):
    """
    args:
      - agent_batch: list of (ax, ay) tuples
      - goals: list of (gx, gy)
      - grid_w, grid_h: ints
      - reached_goals: set of (x,y) that should be treated as walls for planning
    returns:
      list of (agent_pos, path_tuples or None)
    """
    agent_batch, goals, grid_w, grid_h, reached_goals = args

    results = []
    # make a local boolean copy once per batch and apply reached_goals
    base_walls = _WALLS.astype(bool, copy=True)

    # mark reached goals as walls in the local copy
    if reached_goals:
        for (rx, ry) in reached_goals:
            if 0 <= rx < grid_w and 0 <= ry < grid_h:
                base_walls[rx][ry] = True

    # For each agent in batch, find best goal
    for agent_pos in agent_batch:
        best_path = None
        best_len = float('inf')
        ax, ay = agent_pos

        if base_walls[ax][ay]:
            results.append((agent_pos, None))
            continue

        sorted_goals = sorted(goals, key=lambda g: abs(g[0]-ax) + abs(g[1]-ay))
        for gx, gy in sorted_goals:
            if (gx, gy) in reached_goals:
                continue

            path = astar(base_walls, (ax, ay), (gx, gy), grid_w, grid_h)
            if path:
                if len(path) < best_len:
                    best_len = len(path)
                    best_path = path

                if best_len == abs(gx-ax) + abs(gy-ay):
                    break

        results.append((agent_pos, best_path if best_path else None))

    return results
