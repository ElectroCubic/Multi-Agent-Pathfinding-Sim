# main.py
import multiprocessing
from sim import run_simulation

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # spawn is fine on Windows; explicit set helps consistency
    multiprocessing.set_start_method("spawn", force=True)
    run_simulation()
