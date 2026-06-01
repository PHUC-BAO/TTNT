import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import heapq

# ==============================================================================
# 1. CẤU HÌNH HƯỚNG DI CHUYỂN DÙNG CHUNG (Thứ tự ưu tiên: L -> R -> U -> D)
# ==============================================================================
ACTIONS = [
    ('L', (0, -1), "SANG TRÁI"),
    ('R', (0, 1), "SANG PHẢI"),
    ('U', (-1, 0), "LÊN"),
    ('D', (1, 0), "XUỐNG")
]

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return -1, -1

def swap(state, x1, y1, x2, y2):
    state = [list(row) for row in state]
    state[x1][y1], state[x2][y2] = state[x2][y2], state[x1][y1]
    return tuple(tuple(row) for row in state)

# Hàm Heuristic: Tính tổng khoảng cách Manhattan từ trạng thái hiện tại đến đích
def manhattan_distance(current, goal):
    goal_pos = {}
    for r in range(3):
        for c in range(3):
            goal_pos[goal[r][c]] = (r, c)

    distance = 0
    for r in range(3):
        for c in range(3):
            val = current[r][c]
            if val != 0:
                target_r, target_c = goal_pos[val]
                distance += abs(r - target_r) + abs(c - target_c)
    return distance

# ==============================================================================
# 2. KHU VỰC THUẬT TOÁN
# ==============================================================================

# 2.1 THUẬT TOÁN BFS
def run_bfs(start, goal, max_steps):
    queue = deque()
    queue.append((start, [], "Trạng thái khởi đầu (START)."))
    visited = set()
    visited.add(start)
    states_history = []

    while queue:
        if len(states_history) >= max_steps:
            return None, states_history

        current, path, info = queue.popleft()
        states_history.append((current, info))

        if current == goal:
            return path, states_history

        x, y = find_zero(current)
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = swap(current, x, y, nx, ny)
                if new_state not in visited:
                    swapped_val = current[nx][ny]
                    desc = f"Hành động [{move}]: Di chuyển ô trống {move_name}, hoán đổi với số ({swapped_val})."
                    visited.add(new_state)
                    queue.append((new_state, path + [move], desc))
    return None, states_history


# 2.2 THUẬT TOÁN DFS
def run_dfs(start, goal, max_steps):
    stack = []
    stack.append((start, [], "Trạng thái khởi đầu (START)."))
    visited = set()
    states_history = []

    while stack:
        if len(states_history) >= max_steps:
            return None, states_history

        current, path, info = stack.pop()

        if current in visited:
            continue
        visited.add(current)

        states_history.append((current, info))

        if current == goal:
            return path, states_history

        x, y = find_zero(current)
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = swap(current, x, y, nx, ny)
                if new_state not in visited:
                    swapped_val = current[nx][ny]
                    desc = f"Hành động [{move}]: Đẩy vào Stack hướng {move_name} (đổi với số {swapped_val})."
                    stack.append((new_state, path + [move], desc))

    return None, states_history


# 2.3 THUẬT TOÁN IDFS
def dls_for_gui(current, goal, limit, path, visited, states_history, last_info, max_steps):
    if len(states_history) >= max_steps:
        return "LIMIT_EXCEEDED"

    states_history.append((current, last_info))

    if current == goal:
        return path
    if limit <= 0:
        return None

    visited.add(current)
    x, y = find_zero(current)

    for move, (dx, dy), move_name in ACTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            neighbor = swap(current, x, y, nx, ny)
            if neighbor not in visited:
                swapped_val = current[nx][ny]
                desc = f"Tầng sâu giới hạn = {limit}. Đi tiếp hướng [{move}] {move_name} (đổi với số {swapped_val})."
                result = dls_for_gui(neighbor, goal, limit - 1, path + [move], visited, states_history, desc, max_steps)
                if result is not None:
                    return result

    return None


def run_idfs(start, goal, max_steps):
    depth = 0
    states_history = []

    while True:
        visited = set()
        init_info = f"--- Bắt đầu dò tìm vòng lặp mới với Giới hạn độ sâu = {depth} ---"
        result = dls_for_gui(start, goal, depth, [], visited, states_history, init_info, max_steps)

        if result == "LIMIT_EXCEEDED":
            return None, states_history
        if result is not None:
            return result, states_history

        depth += 1


