from qtpy.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QStackedWidget,
    QMainWindow, QSizePolicy, QLineEdit, QSpinBox, QTableWidget, QTableWidgetItem,
    QGridLayout, QMessageBox, QHBoxLayout, QSizePolicy
)
from qtpy.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys

# Scheduling Algorithms Implementations

def fcfs(processes):
    # Sort by Arrival Time
    processes = sorted(processes, key=lambda p: p['AT'])
    time = 0
    gantt = []
    for p in processes:
        if time < p['AT']:
            time = p['AT']
        p['ST'] = time
        p['CT'] = time + p['BT']
        p['TAT'] = p['CT'] - p['AT']
        p['WT'] = p['TAT'] - p['BT']
        p['RT'] = p['ST'] - p['AT']
        gantt.append((p['PID'], p['ST'], p['CT']))
        time = p['CT']
    return processes, gantt

def sjf_non_preemptive(processes):
    # Non-preemptive SJF
    n = len(processes)
    completed = 0
    time = 0
    is_completed = [False]*n
    gantt = []
    proc_list = [p.copy() for p in processes]

    while completed < n:
        # Pick process with minimum BT from available
        idx = -1
        min_bt = float('inf')
        for i, p in enumerate(proc_list):
            if p['AT'] <= time and not is_completed[i]:
                if p['BT'] < min_bt:
                    min_bt = p['BT']
                    idx = i
                elif p['BT'] == min_bt:
                    # Tie breaker by arrival time
                    if p['AT'] < proc_list[idx]['AT']:
                        idx = i
        if idx == -1:
            time +=1
        else:
            p = proc_list[idx]
            p['ST'] = time
            p['CT'] = time + p['BT']
            p['TAT'] = p['CT'] - p['AT']
            p['WT'] = p['TAT'] - p['BT']
            p['RT'] = p['ST'] - p['AT']
            time = p['CT']
            is_completed[idx] = True
            completed +=1
            gantt.append((p['PID'], p['ST'], p['CT']))

    # Preserve original order but updated fields
    pid_map = {p['PID']: p for p in proc_list}
    for p in processes:
        p.update(pid_map[p['PID']])
    return processes, gantt

def srtf(processes):
    # Preemptive SJF (SRTF)
    n = len(processes)
    proc_list = [p.copy() for p in processes]
    remaining_bt = [p['BT'] for p in proc_list]
    completed = 0
    time = 0
    minm = float('inf')
    shortest = None
    check = False
    start_time = [-1]*n
    ct = [0]*n
    gantt = []
    last_pid = None
    # Track timeline intervals for gantt
    timeline = []

    while completed != n:
        minm = float('inf')
        shortest = None
        for i in range(n):
            if proc_list[i]['AT'] <= time and remaining_bt[i] > 0:
                if remaining_bt[i] < minm:
                    minm = remaining_bt[i]
                    shortest = i
                elif remaining_bt[i] == minm:
                    if proc_list[i]['AT'] < proc_list[shortest]['AT']:
                        shortest = i
        if shortest is None:
            time +=1
            continue
        # Start time for response time
        if start_time[shortest] == -1:
            start_time[shortest] = time

        # If process switched, log gantt
        if last_pid != proc_list[shortest]['PID']:
            timeline.append((proc_list[shortest]['PID'], time))
            last_pid = proc_list[shortest]['PID']

        remaining_bt[shortest] -= 1
        time +=1

        if remaining_bt[shortest] == 0:
            completed +=1
            ct[shortest] = time
            proc_list[shortest]['CT'] = ct[shortest]
            proc_list[shortest]['TAT'] = ct[shortest] - proc_list[shortest]['AT']
            proc_list[shortest]['WT'] = proc_list[shortest]['TAT'] - proc_list[shortest]['BT']
            proc_list[shortest]['RT'] = start_time[shortest] - proc_list[shortest]['AT']

    # Close last gantt interval
    timeline.append(("END", time))

    # Convert timeline to gantt intervals
    gantt = []
    for i in range(len(timeline)-1):
        pid = timeline[i][0]
        start = timeline[i][1]
        end = timeline[i+1][1]
        gantt.append((pid, start, end))

    # Update original list
    pid_map = {p['PID']: p for p in proc_list}
    for p in processes:
        p.update(pid_map[p['PID']])
    return processes, gantt

