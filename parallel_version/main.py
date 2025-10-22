import multiprocessing
from sim import run_simulation

if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_simulation()
