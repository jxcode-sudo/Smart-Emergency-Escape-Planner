import tkinter as tk
from tkinter import ttk, messagebox
import heapq, math
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Sample building: (location A, location B, walking cost)
EDGES = [
    ("Entrance", "Hall A", 2), ("Hall A", "Room 101", 2),
    ("Hall A", "Hall B", 3), ("Hall B", "Room 102", 2),
    ("Hall B", "Staircase 1", 2), ("Staircase 1", "Exit 1", 3),
    ("Hall B", "Hall C", 2), ("Hall C", "Room 201", 2),
    ("Hall C", "Staircase 2", 2), ("Staircase 2", "Exit 2", 2),
    ("Room 101", "Hall C", 5), ("Room 102", "Hall C", 3),
    ("Room 201", "Exit 2", 4),
]
POS = {
    "Entrance": (0, 2), "Hall A": (1, 2), "Room 101": (1, 3),
    "Hall B": (2.4, 2), "Room 102": (2.4, 3),
    "Staircase 1": (3.5, 2.6), "Exit 1": (4.7, 2.6),
    "Hall C": (3.5, 1.3), "Room 201": (3.5, 0.2),
    "Staircase 2": (4.7, 1.3), "Exit 2": (5.9, 1.3),
}
EXITS = ["Exit 1", "Exit 2"]