# 2.4 THUẬT TOÁN UCS
def run_ucs(start, goal, max_steps):
    step_count = 0
    frontier = []
    heapq.heappush(frontier, (0, step_count, start, [], "Trạng thái khởi đầu (START) với Chi phí g = 0."))

    explored = set()
    frontier_costs = {start: 0}
    states_history = []

    while frontier:
        if len(states_history) >= max_steps:
            return None, states_history

        g_cost, _, current, path, info = heapq.heappop(frontier)

        if current in explored:
            continue
        states_history.append((current, info))

        if current == goal:
            return path, states_history

        explored.add(current)
        r, c = find_zero(current)

        for move, (dx, dy), move_name in ACTIONS:
            new_r, new_c = r + dx, c + dy
            if 0 <= new_r < 3 and 0 <= new_c < 3:
                next_state = swap(current, r, c, new_r, new_c)
                action_cost = 1
                new_g = g_cost + action_cost

                if next_state in explored:
                    continue

                if next_state not in frontier_costs or new_g < frontier_costs[next_state]:
                    frontier_costs[next_state] = new_g
                    desc = (f"Lấy ra nút có g = {g_cost}. Di chuyển [{move}] {move_name} "
                            f"(đổi chỗ ô số {action_cost}, chi phí bước g tăng +{action_cost} -> tổng g = {new_g}).")
                    step_count += 1
                    heapq.heappush(frontier, (new_g, step_count, next_state, path + [move], desc))

    return None, states_history


# 2.5 THUẬT TOÁN A*
def run_astar(start, goal, max_steps):
    step_count = 0
    frontier = []
    h_start = manhattan_distance(start, goal)
    heapq.heappush(frontier, (h_start, step_count, 0, start, [], f"Khởi tạo START. g=0, h={h_start} -> f={h_start}"))

    explored = set()
    frontier_costs = {start: 0}
    states_history = []

    while frontier:
        if len(states_history) >= max_steps:
            return None, states_history

        f_cost, _, g_cost, current, path, info = heapq.heappop(frontier)

        if current in explored:
            continue
        states_history.append((current, info))

        if current == goal:
            return path, states_history

        explored.add(current)
        r, c = find_zero(current)

        for move, (dx, dy), move_name in ACTIONS:
            new_r, new_c = r + dx, c + dy
            if 0 <= new_r < 3 and 0 <= new_c < 3:
                next_state = swap(current, r, c, new_r, new_c)
                action_cost = 1
                new_g = g_cost + action_cost

                if next_state in explored:
                    continue

                if next_state not in frontier_costs or new_g < frontier_costs[next_state]:
                    frontier_costs[next_state] = new_g
                    new_h = manhattan_distance(next_state, goal)
                    new_f = new_g + new_h

                    desc = (f"Xét nút có g={g_cost}. Di chuyển [{move}] {move_name} (đổi số {action_cost}). "
                            f"Cập nhật: g={new_g}, h(Manhattan)={new_h} -> f={new_f}")
                    step_count += 1
                    heapq.heappush(frontier, (new_f, step_count, new_g, next_state, path + [move], desc))

    return None, states_history


# 2.6 THUẬT TOÁN GREEDY BEST-FIRST SEARCH
def run_greedy(start, goal, max_steps):
    step_count = 0
    frontier = []

    # Greedy chỉ đánh giá dựa trên h(n)
    h_start = manhattan_distance(start, goal)
    heapq.heappush(frontier, (h_start, step_count, start, [], f"Khởi tạo START. Đánh giá Heuristic h={h_start}"))

    explored = set()
    states_history = []

    while frontier:
        if len(states_history) >= max_steps:
            return None, states_history

        h_cost, _, current, path, info = heapq.heappop(frontier)

        if current in explored:
            continue
        states_history.append((current, info))

        if current == goal:
            return path, states_history

        explored.add(current)
        r, c = find_zero(current)

        for move, (dx, dy), move_name in ACTIONS:
            new_r, new_c = r + dx, c + dy
            if 0 <= new_r < 3 and 0 <= new_c < 3:
                next_state = swap(current, r, c, new_r, new_c)

                if next_state not in explored:
                    new_h = manhattan_distance(next_state, goal)
                    desc = (f"Tham lam lấy nút có h={h_cost}. Di chuyển hướng [{move}] {move_name} "
                            f"(đổi vị trí ô số {current[new_r][new_c]}). Ước lượng khoảng cách mới h={new_h}")
                    step_count += 1
                    heapq.heappush(frontier, (new_h, step_count, next_state, path + [move], desc))

    return None, states_history


