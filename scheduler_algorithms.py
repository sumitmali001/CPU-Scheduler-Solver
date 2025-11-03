# scheduler_algorithms.py
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

@dataclass
class Process:
    pid: str
    at: int       # Arrival Time
    bt: int       # Burst Time
    prio: int = 0 # Priority (lower = higher)
    ct: Optional[int] = None
    tat: Optional[int] = None
    wt: Optional[int] = None
    rt: Optional[int] = None
    rem: Optional[int] = None  # Remaining time for preemptive

Timeline = List[Tuple[str, int, int]]  # (pid, start_time, end_time)

# ---------------- Utilities ----------------
def finish_metrics(procs: Dict[str, Process], timeline: Timeline):
    """Calculate CT, TAT, WT, RT from timeline."""
    end_by_pid = {}
    first_run = {}
    for pid, start, end in timeline:
        end_by_pid[pid] = end
        if pid not in first_run:
            first_run[pid] = start
    for p in procs.values():
        p.ct = end_by_pid[p.pid]
        p.tat = p.ct - p.at
        p.wt = p.tat - p.bt
        p.rt = first_run[p.pid] - p.at

# ---------------- Scheduling Algorithms ----------------
def fcfs(processes: List[Process]) -> Tuple[List[Process], Timeline]:
    processes_sorted = sorted(processes, key=lambda p: (p.at, p.pid))
    time = 0
    timeline = []
    for p in processes_sorted:
        if time < p.at:
            time = p.at
        start = time
        end = start + p.bt
        timeline.append((p.pid, start, end))
        time = end
    proc_dict = {p.pid: Process(**p.__dict__) for p in processes}
    finish_metrics(proc_dict, timeline)
    return list(proc_dict.values()), timeline

def sjf_np(processes: List[Process]) -> Tuple[List[Process], Timeline]:
    procs_sorted = sorted(processes, key=lambda p: (p.at, p.bt, p.pid))
    time = 0
    completed = 0
    n = len(processes)
    timeline = []
    ready = []
    i = 0
    while completed < n:
        while i < n and procs_sorted[i].at <= time:
            ready.append(procs_sorted[i])
            i += 1
        if not ready:
            time = procs_sorted[i].at
            continue
        ready.sort(key=lambda p: (p.bt, p.at, p.pid))
        p = ready.pop(0)
        start = time
        end = start + p.bt
        timeline.append((p.pid, start, end))
        time = end
        completed += 1
    proc_dict = {p.pid: Process(**p.__dict__) for p in processes}
    finish_metrics(proc_dict, timeline)
    return list(proc_dict.values()), timeline

def srtf(processes: List[Process]) -> Tuple[List[Process], Timeline]:
    time = 0
    timeline = []
    remaining = {p.pid: p.bt for p in processes}
    first_run = {p.pid: None for p in processes}
    arrived = []
    procs_sorted = sorted(processes, key=lambda p: (p.at, p.pid))
    i = 0
    current = None
    slice_start = 0

    def pick():
        if not arrived:
            return None
        return min(arrived, key=lambda p: (remaining[p.pid], p.at, p.pid)).pid

    while any(remaining[p.pid] > 0 for p in processes):
        while i < len(procs_sorted) and procs_sorted[i].at <= time:
            arrived.append(procs_sorted[i])
            i += 1
        pid = pick()
        if pid is None:
            time += 1
            continue
        if current != pid:
            if current is not None and slice_start != time:
                timeline.append((current, slice_start, time))
            current = pid
            slice_start = time
            if first_run[pid] is None:
                first_run[pid] = time
        remaining[pid] -= 1
        time += 1
        if remaining[pid] == 0:
            timeline.append((pid, slice_start, time))
            arrived = [p for p in arrived if p.pid != pid]
            current = None
    proc_dict = {p.pid: Process(**p.__dict__) for p in processes}
    finish_metrics(proc_dict, timeline)
    for pid, start in first_run.items():
        proc_dict[pid].rt = start - proc_dict[pid].at
    return list(proc_dict.values()), timeline

def priority_np(processes: List[Process]) -> Tuple[List[Process], Timeline]:
    time = 0
    completed = 0
    n = len(processes)
    timeline = []
    procs_sorted = sorted(processes, key=lambda p: (p.at, p.prio, p.pid))
    ready = []
    i = 0
    while completed < n:
        while i < n and procs_sorted[i].at <= time:
            ready.append(procs_sorted[i])
            i += 1
        if not ready:
            time = procs_sorted[i].at
            continue
        ready.sort(key=lambda p: (p.prio, p.at, p.pid))
        p = ready.pop(0)
        start = time
        end = start + p.bt
        timeline.append((p.pid, start, end))
        time = end
        completed += 1
    proc_dict = {p.pid: Process(**p.__dict__) for p in processes}
    finish_metrics(proc_dict, timeline)
    return list(proc_dict.values()), timeline

def round_robin(processes: List[Process], quantum: int) -> Tuple[List[Process], Timeline]:
    if quantum <= 0:
        raise ValueError("Quantum must be > 0")
    time = 0
    timeline = []
    remaining = {p.pid: p.bt for p in processes}
    first_run = {p.pid: None for p in processes}
    ready = []
    procs_sorted = sorted(processes, key=lambda p: (p.at, p.pid))
    i = 0
    while any(remaining[p.pid] > 0 for p in processes):
        while i < len(procs_sorted) and procs_sorted[i].at <= time:
            ready.append(procs_sorted[i])
            i += 1
        if not ready:
            if i < len(procs_sorted):
                time = procs_sorted[i].at
                continue
            else:
                break
        p = ready.pop(0)
        start = time
        run_time = min(quantum, remaining[p.pid])
        if first_run[p.pid] is None:
            first_run[p.pid] = time
        time += run_time
        remaining[p.pid] -= run_time
        timeline.append((p.pid, start, time))
        # Add newly arrived during this quantum
        while i < len(procs_sorted) and procs_sorted[i].at <= time:
            ready.append(procs_sorted[i])
            i += 1
        if remaining[p.pid] > 0:
            ready.append(p)
    proc_dict = {p.pid: Process(**p.__dict__) for p in processes}
    finish_metrics(proc_dict, timeline)
    for pid, start in first_run.items():
        proc_dict[pid].rt = start - proc_dict[pid].at
    return list(proc_dict.values()), timeline

# ---------------- Example Test ----------------
if __name__ == "__main__":
    processes = [
        Process("P1", 0, 5, 2),
        Process("P2", 1, 3, 1),
        Process("P3", 2, 8, 3),
        Process("P4", 3, 6, 2),
    ]

    algos = {
        "FCFS": fcfs,
        "SJF NP": sjf_np,
        "SRTF": srtf,
        "Priority NP": priority_np,
        "RR": lambda procs: round_robin(procs, quantum=2)
    }

    for name, func in algos.items():
        print(f"\n--- {name} ---")
        result, timeline = func(processes)
        for p in result:
            print(f"{p.pid}: AT={p.at}, BT={p.bt}, CT={p.ct}, TAT={p.tat}, WT={p.wt}, RT={p.rt}")
        print("Timeline:", timeline)
