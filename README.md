# CPU-Scheduler-Solver

**CPU Scheduler Solver** is a Python-based graphical simulator developed under the **Operating Systems** course by **Sumit Mali (23BIT193)** and **Chirag Maloo (23BIT192)**.  
The project provides a visual and interactive way to understand how different CPU scheduling algorithms work by displaying process execution order, timing, and performance metrics.

## Overview
This simulator allows users to input process details such as **Arrival Time (AT)**, **Burst Time (BT)**, and **Priority**, and then execute various scheduling algorithms.  
It calculates and displays important metrics such as **Completion Time (CT)**, **Turnaround Time (TAT)**, and **Waiting Time (WT)**, along with average performance values.  
A **Gantt chart** is also generated to help visualize CPU utilization and process scheduling over time.

## Features
- Interactive GUI built with **QtPy**
- Simulation of multiple CPU scheduling algorithms:
  - **First Come First Serve (FCFS)**
  - **Shortest Job First (SJF) – Non-Preemptive**
  - **Shortest Remaining Time First (SRTF)**
  - **Priority Scheduling – Non-Preemptive**
  - **Round Robin** (with fixed quantum = 2)
- Displays a detailed table showing all process statistics
- Automatically computes **average turnaround time** and **average waiting time**
- Generates a **Gantt chart** visualization using **Matplotlib**
- User-friendly interface suitable for educational demonstrations

## Technologies Used
- **Python 3**
- **QtPy (compatible with PyQt / PySide)**
- **Matplotlib**

## Output
- Tabular display of scheduling results with process metrics
- Gantt chart showing the sequence and timing of process execution
- Average TAT and WT displayed for overall performance comparison

## Authors
- **Sumit Mali** — 23BIT193  
- **Chirag Maloo** — 23BIT192