# 2.7 THUẬT TOÁN IDA* (Iterative Deepening A*)
def idfs_astar_for_gui(current, goal, g_cost, f_limit, path, visited, states_history, last_info, max_steps):
    if len(states_history) >= max_steps:
        return "LIMIT_EXCEEDED", max_steps

    h_cost = manhattan_distance(current, goal)
    f_cost = g_cost + h_cost

    states_history.append((current, last_info))

    if current == goal:
        return path, f_cost
    if f_cost > f_limit:
        return None, f_cost  # Trả về giá trị f lớn hơn để làm mốc limit tiếp theo

    visited.add(current)
    x, y = find_zero(current)
    min_cutoff = float('inf')

    for move, (dx, dy), move_name in ACTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            neighbor = swap(current, x, y, nx, ny)
            if neighbor not in visited:
                swapped_val = current[nx][ny]
                new_g = g_cost + 1
                new_h = manhattan_distance(neighbor, goal)
                new_f = new_g + new_h

                desc = f"Giới hạn f_limit = {f_limit}. Xét [{move}] {move_name} (đổi số {swapped_val}): g={new_g}, h={new_h} -> f={new_f}"

                result, next_f = idfs_astar_for_gui(neighbor, goal, new_g, f_limit, path + [move], visited, states_history, desc, max_steps)

                if result == "LIMIT_EXCEEDED":
                    return "LIMIT_EXCEEDED", max_steps
                if result is not None:
                    return result, next_f

                if next_f < min_cutoff:
                    min_cutoff = next_f

    visited.remove(current) # Backtrack
    return None, min_cutoff

def run_idastar(start, goal, max_steps):
    states_history = []
    f_limit = manhattan_distance(start, goal)

    while True:
        visited = set()
        init_info = f"--- Khởi động vòng lặp IDA* mới với f_limit = {f_limit} ---"
        result, next_f = idfs_astar_for_gui(start, goal, 0, f_limit, [], visited, states_history, init_info, max_steps)

        if result == "LIMIT_EXCEEDED":
            return None, states_history
        if result is not None:
            return result, states_history
        if next_f == float('inf') or next_f == f_limit:
            # Không mở rộng thêm được nữa, bài toán vô nghiệm
            return None, states_history

        f_limit = next_f  # Nâng giới hạn f lên mức nhỏ nhất vượt ngưỡng cũ



# 2.8 THUẬT TOÁN SIMPLE HILL CLIMBING (Leo đồi đơn giản)
def run_hill_climbing(start, goal, max_steps):
    current = start
    path = []
    states_history = []

    curr_h = manhattan_distance(current, goal)
    states_history.append((current, f"Bắt đầu tại START. Heuristic hiện tại h = {curr_h}"))

    while current != goal:
        if len(states_history) >= max_steps:
            return None, states_history

        x, y = find_zero(current)
        neighbor_moved = False

        # Duyệt qua các hướng theo thứ tự ưu tiên L -> R -> U -> D
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)

                # Simple Hill Climbing: Chọn ngay nút ĐẦU TIÊN có cải thiện (hoặc bằng)
                if neighbor_h < curr_h:
                    current = neighbor
                    curr_h = neighbor_h
                    path.append(move)
                    swapped_val = current[x][y] # Giá trị cũ tại vị trí mới đổi

                    desc = f"Hành động [{move}]: Leo đồi thành công sang {move_name} (đổi số {swapped_val}). h mới = {curr_h} tốt hơn h cũ."
                    states_history.append((current, desc))
                    neighbor_moved = True
                    break # Đi tiếp luôn từ trạng thái mới, bỏ qua các hướng còn lại

        # Nếu duyệt qua tất cả các hướng mà không tìm được trạng thái nào tốt hơn -> Kẹt cục bộ
        if not neighbor_moved:
            states_history.append((current, f"🛑 KẸT CỤC BỘ (Local Optimum)! Không có hướng nào quanh đây giảm h xuống dưới {curr_h}. Thuật toán dừng lại."))
            return None, states_history

    return path, states_history