def priority_non_preemptive(processes):
    # Non-preemptive priority scheduling (lower number = higher priority)
    n = len(processes)
    proc_list = [p.copy() for p in processes]
    completed = 0
    time = 0
    is_completed = [False]*n
    gantt = []

    while completed < n:
        idx = -1
        highest_priority = float('inf')
        for i, p in enumerate(proc_list):
            if p['AT'] <= time and not is_completed[i]:
                if p['Priority'] < highest_priority:
                    highest_priority = p['Priority']
                    idx = i
                elif p['Priority'] == highest_priority:
                    if p['AT'] < proc_list[idx]['AT']:
                        idx = i
        if idx == -1:
            time +=1
        else:
            p = proc_list[idx]
            p['ST'] = time
            p['CT'] = time + p['BT']
            p['TAT'] = p['CT'] - p['AT']
            p['WT'] = p['TAT'] - p['BT']
            p['RT'] = p['ST'] - p['AT']
            time = p['CT']
            is_completed[idx] = True
            completed +=1
            gantt.append((p['PID'], p['ST'], p['CT']))

    pid_map = {p['PID']: p for p in proc_list}
    for p in processes:
        p.update(pid_map[p['PID']])
    return processes, gantt

def round_robin(processes, quantum=2):
    # Preemptive Round Robin Scheduling
    proc_list = [p.copy() for p in processes]
    n = len(proc_list)
    rem_bt = [p['BT'] for p in proc_list]
    time = 0
    queue = []
    gantt = []

    # Sort by arrival time and add processes as they come
    proc_list = sorted(proc_list, key=lambda x: x['AT'])
    completed = 0
    visited = [False]*n
    last_exec = -1

    # For RT
    start_time = [-1]*n

    # Add first process(es) arrived at time 0
    for i, p in enumerate(proc_list):
        if p['AT'] <= time and not visited[i]:
            queue.append(i)
            visited[i] = True

    while completed < n:
        if not queue:
            # No process in queue, move time forward
            time += 1
            for i, p in enumerate(proc_list):
                if p['AT'] <= time and not visited[i]:
                    queue.append(i)
                    visited[i] = True
            continue
        idx = queue.pop(0)
        if start_time[idx] == -1:
            start_time[idx] = time
        exec_time = min(quantum, rem_bt[idx])
        # Add to Gantt chart
        gantt.append((proc_list[idx]['PID'], time, time + exec_time))
        time += exec_time
        rem_bt[idx] -= exec_time

        # Add new processes which have arrived in this time
        for i, p in enumerate(proc_list):
            if p['AT'] > time - exec_time and p['AT'] <= time and not visited[i]:
                queue.append(i)
                visited[i] = True

        if rem_bt[idx] == 0:
            completed +=1
            proc_list[idx]['CT'] = time
            proc_list[idx]['TAT'] = proc_list[idx]['CT'] - proc_list[idx]['AT']
            proc_list[idx]['WT'] = proc_list[idx]['TAT'] - proc_list[idx]['BT']
            proc_list[idx]['RT'] = start_time[idx] - proc_list[idx]['AT']
        else:
            queue.append(idx)

    # Update original list
    pid_map = {p['PID']: p for p in proc_list}
    for p in processes:
        p.update(pid_map[p['PID']])

    return processes, gantt


class GanttChartCanvas(FigureCanvas):
    def __init__(self, gantt_data, parent=None):
        fig = Figure(figsize=(8, 2))
        super().__init__(fig)
        self.setParent(parent)
        self.axes = fig.add_subplot(111)
        self.gantt_data = gantt_data or []
        self.draw_gantt()

    def draw_gantt(self):
        ax = self.axes
        ax.clear()
        ax.set_title("Gantt Chart")
        ax.set_xlabel("Time")
        ax.set_yticks([])  # Hide y-axis
        ax.grid(True, axis='x')

        if not self.gantt_data:
            ax.text(0.5, 0.5, "No Gantt Data", ha='center', va='center')
            self.draw()
            return

        try:
            # Plot Gantt bars
            for pid, start, end in self.gantt_data:
                ax.barh(0, end - start, left=start, height=0.5, align='center', edgecolor='black')
                ax.text((start + end) / 2, 0, f"P{pid}", ha='center', va='center', color='white', fontweight='bold')

            # Collect context switch times (start + end times)
            switch_times = sorted(set([start for _, start, _ in self.gantt_data] +
                                    [end for _, _, end in self.gantt_data]))

            # Set x-axis ticks only at context switch times
            ax.set_xticks(switch_times)
            ax.set_xticklabels([str(t) for t in switch_times])

            # Set grid only at those times
            ax.set_xlim(0, max(switch_times))
            ax.xaxis.grid(True, which='major')

            self.draw()

        except Exception as e:
            print("Error drawing Gantt chart:", e)
            ax.text(0.5, 0.5, "Error Drawing Gantt Chart", ha='center', va='center')
            self.draw()





