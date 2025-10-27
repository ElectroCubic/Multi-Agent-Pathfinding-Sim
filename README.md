# Interactive Multi-Agent Parallel Pathfinding Simulator (IMAPPS)
An interactive multi-agent pathfinding simulator in Python using Pygame, and multi-processing modules for parallel A* path computations and optimizations. This repository contains both the serial and parallel implementations of the simulator.

## Table of Contents:
1) [Key Features](#Key-Features)
2) [Pathfinding Algorithm](#Pathfinding-Algorithm)
3) [System Requirements](#System-Requirements)
4) [Installation](#Installation)
5) [Project Structure](#Project-Structure)
6) [How to Run](#How-to-Run)
7) [Simulator Controls](#Simulator-Controls)
8) [Contributors](#Contributors)

## Key Features:
- A*-based pathfinding for each agent
- Parallelized execution using Python’s multiprocessing
- Configurable grid size and number of agents
- Agents move orthogonally (4-ways) in a 2D grid space.
- Place agents, goals and obstacles with easy mouse controls.
- Agents can dynamically replan their paths if blocked by other agents.
- Measure time performance of A* path calculations.

## Pathfinding Algorithm:
### A* Algorithm

Each agent computes the shortest path to its goal using the A* algorithm, defined by: <br>
- Heuristic used: Manhattan distance <br>
- Cost Function: f(n) = g(n) + h(n) <br>
- Neighbors: 4-directional (up, down, left, right) <br>
- Obstacles: Cells marked as blocked are ignored during path expansion. <br>

## System Requirements:
- Python version: 3.13 or newer
- OS: Windows 10/11, macOS, or Linux
- RAM: 4GB or more
- CPU:  
  - Minimum: Dual-core processor (e.g., Intel Core i3 or AMD Ryzen 3)  
  - Recommended: Quad-core or higher (e.g., Intel Core i5/i7, AMD Ryzen 5/7)

## Installation:
```
python
# Clone the repository
git clone https://github.com/ElectroCubic/Multi-Agent-Pathfinding-Sim.git
cd Multi-Agent-Pathfinding-Sim

# Install dependencies
pip install -r requirements.txt
```
## Simulator Controls:
- Press **T to toggle Wall Mode**. Then use **Left Click** to place/remove walls.
- Press **Right Mouse Button** to place Agents.
- Press **Middle Mouse Button** to place Goals.
- Press **Space bar** to run the simualation.
- Press **R to Reset** the agents and goals.

## Contributors: 
- Anush Bundel - 2023BCS0005
- Ankush Sharma - 2023BCS0131