# ==============================================================================
# 3. GIAO DIỆN ỨNG DỤNG
# ==============================================================================
class PuzzleApp:

    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver Simulation Pro")
        self.root.geometry("1150x850") # Nới rộng một chút để vừa 6 nút bấm
        self.root.configure(bg="#f0f2f5")

        self.cached_start = [["" for _ in range(3)] for _ in range(3)]
        self.cached_goal = [["" for _ in range(3)] for _ in range(3)]
        self.max_steps = 2000

        self.start_state = None
        self.goal_state = None
        self.history = []
        self.current_index = 0
        self.final_path = []
        self.is_playing = False
        self.play_job = None

        self.main_menu()

    def clear_screen(self):
        self.stop_auto_play()
        for widget in self.root.winfo_children():
            widget.destroy()

    def main_menu(self):
        self.clear_screen()

        title_label = tk.Label(
            self.root, text="8-PUZZLE SOLVER SYSTEM",
            font=("Helvetica", 24, "bold"), bg="#f0f2f5", fg="#1a73e8"
        )
        title_label.pack(pady=20)

        input_frame = tk.Frame(self.root, bg="#f0f2f5")
        input_frame.pack(pady=10)

        start_fill_frame = tk.LabelFrame(input_frame, text=" Cấu hình trạng thái START ", font=("Helvetica", 10, "bold"), bg="#f0f2f5", fg="#3c4043", padx=15, pady=15)
        start_fill_frame.grid(row=0, column=0, padx=20)

        self.start_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                ent = tk.Entry(start_fill_frame, width=3, font=("Helvetica", 14, "bold"), justify="center", bd=2, relief="groove")
                ent.grid(row=i, column=j, padx=4, pady=4)
                ent.insert(0, str(self.cached_start[i][j]))
                row_entries.append(ent)
            self.start_entries.append(row_entries)

        goal_fill_frame = tk.LabelFrame(input_frame, text=" Cấu hình trạng thái GOAL ", font=("Helvetica", 10, "bold"), bg="#f0f2f5", fg="#155724", padx=15, pady=15)
        goal_fill_frame.grid(row=0, column=1, padx=20)

        self.goal_entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                ent = tk.Entry(goal_fill_frame, width=3, font=("Helvetica", 14, "bold"), justify="center", bd=2, relief="groove")
                ent.grid(row=i, column=j, padx=4, pady=4)
                ent.insert(0, str(self.cached_goal[i][j]))
                row_entries.append(ent)
            self.goal_entries.append(row_entries)

        note_lbl = tk.Label(self.root, text="*Lưu ý: Ô nhập không được để trống, phải chứa đầy đủ từ 0 đến 8 không trùng nhau (0 là ô trống).", font=("Helvetica", 9, "italic"), bg="#f0f2f5", fg="#5f6368")
        note_lbl.pack(pady=5)

        limit_frame = tk.Frame(self.root, bg="#f0f2f5")
        limit_frame.pack(pady=15)

        limit_lbl = tk.Label(limit_frame, text="Giới hạn số bước duyệt tối đa của thuật toán:", font=("Helvetica", 11, "bold"), bg="#f0f2f5", fg="#d93025")
        limit_lbl.pack(side="left", padx=10)

        self.limit_entry = tk.Entry(limit_frame, width=8, font=("Helvetica", 11, "bold"), justify="center")
        self.limit_entry.pack(side="left")
        self.limit_entry.insert(0, str(self.max_steps))

        subtitle_label = tk.Label(
            self.root, text="Chọn thuật toán để bắt đầu tìm kiếm:",
            font=("Helvetica", 12, "bold"), bg="#f0f2f5", fg="#3c4043"
        )
        subtitle_label.pack(pady=10)

        btn_frame = tk.Frame(self.root, bg="#f0f2f5")
        btn_frame.pack(pady=5)

        # Hàng 1: Các thuật toán tìm kiếm mù quáng (Uninformed)
        ttk.Button(btn_frame, text="BFS Algorithm", command=lambda: self.validate_and_start("BFS")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="DFS Algorithm", command=lambda: self.validate_and_start("DFS")).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="IDFS Algorithm", command=lambda: self.validate_and_start("IDFS")).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="UCS Algorithm", command=lambda: self.validate_and_start("UCS")).grid(row=0, column=3, padx=5, pady=5)

        # Hàng 2: Các thuật toán có tri thức (Informed / Heuristic)
        ttk.Button(btn_frame, text="Greedy Search", command=lambda: self.validate_and_start("Greedy")).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="A* Algorithm", command=lambda: self.validate_and_start("A*")).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="IDA* Algorithm", command=lambda: self.validate_and_start("IDA*")).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Hill Climbing", command=lambda: self.validate_and_start("HillClimbing")).grid(row=1, column=3, padx=5, pady=5)

    def validate_and_start(self, algo_type):
        try:
            limit_val = int(self.limit_entry.get().strip())
            if limit_val <= 0:
                raise ValueError()
            self.max_steps = limit_val
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Vui lòng nhập số nguyên dương hợp lệ cho ô 'Giới hạn số bước duyệt tối đa'!")
            return

        try:
            start_res = []
            goal_res = []
            for i in range(3):
                start_row = []
                goal_row = []
                for j in range(3):
                    st_val = self.start_entries[i][j].get().strip()
                    gl_val = self.goal_entries[i][j].get().strip()

                    if st_val == "" or gl_val == "":
                        raise ValueError("Không được để trống bất kỳ ô nào trong ma trận!")

                    self.cached_start[i][j] = st_val
                    self.cached_goal[i][j] = gl_val

                    start_row.append(int(st_val))
                    goal_row.append(int(gl_val))
                start_res.append(tuple(start_row))
                goal_res.append(tuple(goal_row))

            st_tuple = tuple(start_res)
            gl_tuple = tuple(goal_res)

            flatten_st = [num for r in st_tuple for num in r]
            flatten_gl = [num for r in gl_tuple for num in r]

            if sorted(flatten_st) != list(range(9)):
                raise ValueError("Ma trận START phải chứa đủ các số từ 0 đến 8 và không được trùng lặp!")
            if sorted(flatten_gl) != list(range(9)):
                raise ValueError("Ma trận GOAL phải chứa đủ các số từ 0 đến 8 và không được trùng lặp!")

            self.start_state = st_tuple
            self.goal_state = gl_tuple

        except ValueError as e:
            messagebox.showerror("Lỗi cấu hình ma trận", f"Phát hiện lỗi nhập liệu:\n⚠️ {e}")
            return

        # Định tuyến gọi thuật toán tương ứng
        if algo_type == "BFS":
            self.final_path, self.history = run_bfs(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "DFS":
            self.final_path, self.history = run_dfs(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "IDFS":
            self.final_path, self.history = run_idfs(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "UCS":
            self.final_path, self.history = run_ucs(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "A*":
            self.final_path, self.history = run_astar(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "Greedy":
            self.final_path, self.history = run_greedy(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "IDA*":
            self.final_path, self.history = run_idastar(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "HillClimbing":
            self.final_path, self.history = run_hill_climbing(self.start_state, self.goal_state, self.max_steps)

        self.current_index = 0
        self.game_screen(algo_type)

    def game_screen(self, algo_type):
        self.clear_screen()

        top_bar = tk.Frame(self.root, bg="#1a73e8", height=50)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        title_lbl = tk.Label(
            top_bar, text=f"Mô phỏng động: Thuật toán {algo_type}",
            font=("Helvetica", 13, "bold"), fg="white", bg="#1a73e8"
        )
        title_lbl.pack(side="left", padx=20)

        back_btn = ttk.Button(top_bar, text="◀ Quay lại thiết lập", command=self.main_menu)
        back_btn.pack(side="right", padx=20, pady=5)

        main_container = tk.Frame(self.root, bg="#f0f2f5")
        main_container.pack(fill="both", expand=True, padx=20, pady=15)

        left_frame = tk.Frame(main_container, bg="#f0f2f5")
        left_frame.pack(side="left", fill="both", expand=True, padx=10)

        matrices_frame = tk.Frame(left_frame, bg="#f0f2f5")
        matrices_frame.pack(anchor="w", pady=(0, 15))

        start_container = tk.Frame(matrices_frame, bg="#f0f2f5")
        start_container.grid(row=0, column=0, padx=(0, 25))
        tk.Label(start_container, text="Trạng thái START", font=("Helvetica", 10, "bold"), bg="#f0f2f5", fg="#3c4043").pack(anchor="w", pady=(0, 3))
        start_grid = tk.Frame(start_container, bg="#bdc3c7", bd=2)
        start_grid.pack()
        self.draw_static_matrix(start_grid, self.start_state, is_goal=False)

        goal_container = tk.Frame(matrices_frame, bg="#f0f2f5")
        goal_container.grid(row=0, column=1)
        tk.Label(goal_container, text="Trạng thái ĐÍCH (GOAL)", font=("Helvetica", 10, "bold"), bg="#f0f2f5", fg="#155724").pack(anchor="w", pady=(0, 3))
        goal_grid = tk.Frame(goal_container, bg="#bdc3c7", bd=2)
        goal_grid.pack()
        self.draw_static_matrix(goal_grid, self.goal_state, is_goal=True)

        path_lbl = tk.Label(left_frame, text="Kết quả đường đi tìm kiếm:", font=("Helvetica", 11, "bold"), bg="#f0f2f5", fg="#3c4043")
        path_lbl.pack(anchor="w", pady=(10, 3))

        self.path_text = tk.Text(left_frame, height=8, width=40, font=("Courier New", 11, "bold"), fg="#d93025", bg="white", relief="solid", bd=1)
        self.path_text.pack(anchor="w", fill="x", expand=True)

        if self.final_path is not None:
            formatted_path = " -> ".join(self.final_path)
            self.path_text.insert("1.0", f"Tìm thấy đích thành công!\nTổng số bước đi: {len(self.final_path)}\nTổng số Node đã duyệt: {len(self.history)}\n\nLộ trình di chuyển:\n{formatted_path}")
        else:
            if len(self.history) >= self.max_steps:
                self.path_text.insert("1.0", f"❌ THẤT BẠI: VƯỢT QUÁ GIỚI HẠN DUYỆT!\n\nThuật toán đã bị ngắt cưỡng bức do chạm mốc giới hạn tối đa ({self.max_steps} nodes) mà bạn đã thiết lập nhưng chưa tìm thấy đích.")
                messagebox.showwarning("Cảnh báo giới hạn", f"Thuật toán dừng lại vì chạm ngưỡng giới hạn {self.max_steps} bước duyệt để bảo vệ bộ nhớ!")
            else:
                self.path_text.insert("1.0", "❌ KHÔNG TÌM THẤY ĐƯỜNG ĐI!\n\nĐã quét sạch toàn bộ không gian cây trạng thái khả thi của bài toán này nhưng không tồn tại lời giải nào.")

        self.path_text.config(state="disabled")

        right_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        tk.Label(right_frame, text="Mô phỏng tiến trình duyệt cây trạng thái", font=("Helvetica", 11, "bold"), bg="#1a73e8", fg="white", pady=6).pack(fill="x")

        self.step_lbl = tk.Label(right_frame, text="", font=("Helvetica", 10, "italic"), bg="white", fg="#5f6368", pady=5)
        self.step_lbl.pack()

        self.live_grid_frame = tk.Frame(right_frame, bg="#bdc3c7", bd=2)
        self.live_grid_frame.pack(pady=5)

        tk.Label(right_frame, text="Chi tiết hành động tại Node này:", font=("Helvetica", 10, "bold"), bg="white", fg="#e65100").pack(anchor="w", padx=20, pady=(10, 2))

        self.explain_text_lbl = tk.Label(right_frame, text="", font=("Helvetica", 11), bg="#fff3e0", fg="#e65100", relief="solid", bd=1, wraplength=400, justify="center", pady=6)
        self.explain_text_lbl.pack(fill="x", padx=20, pady=(0, 10))

        control_frame = tk.Frame(right_frame, bg="white")
        control_frame.pack(side="bottom", pady=10)

        ttk.Button(control_frame, text="◀ Bước trước", command=self.prev_step).grid(row=0, column=0, padx=4, pady=4)
        self.play_btn = ttk.Button(control_frame, text="▶ Tự động chạy", command=self.toggle_auto_play)
        self.play_btn.grid(row=0, column=1, padx=4, pady=4)
        ttk.Button(control_frame, text="Bước sau ▶", command=self.next_step).grid(row=0, column=2, padx=4, pady=4)

        ttk.Button(control_frame, text="⏮ Về START", command=self.jump_to_start).grid(row=1, column=0, padx=4, pady=4)
        ttk.Button(control_frame, text="⏭ Đến cuối lịch sử", command=self.jump_to_goal).grid(row=1, column=2, padx=4, pady=4)

        self.update_live_matrix()

    def draw_static_matrix(self, frame, state, is_goal=False):
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                text = "" if val == 0 else str(val)
                bg_color = "#e8eaed" if val == 0 else ("#e6f4ea" if is_goal else "#ffffff")
                fg_color = "#137333" if (is_goal and val != 0) else "#3c4043"

                lbl = tk.Label(frame, text=text, font=("Helvetica", 12, "bold"), width=4, height=2, bg=bg_color, fg=fg_color, bd=1, relief="raised")
                lbl.grid(row=i, column=j, padx=1, pady=1)

    def update_live_matrix(self):
        if not self.history:
            return

        current_state, explanation = self.history[self.current_index]

        for widget in self.live_grid_frame.winfo_children():
            widget.destroy()

        self.step_lbl.config(text=f"Trạng thái đang xét (Node thứ: {self.current_index + 1}/{len(self.history)})")

        if current_state == self.goal_state:
            self.explain_text_lbl.config(text="🎉 THÀNH CÔNG! Thuật toán đã chạm được đến GOAL_STATE!", bg="#d4edda", fg="#155724")
        else:
            self.explain_text_lbl.config(text=explanation, bg="#fff3e0", fg="#e65100")

        for i in range(3):
            for j in range(3):
                val = current_state[i][j]
                text = "" if val == 0 else str(val)
                bg_color = "#e8eaed" if val == 0 else ("#d4edda" if current_state == self.goal_state else "#e8f0fe")
                fg_color = "#155724" if current_state == self.goal_state else "#1a73e8"

                lbl = tk.Label(self.live_grid_frame, text=text, font=("Helvetica", 18, "bold"), width=4, height=2, bg=bg_color, fg=fg_color, bd=1, relief="solid")
                lbl.grid(row=i, column=j, padx=2, pady=2)

    def next_step(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.update_live_matrix()
            return True
        else:
            self.stop_auto_play()
            messagebox.showinfo("Thông báo", "Đã mô phỏng xong toàn bộ tiến trình lịch sử!")
            return False

    def prev_step(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_live_matrix()

    def jump_to_start(self):
        self.stop_auto_play()
        self.current_index = 0
        self.update_live_matrix()

    def jump_to_goal(self):
        self.stop_auto_play()
        self.current_index = len(self.history) - 1
        self.update_live_matrix()

    def toggle_auto_play(self):
        if self.is_playing:
            self.stop_auto_play()
        else:
            self.is_playing = True
            self.play_btn.config(text="⏸ Dừng chạy")
            self.auto_play_loop()

    def auto_play_loop(self):
        if self.is_playing:
            has_next = self.next_step()
            if has_next:
                self.play_job = self.root.after(120, self.auto_play_loop)

    def stop_auto_play(self):
        self.is_playing = False
        if hasattr(self, "play_btn") and self.play_btn.winfo_exists():
            self.play_btn.config(text="▶ Tự động chạy")
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