class ResultScreen(QWidget):
    def __init__(self, processes, gantt_data, algorithm, on_back):
        super().__init__()
        self.processes = processes
        self.gantt_data = gantt_data
        self.algorithm = algorithm
        self.on_back = on_back
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        title = QLabel(f"Results - {self.algorithm}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold;")
        layout.addWidget(title)

        # Table with Process Results
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(['PID', 'AT', 'BT', 'Priority', 'CT', 'TAT', 'WT'])
        table.setRowCount(len(self.processes))
        for i, p in enumerate(self.processes):
            table.setItem(i, 0, QTableWidgetItem(str(p['PID'])))
            table.setItem(i, 1, QTableWidgetItem(str(p['AT'])))
            table.setItem(i, 2, QTableWidgetItem(str(p['BT'])))
            table.setItem(i, 3, QTableWidgetItem(str(p.get('Priority', '-'))))
            table.setItem(i, 4, QTableWidgetItem(str(p.get('CT', '-'))))
            table.setItem(i, 5, QTableWidgetItem(str(p.get('TAT', '-'))))
            table.setItem(i, 6, QTableWidgetItem(str(p.get('WT', '-'))))
        table.resizeColumnsToContents()
        layout.addWidget(table)

        # Calculate averages
        total_tat = sum(p.get('TAT',0) for p in self.processes)
        total_wt = sum(p.get('WT',0) for p in self.processes)
        n = len(self.processes)
        avg_tat = total_tat / n if n else 0
        avg_wt = total_wt / n if n else 0

        avg_label = QLabel(f"Average Turnaround Time (TAT): {avg_tat:.2f}    Average Waiting Time (WT): {avg_wt:.2f}")
        avg_label.setAlignment(Qt.AlignCenter)
        avg_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin: 10px;")
        layout.addWidget(avg_label)

        # Gantt chart
        gantt_chart = GanttChartCanvas(self.gantt_data)
        gantt_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(gantt_chart)

        # Back button
        back_btn = QPushButton("Back to Process Input")
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn)

        self.setLayout(layout)


