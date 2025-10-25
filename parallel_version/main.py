import multiprocessing
from sim import run_simulation

if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)
    run_simulation()