class App:
    def __init__(self, root):
        self.root = root
        root.title("Smart Emergency Escape Planner | DAA")
        root.geometry("1150x760")
        root.configure(bg="#f1f5f9")
        self.blocked = set()
        self.graph = nx.Graph()
        self.make_graph()
        self.start = tk.StringVar(value="Room 101")
        self.destination = tk.StringVar(value="Nearest available exit")
        self.corridor = tk.StringVar()
        self.path = []
        self.build_ui()
        self.refresh_corridors()
        self.draw()

    def make_graph(self):
        self.graph.clear()
        self.graph.add_nodes_from(POS)
        for a, b, w in EDGES:
            if tuple(sorted((a, b))) not in self.blocked:
                self.graph.add_edge(a, b, weight=w)

    def build_ui(self):
        header = tk.Frame(self.root, bg="#17324d", padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="SMART EMERGENCY ESCAPE PLANNER",
                 font=("Segoe UI", 18, "bold"), fg="white", bg="#17324d").pack(anchor="w")
        tk.Label(header, text="DAA project • Dijkstra shortest-path algorithm",
                 font=("Segoe UI", 10), fg="#dbeafe", bg="#17324d").pack(anchor="w")

        body = tk.Frame(self.root, bg="#f1f5f9", padx=12, pady=12)
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg="white", padx=12, pady=12, width=260)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)
        tk.Label(left, text="ROUTE CONTROLS", bg="white",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))

        tk.Label(left, text="Starting location", bg="white").pack(anchor="w")
        ttk.Combobox(left, textvariable=self.start, values=list(POS),
                     state="readonly").pack(fill="x", pady=(3, 10))
        tk.Label(left, text="Destination", bg="white").pack(anchor="w")
        ttk.Combobox(left, textvariable=self.destination,
                     values=["Nearest available exit"] + EXITS,
                     state="readonly").pack(fill="x", pady=(3, 10))
        ttk.Button(left, text="Find Escape Route", command=self.find_route).pack(fill="x", pady=3)
        ttk.Button(left, text="Reset Building", command=self.reset).pack(fill="x", pady=3)
        ttk.Separator(left).pack(fill="x", pady=12)

        tk.Label(left, text="Block / reopen corridor", bg="white",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Combobox(left, textvariable=self.corridor, state="readonly").pack(
            fill="x", pady=6)
        ttk.Button(left, text="Toggle Corridor", command=self.toggle).pack(fill="x")
        ttk.Separator(left).pack(fill="x", pady=12)
        tk.Label(left, text="Algorithm: Dijkstra\n"
                 "Time: O((V + E) log V)\n"
                 "Space: O(V + E)\n\n"
                 "V = locations\nE = corridors\n\n"
                 "Green: selected route\nRed dashed: blocked corridor",
                 bg="white", justify="left", font=("Consolas", 9)).pack(anchor="w")

        right = tk.Frame(body, bg="white", padx=10, pady=10)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Building Map", bg="white",
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.fig = Figure(figsize=(7.4, 4.3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=.02, right=.98, top=.92, bottom=.03)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        tk.Label(right, text="Algorithm steps", bg="white",
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(6, 3))
        self.log = tk.Text(right, height=9, wrap="word", font=("Consolas", 9),
                           bg="#f8fafc", relief="flat")
        self.log.pack(fill="x")
        self.status = tk.StringVar(value="Choose a start location and find a route.")
        tk.Label(self.root, textvariable=self.status, bg="#dbeafe",
                 fg="#17324d", anchor="w", padx=12, pady=7).pack(fill="x")
        tk.Label(self.root, text="Educational simulation only; not for real emergency navigation.",
                 bg="#f1f5f9", fg="#64748b", font=("Segoe UI", 8)).pack(pady=4)

    def refresh_corridors(self):
        choices = []
        for a, b, w in EDGES:
            label = f"{a} <-> {b} (cost {w})"
            if tuple(sorted((a, b))) in self.blocked:
                label += " [BLOCKED]"
            choices.append(label)
        self.corridor_box_values = choices
        # Find the combobox created in the controls panel.
        for child in self.root.winfo_children():
            pass
        # Store/update the corridor combobox directly.
        if hasattr(self, "corridor_combo"):
            self.corridor_combo["values"] = choices
            if self.corridor.get() not in choices and choices:
                self.corridor.set(choices[0])

    def _corridor_widget_fix(self):
        pass

    def toggle(self):
        selected = self.corridor.get()
        for a, b, w in EDGES:
            label = f"{a} <-> {b} (cost {w})"
            if selected.startswith(label):
                key = tuple(sorted((a, b)))
                if key in self.blocked:
                    self.blocked.remove(key)
                    self.status.set(f"Reopened corridor: {a} <-> {b}")
                else:
                    self.blocked.add(key)
                    self.status.set(f"Blocked corridor: {a} <-> {b}")
                self.make_graph()
                self.refresh_corridors()
                self.draw()
                self.find_route()
                return

    def reset(self):
        self.blocked.clear()
        self.make_graph()
        self.refresh_corridors()
        self.path = []
        self.draw()
        self.log.delete("1.0", "end")
        self.status.set("Building reset. All corridors are open.")

    def dijkstra(self, start):
        dist = {n: math.inf for n in self.graph.nodes}
        prev = {n: None for n in self.graph.nodes}
        dist[start] = 0
        queue = [(0, start)]
        visited = []
        steps = [f"1. Set distance of {start} to 0; all other distances to infinity."]
        count = 2
        while queue:
            d, u = heapq.heappop(queue)
            if d != dist[u] or u in visited:
                continue
            visited.append(u)
            steps.append(f"{count}. Visit {u} with cost {d}.")
            count += 1
            for v in sorted(self.graph.neighbors(u)):
                nd = d + self.graph[u][v]["weight"]
                if nd < dist[v]:
                    old = "∞" if dist[v] == math.inf else str(dist[v])
                    dist[v], prev[v] = nd, u
                    heapq.heappush(queue, (nd, v))
                    steps.append(f"{count}. Update {v}: {old} -> {nd} through {u}.")
                    count += 1
        return dist, prev, visited, steps

    def find_route(self):
        start = self.start.get()
        dist, prev, visited, steps = self.dijkstra(start)
        choice = self.destination.get()
        reachable = [e for e in EXITS if dist[e] < math.inf]
        if choice == "Nearest available exit":
            if not reachable:
                self.path = []
                self.log.delete("1.0", "end")
                self.log.insert("end", "\n".join(steps + ["No exit is reachable."]))
                self.status.set("No reachable exit. Try reopening a corridor.")
                self.draw()
                return
            target = min(reachable, key=lambda e: dist[e])
        else:
            target = choice
        if dist[target] == math.inf:
            self.path = []
            self.log.delete("1.0", "end")
            self.log.insert("end", "\n".join(steps + [f"{target} is unreachable from {start}."]))
            self.status.set(f"No route from {start} to {target}.")
            self.draw()
            return
        path, node = [], target
        while node is not None:
            path.append(node)
            node = prev[node]
        self.path = path[::-1]
        steps += ["", f"Destination: {target}",
                  "Shortest route: " + " -> ".join(self.path),
                  f"Total cost: {dist[target]} units",
                  f"Visited locations: {len(visited)} of {len(self.graph.nodes)}"]
        self.log.delete("1.0", "end")
        self.log.insert("end", "\n".join(steps))
        self.status.set(f"Route: {' -> '.join(self.path)} | Total cost: {dist[target]} units")
        self.draw()

    def draw(self):
        self.ax.clear()
        open_edges, blocked_edges, route_edges = [], [], []
        for a, b, w in EDGES:
            edge = (a, b)
            if tuple(sorted(edge)) in self.blocked:
                blocked_edges.append(edge)
            else:
                open_edges.append(edge)
        route_edges = [(self.path[i], self.path[i+1]) for i in range(len(self.path)-1)]
        nx.draw_networkx_edges(self.graph, POS, ax=self.ax, edgelist=open_edges,
                               edge_color="#94a3b8", width=2)
        if blocked_edges:
            nx.draw_networkx_edges(self.graph, POS, ax=self.ax, edgelist=blocked_edges,
                                   edge_color="#dc2626", style="dashed", width=2)
        if route_edges:
            nx.draw_networkx_edges(self.graph, POS, ax=self.ax, edgelist=route_edges,
                                   edge_color="#16a34a", width=4)
        colors = ["#16a34a" if n in EXITS else "#bbf7d0" if n in self.path
                  else "#fde68a" if n.startswith("Staircase") else "#bfdbfe"
                  for n in self.graph.nodes]
        nx.draw_networkx_nodes(self.graph, POS, ax=self.ax, node_color=colors,
                               node_size=1650, edgecolors="#334155")
        nx.draw_networkx_labels(self.graph, POS, ax=self.ax, font_size=8,
                                font_weight="bold")
        labels = {(a, b): ("X" if tuple(sorted((a, b))) in self.blocked else str(w))
                  for a, b, w in EDGES}
        nx.draw_networkx_edge_labels(self.graph, POS, edge_labels=labels,
                                     ax=self.ax, font_size=8,
                                     bbox={"alpha": .7, "color": "white", "pad": 1})
        self.ax.set_title("Sample building layout • corridor cost shown on edges", fontsize=10)
        self.ax.axis("off")
        self.canvas.draw_idle()

# Replace the corridor selector with a stored widget so it can be refreshed.
_original_build_ui = App.build_ui
def build_ui_with_saved_corridor(self):
    _original_build_ui(self)
    # The corridor combobox is the one immediately after the "Block / reopen corridor" label.
    left = self.root.winfo_children()[1].winfo_children()[0]
    for child in left.winfo_children():
        if isinstance(child, ttk.Combobox) and child.cget("state") == "readonly":
            # Comboboxes appear in order: start, destination, corridor.
            pass
    combos = [c for c in left.winfo_children() if isinstance(c, ttk.Combobox)]
    self.corridor_combo = combos[2]

App.build_ui = build_ui_with_saved_corridor

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
