import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import heapq

# 1. CẤU HÌNH TRẠNG THÁI & HƯỚNG ĐI
START_STATE = ((2, 8, 3), (1, 6, 4), (7, 0, 5))
GOAL_STATE = ((1, 2, 3), (8, 0, 4), (7, 6, 5))

# Các hướng di chuyển của ô trống (Dùng chung cho BFS, DFS, IDFS)
MOVES = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}

# Thứ tự ưu tiên hành động khi chi phí g bằng nhau của UCS
UCS_ACTIONS = ['L', 'R', 'U', 'D']


def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j


def swap(state, x1, y1, x2, y2):
    state = [list(row) for row in state]
    state[x1][y1], state[x2][y2] = state[x2][y2], state[x1][y1]
    return tuple(tuple(row) for row in state)

# 2. THUẬT TOÁN
# 2.1 THUẬT TOÁN BFS
def run_bfs(start, goal):
    queue = deque()
    queue.append((start, [], "Trạng thái khởi đầu (START)."))
    visited = set()
    visited.add(start)
    states_history = []

    while queue:
        current, path, info = queue.popleft()
        states_history.append((current, info))

        if current == goal:
            return path, states_history

        x, y = find_zero(current)
        for move, (dx, dy) in MOVES.items():
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = swap(current, x, y, nx, ny)
                if new_state not in visited:
                    swapped_val = current[nx][ny]
                    move_name = {"U": "LÊN", "D": "XUỐNG", "L": "SANG TRÁI", "R": "SANG PHẢI"}[move]
                    desc = f"Hành động [{move}]: Di chuyển ô trống {move_name}, hoán đổi với số ({swapped_val})."
                    visited.add(new_state)
                    queue.append((new_state, path + [move], desc))
    return None, states_history


# 2.2 THUẬT TOÁN DFS
def run_dfs(start, goal):
    stack = []
    stack.append((start, [], "Trạng thái khởi đầu (START)."))
    visited = set()
    visited.add(start)
    states_history = []
    max_depth = 30

    while stack:
        current, path, info = stack.pop()
        states_history.append((current, info))

        if current == goal:
            return path, states_history

        if len(path) >= max_depth:
            continue

        x, y = find_zero(current)
        for move, (dx, dy) in list(MOVES.items()):
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = swap(current, x, y, nx, ny)
                if new_state not in visited:
                    swapped_val = current[nx][ny]
                    move_name = {"U": "LÊN", "D": "XUỐNG", "L": "SANG TRÁI", "R": "SANG PHẢI"}[move]
                    desc = f"Hành động [{move}]: Đẩy vào Stack hướng {move_name} (đổi với số {swapped_val})."
                    visited.add(new_state)
                    stack.append((new_state, path + [move], desc))
    return None, states_history


# 2.3 THUẬT TOÁN IDFS
def dls_for_gui(current, goal, limit, path, visited, states_history, last_info):
    states_history.append((current, last_info))

    if current == goal:
        return path
    if limit <= 0:
        return None

    visited.add(current)
    x, y = find_zero(current)

    for move, (dx, dy) in MOVES.items():
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            neighbor = swap(current, x, y, nx, ny)
            if neighbor not in visited:
                swapped_val = current[nx][ny]
                move_name = {"U": "LÊN", "D": "XUỐNG", "L": "SANG TRÁI", "R": "SANG PHẢI"}[move]
                desc = f"Tầng sâu giới hạn = {limit}. Đi tiếp hướng [{move}] {move_name} (đổi với số {swapped_val})."
                result = dls_for_gui(neighbor, goal, limit - 1, path + [move], visited, states_history, desc)
                if result is not None:
                    return result

    visited.remove(current)
    return None


def run_idfs(start, goal):
    depth = 0
    states_history = []
    while depth <= 50:
        visited = set()
        init_info = f"--- Bắt đầu dò tìm vòng lặp mới với Giới hạn độ sâu = {depth} ---"
        result = dls_for_gui(start, goal, depth, [], visited, states_history, init_info)
        if result is not None:
            return result, states_history
        depth += 1
    return None, states_history