class ProcessInputScreen(QWidget):
    def __init__(self, on_back, on_run, selected_algo):
        super().__init__()
        self.on_back = on_back
        self.on_run = on_run
        self.selected_algo = selected_algo
        self.processes = []
        self.pid_counter = 1
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        title = QLabel(f"Algorithm Selected: {self.selected_algo}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        form_layout = QGridLayout()

        # Arrival Time
        self.arrival_input = QSpinBox()
        self.arrival_input.setRange(0, 1000)
        self.arrival_input.setButtonSymbols(QSpinBox.NoButtons)  # 🔹 Removes arrow buttons
        form_layout.addWidget(QLabel("Arrival Time (AT):"), 0, 0)
        form_layout.addWidget(self.arrival_input, 0, 1)

        # Burst Time
        self.burst_input = QSpinBox()
        self.burst_input.setRange(1, 1000)
        self.burst_input.setButtonSymbols(QSpinBox.NoButtons)  # 🔹 Removes arrow buttons
        form_layout.addWidget(QLabel("Burst Time (BT):"), 1, 0)
        form_layout.addWidget(self.burst_input, 1, 1)

        # Priority (only for Priority algo)
        self.priority_input = QSpinBox()
        self.priority_input.setRange(1, 1000)
        self.priority_input.setButtonSymbols(QSpinBox.NoButtons)  # 🔹 Removes arrow buttons
        if self.selected_algo == "Priority Non-Preemptive":
            form_layout.addWidget(QLabel("Priority:"), 2, 0)
            form_layout.addWidget(self.priority_input, 2, 1)

        layout.addLayout(form_layout)

        # Add process button
        add_btn = QPushButton("Add Process")
        add_btn.clicked.connect(self.add_process)
        layout.addWidget(add_btn)

        # Processes table
        self.table = QTableWidget()
        self.table.setColumnCount(4 if self.selected_algo=="Priority Non-Preemptive" else 3)
        headers = ['PID', 'Arrival Time', 'Burst Time']
        if self.selected_algo == "Priority Non-Preemptive":
            headers.append('Priority')
        self.table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.table)

        # Run Scheduler button
        run_btn = QPushButton("Run Scheduler")
        run_btn.clicked.connect(self.run_scheduler)
        layout.addWidget(run_btn)

        # Back button
        back_btn = QPushButton("Back to Algorithm Selection")
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def add_process(self):
        at = self.arrival_input.value()
        bt = self.burst_input.value()
        p = {'PID': self.pid_counter, 'AT': at, 'BT': bt}
        if self.selected_algo == "Priority Non-Preemptive":
            pr = self.priority_input.value()
            p['Priority'] = pr

        # Basic validation: AT and BT positive, PID unique
        if bt <= 0:
            QMessageBox.warning(self, "Invalid Input", "Burst time must be > 0")
            return
        if at < 0:
            QMessageBox.warning(self, "Invalid Input", "Arrival time cannot be negative")
            return

        self.processes.append(p)
        self.pid_counter += 1
        self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.processes))
        for i, p in enumerate(self.processes):
            self.table.setItem(i, 0, QTableWidgetItem(str(p['PID'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(p['AT'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(p['BT'])))
            if self.selected_algo == "Priority Non-Preemptive":
                self.table.setItem(i, 3, QTableWidgetItem(str(p.get('Priority','-'))))

    def run_scheduler(self):
        if not self.processes:
            QMessageBox.warning(self, "No Processes", "Please add at least one process before running scheduler.")
            return
        algo = self.selected_algo
        procs = [p.copy() for p in self.processes]

        # Run the selected algorithm
        if algo == "FCFS":
            procs, gantt = fcfs(procs)
        elif algo == "SJF Non-Preemptive":
            procs, gantt = sjf_non_preemptive(procs)
        elif algo == "SRTF":
            procs, gantt = srtf(procs)
        elif algo == "Priority Non-Preemptive":
            procs, gantt = priority_non_preemptive(procs)
        elif algo == "Round Robin":
            # For demo, quantum=2 fixed, can be enhanced to user input later
            procs, gantt = round_robin(procs, quantum=2)
        else:
            QMessageBox.warning(self, "Error", f"Algorithm {algo} not supported.")
            return

        # Call on_run callback to show results screen
        self.on_run(procs, gantt, algo)


class AlgorithmSelectionScreen(QWidget):
    def __init__(self, on_select):
        super().__init__()
        self.on_select = on_select
        self.algorithms = [
            "FCFS",
            "SJF Non-Preemptive",
            "SRTF",
            "Priority Non-Preemptive",
            "Round Robin"
        ]
        self.current_index = 0
        self.initUI()
        self.setFocusPolicy(Qt.StrongFocus)  # Allow widget to receive keyboard focus
        self.setFocus()  # Set focus so key events are received immediately

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("CPU Scheduler")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        subtitle = QLabel("Please select an algorithm to execute")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 18pt; margin-bottom: 30px;")
        layout.addWidget(subtitle)

        self.algo_labels = []
        for i, algo in enumerate(self.algorithms):
            label = QLabel(algo)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 16pt; margin: 4px;")
            layout.addWidget(label)
            self.algo_labels.append(label)

        self.update_highlight()

        # Instructions label
        inst = QLabel("Use Up/Down arrow keys to navigate, Enter to select")
        inst.setAlignment(Qt.AlignCenter)
        inst.setStyleSheet("font-size: 12pt; margin-top: 20px; font-style: italic;")
        layout.addWidget(inst)

        self.setLayout(layout)

    def update_highlight(self):
        for i, label in enumerate(self.algo_labels):
            if i == self.current_index:
                label.setStyleSheet("font-size: 16pt; margin: 4px; background-color: #87CEFA; font-weight: bold;")
            else:
                label.setStyleSheet("font-size: 16pt; margin: 4px;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            self.current_index = (self.current_index + 1) % len(self.algorithms)
            self.update_highlight()
        elif event.key() == Qt.Key_Up:
            self.current_index = (self.current_index - 1) % len(self.algorithms)
            self.update_highlight()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            selected_algo = self.algorithms[self.current_index]
            self.on_select(selected_algo)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduling Simulator")
        self.resize(800, 600)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Algorithm selection screen
        self.alg_screen = AlgorithmSelectionScreen(self.on_algo_selected)
        self.stack.addWidget(self.alg_screen)

        self.proc_input_screen = None
        self.result_screen = None

    def on_algo_selected(self, algo):
        # Create new ProcessInputScreen for selected algorithm
        self.proc_input_screen = ProcessInputScreen(self.back_to_algo, self.show_results, algo)
        self.stack.addWidget(self.proc_input_screen)
        self.stack.setCurrentWidget(self.proc_input_screen)

    def back_to_algo(self):
        self.stack.setCurrentWidget(self.alg_screen)
        # Remove other screens if desired
        if self.proc_input_screen:
            self.stack.removeWidget(self.proc_input_screen)
            self.proc_input_screen.deleteLater()
            self.proc_input_screen = None
        if self.result_screen:
            self.stack.removeWidget(self.result_screen)
            self.result_screen.deleteLater()
            self.result_screen = None

    def show_results(self, processes, gantt_data, algorithm):
        # Create results screen and switch
        self.result_screen = ResultScreen(processes, gantt_data, algorithm, self.back_to_proc_input)
        self.stack.addWidget(self.result_screen)
        self.stack.setCurrentWidget(self.result_screen)

    def back_to_proc_input(self):
        self.stack.setCurrentWidget(self.proc_input_screen)
        # Remove result screen
        if self.result_screen:
            self.stack.removeWidget(self.result_screen)
            self.result_screen.deleteLater()
            self.result_screen = None


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
