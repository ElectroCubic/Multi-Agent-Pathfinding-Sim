# Interactive Multi-Agent Parallel Pathfinding Simulator (IMAPPS)
An interactive multi-agent pathfinding simulator in Python using Pygame, and multi-processing modules for parallel A* path computations and optimizations. This repository contains both the serial and parallel implementations of the simulator.

## Table of Contents:
1) [Key Features](#Key-Features)
2) [Pathfinding Algorithm](#Pathfinding-Algorithm)
3) System Requirements
4) Installation
5) Project Structure
6) How to Run
7) Simulator Controls

## Key Features:
- A*-based pathfinding for each agent
- Parallelized execution using Python’s multiprocessing
- Configurable grid size and number of agents
- Agents move orthogonally (4-ways) in a 2D grid space.
- Place agents, goals and obstacles with easy mouse controls.
- Agents can dynamically replan their paths if blocked by other agents.
- Measure time performance of A* path calculations.

## Pathfinding Algorithm
### A* Algorithm

Each agent computes the shortest path to its goal using the A* algorithm, defined by:
Heuristic: Manhattan distance
Cost Function: f(n) = g(n) + h(n)
Neighbors: 4-directional (up, down, left, right)
Obstacles: Cells marked as blocked are ignored during path expansion.

Parallelization Strategy

Each agent runs its pathfinding computation in a separate process.

The main process collects results and updates the display in sync.

Parallelism leverages the multiprocessing library for CPU-bound workloads.

## Simulator Controls:
- Press **T to toggle Wall Mode**. Then use **Left Click** to place/remove walls.
- Press **Right Mouse Button** to place Agents.
- Press **Middle Mouse Button** to place Goals.
- Press **Space bar** to run the simualation.
- Press **R to Reset** the agents and goals.

## Contributions Made By: 
- Anush Bundel - 2023BCS0005
- Ankush Sharma - 2023BCS0131