# 2.4 THUẬT TOÁN UCS (CHI PHÍ DI CHUYỂN BẰNG GIÁ TRỊ Ô ĐƯỢC ĐỔI)
def run_ucs(start, goal):
    step_count = 0
    # Cấu trúc Frontier Heap Queue: (tổng_chi_phí_g, thứ_tự_vào, trạng_thái, đường_đi, thông_tin_giải_thích)
    frontier = []
    heapq.heappush(frontier, (0, step_count, start, [], "Trạng thái khởi đầu (START) với Chi phí g = 0."))

    explored = set()
    frontier_costs = {start: 0}
    states_history = []

    while frontier:
        g_cost, _, current, path, info = heapq.heappop(frontier)
        states_history.append((current, info))

        if current == goal:
            return path, states_history

        explored.add(current)

        r, c = find_zero(current)
        for action in UCS_ACTIONS:
            new_r, new_c = r, c
            if action == 'L': new_c -= 1
            elif action == 'R': new_c += 1
            elif action == 'U': new_r -= 1
            elif action == 'D': new_r += 1

            if 0 <= new_r < 3 and 0 <= new_c < 3:
                next_state = swap(current, r, c, new_r, new_c)
                action_cost = current[new_r][new_c]  # Chi phí bằng số trên ô bị đổi
                new_g = g_cost + action_cost

                if next_state in explored:
                    continue

                if next_state not in frontier_costs or new_g < frontier_costs[next_state]:
                    frontier_costs[next_state] = new_g

                    action_name = {"U": "LÊN", "D": "XUỐNG", "L": "SANG TRÁI", "R": "SANG PHẢI"}[action]
                    desc = (f"Lấy ra nút có g = {g_cost}. Di chuyển [{action}] {action_name} "
                            f"(đổi chỗ ô số {action_cost}, chi phí bước g tăng +{action_cost} -> tổng g = {new_g}).")

                    step_count += 1
                    heapq.heappush(frontier, (new_g, step_count, next_state, path + [action], desc))

    return None, states_history

# 3. GIAO DIỆN
class PuzzleApp:

    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver Simulation")
        self.root.geometry("1050x760")
        self.root.configure(bg="#f0f2f5")

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
            self.root, text="8-PUZZLE SOLVER",
            font=("Helvetica", 28, "bold"), bg="#f0f2f5", fg="#1a73e8"
        )
        title_label.pack(pady=50)

        subtitle_label = tk.Label(
            self.root, text="Chọn thuật toán để bắt đầu trò chơi:",
            font=("Helvetica", 14), bg="#f0f2f5", fg="#5f6368"
        )
        subtitle_label.pack(pady=10)

        btn_frame = tk.Frame(self.root, bg="#f0f2f5")
        btn_frame.pack(pady=30)

        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 11, "bold"), padding=8)

        bfs_btn = ttk.Button(btn_frame, text="BFS 8-puzzle", command=lambda: self.start_game("BFS"))
        bfs_btn.grid(row=0, column=0, padx=10, ipadx=5)

        dfs_btn = ttk.Button(btn_frame, text="DFS 8-puzzle", command=lambda: self.start_game("DFS"))
        dfs_btn.grid(row=0, column=1, padx=10, ipadx=5)

        idfs_btn = ttk.Button(btn_frame, text="IDFS 8-puzzle", command=lambda: self.start_game("IDFS"))
        idfs_btn.grid(row=0, column=2, padx=10, ipadx=5)

        ucs_btn = ttk.Button(btn_frame, text="UCS 8-puzzle", command=lambda: self.start_game("UCS"))
        ucs_btn.grid(row=0, column=3, padx=10, ipadx=5)

    def start_game(self, algo_type):
        if algo_type == "BFS":
            self.final_path, self.history = run_bfs(START_STATE, GOAL_STATE)
        elif algo_type == "DFS":
            self.final_path, self.history = run_dfs(START_STATE, GOAL_STATE)
        elif algo_type == "IDFS":
            self.final_path, self.history = run_idfs(START_STATE, GOAL_STATE)
        else:
            self.final_path, self.history = run_ucs(START_STATE, GOAL_STATE)

        self.current_index = 0
        self.game_screen(algo_type)

    def game_screen(self, algo_type):
        self.clear_screen()

        # Top Bar
        top_bar = tk.Frame(self.root, bg="#1a73e8", height=50)
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)

        title_lbl = tk.Label(
            top_bar, text=f"Trò chơi: {algo_type} 8-Puzzle",
            font=("Helvetica", 14, "bold"), fg="white", bg="#1a73e8"
        )
        title_lbl.pack(side="left", padx=20)

        back_btn = ttk.Button(top_bar, text="Quay lại", command=self.main_menu, style="TButton")
        back_btn.pack(side="right", padx=20, pady=5)

        main_container = tk.Frame(self.root, bg="#f0f2f5")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # ----------------------------------------
        # NỬA BÊN TRÁI
        # ----------------------------------------
        left_frame = tk.Frame(main_container, bg="#f0f2f5")
        left_frame.pack(side="left", fill="both", expand=True, padx=10)

        matrices_frame = tk.Frame(left_frame, bg="#f0f2f5")
        matrices_frame.pack(anchor="w", pady=(0, 25))

        # Khung START
        start_container = tk.Frame(matrices_frame, bg="#f0f2f5")
        start_container.grid(row=0, column=0, padx=(0, 30))

        start_lbl = tk.Label(
            start_container, text="Trạng thái START",
            font=("Helvetica", 11, "bold"), bg="#f0f2f5", fg="#3c4043"
        )
        start_lbl.pack(anchor="w", pady=(0, 5))

        start_grid = tk.Frame(start_container, bg="#bdc3c7", bd=2)
        start_grid.pack()
        self.draw_static_matrix(start_grid, START_STATE, is_goal=False)

        # Khung GOAL
        goal_container = tk.Frame(matrices_frame, bg="#f0f2f5")
        goal_container.grid(row=0, column=1)

        goal_lbl = tk.Label(
            goal_container, text="Trạng thái ĐÍCH (GOAL)",
            font=("Helvetica", 11, "bold"), bg="#f0f2f5", fg="#155724"
        )
        goal_lbl.pack(anchor="w", pady=(0, 5))

        goal_grid = tk.Frame(goal_container, bg="#bdc3c7", bd=2)
        goal_grid.pack()
        self.draw_static_matrix(goal_grid, GOAL_STATE, is_goal=True)

        # Khung lộ trình kết quả đường đi
        path_lbl = tk.Label(
            left_frame, text="Đường đi tìm được đến GOAL:",
            font=("Helvetica", 12, "bold"), bg="#f0f2f5", fg="#3c4043"
        )
        path_lbl.pack(anchor="w", pady=(10, 5))

        self.path_text = tk.Text(
            left_frame, height=7, width=42, font=("Courier New", 11, "bold"),
            fg="#d93025", bg="white", relief="solid", bd=1
        )
        self.path_text.pack(anchor="w", fill="x", expand=True)

        if self.final_path is not None:
            formatted_path = " -> ".join(self.final_path)
            self.path_text.insert(
                "1.0",
                f"Tổng số bước di chuyển: {len(self.final_path)}\n\nLộ trình hành động:\n{formatted_path}"
            )
        else:
            self.path_text.insert("1.0", "Không tìm thấy đường đi tới đích!")
        self.path_text.config(state="disabled")

        # ----------------------------------------
        # NỬA BÊN PHẢI (Mô phỏng động + Thuyết minh)
        # ----------------------------------------
        right_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        right_title = tk.Label(
            right_frame, text="Mô phỏng tiến trình duyệt trạng thái",
            font=("Helvetica", 12, "bold"), bg="#1a73e8", fg="white", pady=8
        )
        right_title.pack(fill="x")

        self.step_lbl = tk.Label(
            right_frame, text="", font=("Helvetica", 11, "italic"),
            bg="white", fg="#5f6368", pady=8
        )
        self.step_lbl.pack()

        self.live_grid_frame = tk.Frame(right_frame, bg="#bdc3c7", bd=2)
        self.live_grid_frame.pack(pady=5)

        # Khung giải thích chi tiết động
        explain_lbl = tk.Label(
            right_frame, text="Chi tiết hành động di chuyển:",
            font=("Helvetica", 10, "bold"), bg="white", fg="#e65100"
        )
        explain_lbl.pack(anchor="w", padx=20, pady=(10, 2))

        self.explain_text_lbl = tk.Label(
            right_frame, text="", font=("Helvetica", 11),
            bg="#fff3e0", fg="#e65100", relief="solid", bd=1,
            wraplength=420, justify="center", pady=8
        )
        self.explain_text_lbl.pack(fill="x", padx=20, pady=(0, 10))

        # Cụm nút điều khiển tích hợp ở dưới cùng
        control_frame = tk.Frame(right_frame, bg="white")
        control_frame.pack(side="bottom", pady=15)

        prev_btn = ttk.Button(control_frame, text="◀ Bước trước", command=self.prev_step)
        prev_btn.grid(row=0, column=0, padx=5, pady=5)

        self.play_btn = ttk.Button(control_frame, text="▶ Tự động chạy", command=self.toggle_auto_play)
        self.play_btn.grid(row=0, column=1, padx=5, pady=5)

        next_btn = ttk.Button(control_frame, text="Bước sau ▶", command=self.next_step)
        next_btn.grid(row=0, column=2, padx=5, pady=5)

        jump_start_btn = ttk.Button(control_frame, text="⏮ Về START", command=self.jump_to_start)
        jump_start_btn.grid(row=1, column=0, padx=5, pady=5)

        jump_goal_btn = ttk.Button(control_frame, text="⏭ Đến thẳng GOAL", command=self.jump_to_goal)
        jump_goal_btn.grid(row=1, column=2, padx=5, pady=5)

        self.update_live_matrix()

    def draw_static_matrix(self, frame, state, is_goal=False):
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                text = "" if val == 0 else str(val)
                bg_color = "#e8eaed" if val == 0 else ("#e6f4ea" if is_goal else "#ffffff")
                fg_color = "#137333" if (is_goal and val != 0) else "#3c4043"

                lbl = tk.Label(
                    frame, text=text, font=("Helvetica", 13, "bold"),
                    width=4, height=2, bg=bg_color, fg=fg_color, bd=1, relief="raised"
                )
                lbl.grid(row=i, column=j, padx=1, pady=1)

    def update_live_matrix(self):
        if not self.history:
            return

        current_state, explanation = self.history[self.current_index]

        # Xóa khung ma trận cũ
        for widget in self.live_grid_frame.winfo_children():
            widget.destroy()

        self.step_lbl.config(
            text=f"Trạng thái hiện tại (Node thứ: {self.current_index + 1}/{len(self.history)})"
        )

        # Thiết lập màu sắc thuyết minh tương ứng
        if current_state == GOAL_STATE:
            self.explain_text_lbl.config(
                text="🎉 CHÚC MỪNG! Thuật toán đã chạm đích thành công (GOAL_STATE)!",
                bg="#d4edda", fg="#155724"
            )
        else:
            self.explain_text_lbl.config(text=explanation, bg="#fff3e0", fg="#e65100")

        # Vẽ lại lưới ô vuông số
        for i in range(3):
            for j in range(3):
                val = current_state[i][j]
                text = "" if val == 0 else str(val)

                if val == 0:
                    bg_color = "#e8eaed"
                elif current_state == GOAL_STATE:
                    bg_color = "#d4edda"
                else:
                    bg_color = "#e8f0fe"

                fg_color = "#155724" if current_state == GOAL_STATE else "#1a73e8"

                lbl = tk.Label(
                    self.live_grid_frame, text=text, font=("Helvetica", 20, "bold"),
                    width=4, height=2, bg=bg_color, fg=fg_color, bd=1, relief="solid"
                )
                lbl.grid(row=i, column=j, padx=3, pady=3)

    # --- ĐIỀU KHIỂN MÔ PHỎNG ---
    def next_step(self):
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.update_live_matrix()
            return True
        else:
            self.stop_auto_play()
            messagebox.showinfo("Thông báo", "Đã duyệt đến trạng thái cuối cùng!")
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

    # --- HỆ THỐNG RUN TỰ ĐỘNG CHẠY ---
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
                self.play_job = self.root.after(150, self.auto_play_loop)

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
