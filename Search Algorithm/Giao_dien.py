import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import heapq
import random
import math

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

# Hàm kiểm tra tính khả giải của ma trận 8-puzzle
def is_solvable(start, goal):
    def count_inversions(state):
        flat = [num for row in state for num in row if num != 0]
        inversions = 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                if flat[i] > flat[j]:
                    inversions += 1
        return inversions
    return (count_inversions(start) % 2) == (count_inversions(goal) % 2)

# ==============================================================================
# 2. KHU VỰC THUẬT TOÁN
# ==============================================================================

def run_bfs(start, goal, max_steps):
    queue = deque()
    queue.append((start, [], "Trạng thái khởi đầu (START)."))
    visited = {start}
    states_history = []
    while queue:
        if len(states_history) >= max_steps: return None, states_history
        current, path, info = queue.popleft()
        states_history.append((current, info))
        if current == goal: return path, states_history
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

def run_dfs(start, goal, max_steps):
    stack = [(start, [], "Trạng thái khởi đầu (START).")]
    visited = set()
    states_history = []
    while stack:
        if len(states_history) >= max_steps: return None, states_history
        current, path, info = stack.pop()
        if current in visited: continue
        visited.add(current)
        states_history.append((current, info))
        if current == goal: return path, states_history
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

def dls_for_gui(current, goal, limit, path, visited, states_history, last_info, max_steps):
    if len(states_history) >= max_steps: return "LIMIT_EXCEEDED"
    states_history.append((current, last_info))
    if current == goal: return path
    if limit <= 0: return None
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
                if result is not None: return result
    return None

def run_idfs(start, goal, max_steps):
    depth = 0
    states_history = []
    while True:
        visited = set()
        init_info = f"--- Bắt đầu dò tìm vòng lặp mới với Giới hạn độ sâu = {depth} ---"
        result = dls_for_gui(start, goal, depth, [], visited, states_history, init_info, max_steps)
        if result == "LIMIT_EXCEEDED": return None, states_history
        if result is not None: return result, states_history
        depth += 1

def run_ucs(start, goal, max_steps):
    step_count = 0
    frontier = [(0, step_count, start, [], "Trạng thái khởi đầu (START) với Chi phí g = 0.")]
    explored = set()
    frontier_costs = {start: 0}
    states_history = []
    while frontier:
        if len(states_history) >= max_steps: return None, states_history
        g_cost, _, current, path, info = heapq.heappop(frontier)
        if current in explored: continue
        states_history.append((current, info))
        if current == goal: return path, states_history
        explored.add(current)
        r, c = find_zero(current)
        for move, (dx, dy), move_name in ACTIONS:
            new_r, new_c = r + dx, c + dy
            if 0 <= new_r < 3 and 0 <= new_c < 3:
                next_state = swap(current, r, c, new_r, new_c)
                new_g = g_cost + 1
                if next_state in explored: continue
                if next_state not in frontier_costs or new_g < frontier_costs[next_state]:
                    frontier_costs[next_state] = new_g
                    desc = f"Lấy ra nút có g = {g_cost}. Di chuyển [{move}] {move_name} (tổng g = {new_g})."
                    step_count += 1
                    heapq.heappush(frontier, (new_g, step_count, next_state, path + [move], desc))
    return None, states_history

def run_astar(start, goal, max_steps):
    step_count = 0
    frontier = []
    h_start = manhattan_distance(start, goal)
    heapq.heappush(frontier, (h_start, step_count, 0, start, [], f"Khởi tạo START. g=0, h={h_start} -> f={h_start}"))
    explored = set()
    frontier_costs = {start: 0}
    states_history = []
    while frontier:
        if len(states_history) >= max_steps: return None, states_history
        f_cost, _, g_cost, current, path, info = heapq.heappop(frontier)
        if current in explored: continue
        states_history.append((current, info))
        if current == goal: return path, states_history
        explored.add(current)
        r, c = find_zero(current)
        for move, (dx, dy), move_name in ACTIONS:
            new_r, new_c = r + dx, c + dy
            if 0 <= new_r < 3 and 0 <= new_c < 3:
                next_state = swap(current, r, c, new_r, new_c)
                new_g = g_cost + 1
                if next_state in explored: continue
                if next_state not in frontier_costs or new_g < frontier_costs[next_state]:
                    frontier_costs[next_state] = new_g
                    new_h = manhattan_distance(next_state, goal)
                    new_f = new_g + new_h
                    desc = f"Xét nút có g={g_cost}. Di chuyển [{move}] {move_name}. Cập nhật: g={new_g}, h={new_h} -> f={new_f}"
                    step_count += 1
                    heapq.heappush(frontier, (new_f, step_count, new_g, next_state, path + [move], desc))
    return None, states_history

def run_greedy(start, goal, max_steps):
    step_count = 0
    frontier = []
    h_start = manhattan_distance(start, goal)
    heapq.heappush(frontier, (h_start, step_count, start, [], f"Khởi tạo START. Đánh giá Heuristic h={h_start}"))
    explored = set()
    states_history = []
    while frontier:
        if len(states_history) >= max_steps: return None, states_history
        h_cost, _, current, path, info = heapq.heappop(frontier)
        if current in explored: continue
        states_history.append((current, info))
        if current == goal: return path, states_history
        explored.add(current)
        r, c = find_zero(current)
        for move, (dx, dy), move_name in ACTIONS:
            new_r, new_c = r + dx, c + dy
            if 0 <= new_r < 3 and 0 <= new_c < 3:
                next_state = swap(current, r, c, new_r, new_c)
                if next_state not in explored:
                    new_h = manhattan_distance(next_state, goal)
                    desc = f"Tham lam lấy nút có h={h_cost}. Di chuyển hướng [{move}] {move_name}. Ước lượng h mới={new_h}"
                    step_count += 1
                    heapq.heappush(frontier, (new_h, step_count, next_state, path + [move], desc))
    return None, states_history

def idfs_astar_for_gui(current, goal, g_cost, f_limit, path, visited, states_history, last_info, max_steps):
    if len(states_history) >= max_steps: return "LIMIT_EXCEEDED", max_steps
    h_cost = manhattan_distance(current, goal)
    f_cost = g_cost + h_cost
    states_history.append((current, last_info))
    if current == goal: return path, f_cost
    if f_cost > f_limit: return None, f_cost
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
                if result == "LIMIT_EXCEEDED": return "LIMIT_EXCEEDED", max_steps
                if result is not None: return result, next_f
                if next_f < min_cutoff: min_cutoff = next_f
    visited.remove(current)
    return None, min_cutoff

def run_idastar(start, goal, max_steps):
    states_history = []
    f_limit = manhattan_distance(start, goal)
    while True:
        visited = set()
        init_info = f"--- Khởi động vòng lặp IDA* mới với f_limit = {f_limit} ---"
        result, next_f = idfs_astar_for_gui(start, goal, 0, f_limit, [], visited, states_history, init_info, max_steps)
        if result == "LIMIT_EXCEEDED": return None, states_history
        if result is not None: return result, states_history
        if next_f == float('inf') or next_f == f_limit: return None, states_history
        f_limit = next_f

def run_hill_climbing(start, goal, max_steps):
    current = start
    path = []
    states_history = []
    curr_h = manhattan_distance(current, goal)
    states_history.append((current, f"Bắt đầu tại START. Heuristic hiện tại h = {curr_h}"))
    while current != goal:
        if len(states_history) >= max_steps: return None, states_history
        x, y = find_zero(current)
        neighbor_moved = False
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)
                if neighbor_h < curr_h:
                    current = neighbor
                    curr_h = neighbor_h
                    path.append(move)
                    states_history.append((current, f"Hành động [{move}]: Leo đồi thành công sang {move_name}. h mới = {curr_h}"))
                    neighbor_moved = True
                    break
        if not neighbor_moved:
            states_history.append((current, f"KẸT CỤC BỘ (Local Optimum)! h = {curr_h}. Thuật toán dừng lại."))
            return None, states_history
    return path, states_history

def run_steepest_hill_climbing(start, goal, max_steps):
    current = start
    path = []
    states_history = []
    curr_h = manhattan_distance(current, goal)
    states_history.append((current, f"Bắt đầu tại START. Heuristic hiện tại h = {curr_h}"))
    while current != goal:
        if len(states_history) >= max_steps: return None, states_history
        x, y = find_zero(current)
        best_neighbor = None
        best_h = curr_h
        best_move, best_move_name = None, None
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)
                if neighbor_h < best_h:
                    best_h = neighbor_h
                    best_neighbor = neighbor
                    best_move = move
                    best_move_name = move_name
        if best_neighbor is not None:
            current = best_neighbor
            curr_h = best_h
            path.append(best_move)
            states_history.append((current, f"Hành động [{best_move}]: Chọn hướng TỐT NHẤT {best_move_name}. h mới = {curr_h}."))
        else:
            states_history.append((current, f"KẸT CỤC BỘ (Local Optimum)! Không hướng nào tốt hơn h = {curr_h}."))
            return None, states_history
    return path, states_history

def run_stochastic_hill_climbing(start, goal, max_steps):
    current = start
    path = []
    states_history = []
    curr_h = manhattan_distance(current, goal)
    states_history.append((current, f"Bắt đầu tại START. Heuristic hiện tại h = {curr_h}"))
    while current != goal:
        if len(states_history) >= max_steps: return None, states_history
        x, y = find_zero(current)
        better_neighbors = []
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)
                if neighbor_h < curr_h:
                    better_neighbors.append((neighbor, neighbor_h, move, move_name))
        if better_neighbors:
            current, curr_h, move, move_name = random.choice(better_neighbors)
            path.append(move)
            states_history.append((current, f"Hành động [{move}]: Lựa chọn NGẪU NHIÊN hướng tốt {move_name}. h mới = {curr_h}."))
        else:
            states_history.append((current, f"KẸT CỤC BỘ! Không có hướng ngẫu nhiên nào cải thiện được h = {curr_h}."))
            return None, states_history
    return path, states_history

def run_hill_climbing_random_walk(start, goal, max_steps, walk_steps=6):
    current = start
    path = []
    states_history = []
    curr_h = manhattan_distance(current, goal)
    states_history.append((current, f"Bắt đầu tại START. Heuristic hiện tại h = {curr_h}"))
    while current != goal:
        if len(states_history) >= max_steps: return None, states_history
        x, y = find_zero(current)
        neighbor_moved = False
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)
                if neighbor_h < curr_h:
                    current = neighbor
                    curr_h = neighbor_h
                    path.append(move)
                    states_history.append((current, f"Hành động [{move}]: Leo đồi sang {move_name}. h mới = {curr_h}."))
                    neighbor_moved = True
                    break
        if not neighbor_moved:
            states_history.append((current, f"⚠️ KẸT CỤC BỘ tại h = {curr_h}! Thực hiện Random Walk {walk_steps} bước để phá kẹt..."))
            for _ in range(walk_steps):
                if current == goal: break
                x, y = find_zero(current)
                valid_moves = []
                for move, (dx, dy), move_name in ACTIONS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 3 and 0 <= ny < 3: valid_moves.append((move, dx, dy, move_name))
                if valid_moves:
                    move, dx, dy, move_name = random.choice(valid_moves)
                    current = swap(current, x, y, x + dx, y + dy)
                    curr_h = manhattan_distance(current, goal)
                    path.append(move)
                    states_history.append((current, f"🎲 [Random Walk]: Đi ngẫu nhiên hướng [{move}] {move_name} -> h = {curr_h}"))
    return path, states_history

def run_local_beam_search(start, goal, max_steps, k=3):
    curr_h = manhattan_distance(start, goal)
    beam = [(curr_h, start, [])]
    states_history = [(start, f"Khởi tạo chùm (Beam Search) với độ rộng k = {k}. Gốc có h = {curr_h}")]
    step_count = 0
    while step_count < max_steps:
        for _, state, path in beam:
            if state == goal:
                states_history.append((state, "Thành công! Một nhánh trong chùm tìm kiếm đã chạm tới ĐÍCH."))
                return path, states_history
        successors = []
        for _, state, path in beam:
            x, y = find_zero(state)
            for move, (dx, dy), move_name in ACTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx < 3 and 0 <= ny < 3:
                    neighbor = swap(state, x, y, nx, ny)
                    neighbor_h = manhattan_distance(neighbor, goal)
                    successors.append((neighbor_h, neighbor, path + [move]))
        if not successors:
            states_history.append((beam[0][1], "Chùm tìm kiếm bị cụt đường. Thuật toán dừng lại."))
            return None, states_history
        successors.sort(key=lambda x: x[0])
        beam = successors[:k]
        step_count += 1
        best_h, best_state, _ = beam[0]
        states_history.append((best_state, f"Vòng duyệt {step_count}: Sàng lọc chùm mới. Trạng thái tốt nhất có h = {best_h}."))
    return None, states_history

def run_simulated_annealing(start, goal, max_steps):
    current = start
    path = []
    curr_h = manhattan_distance(current, goal)
    states_history = [(current, f"Bắt đầu Luyện Kim tại START. h = {curr_h}, Nhiệt độ ban đầu T = 100.0")]
    T, alpha = 100.0, 0.95
    while current != goal:
        if len(states_history) >= max_steps: return None, states_history
        if T < 0.001:
            states_history.append((current, f"Lò nguội hoàn toàn (T đạt giới hạn dưới). Thuật toán dừng lại tại h = {curr_h}."))
            return None, states_history
        x, y = find_zero(current)
        valid_neighbors = []
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)
                valid_neighbors.append((neighbor, neighbor_h, move, move_name))
        if not valid_neighbors: return None, states_history
        next_state, next_h, move, move_name = random.choice(valid_neighbors)
        delta_e = curr_h - next_h
        if delta_e > 0:
            current = next_state
            curr_h = next_h
            path.append(move)
            states_history.append((current, f"✅ Hướng tốt: Di chuyển [{move}] {move_name}. h mới = {curr_h}. T = {T:.3f}"))
        else:
            prob = math.exp(delta_e / T)
            rand_val = random.random()
            if rand_val < prob:
                current = next_state
                curr_h = next_h
                path.append(move)
                states_history.append((current, f"🎲 Chấp nhận hướng tệ nhờ nhiệt độ! [{move}] {move_name}. h mới = {curr_h}. T = {T:.3f}"))
            else:
                states_history.append((current, f"❌ Từ chối hướng tệ [{move}] {move_name} (h={next_h}). Giữ nguyên. T = {T:.3f}"))
        T *= alpha
    return path, states_history

def run_bidirectional_search(start, goal, max_steps):
    queue_f, queue_b = deque([(start, [])]), deque([(goal, [])])
    visited_f, visited_b = {start: []}, {goal: []}
    states_history = [(start, "🧭 Khởi tạo Tìm kiếm Hai hướng: Nhánh Xuôi (Start) và Nhánh Ngược (Goal) quét song song.")]
    reverse_move = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}
    while queue_f and queue_b:
        if len(states_history) >= max_steps: return None, states_history
        curr_f, path_f = queue_f.popleft()
        states_history.append((curr_f, f"➡️ [Nhánh Xuôi] Đang xét một Node. Tập duyệt xuôi: {len(visited_f)}"))
        if curr_f in visited_b:
            return path_f + visited_b[curr_f], states_history + [(curr_f, "🎉 HAI MA TRẬN ĐÃ GẶP NHAU TẠI ĐÂY! Hoàn thành kết nối.")]
        x, y = find_zero(curr_f)
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                next_f = swap(curr_f, x, y, nx, ny)
                if next_f not in visited_f:
                    visited_f[next_f] = path_f + [move]
                    queue_f.append((next_f, path_f + [move]))

        curr_b, path_b = queue_b.popleft()
        states_history.append((curr_b, f"⬅️ [Nhánh Ngược] Đang xét một Node. Tập duyệt ngược: {len(visited_b)}"))
        if curr_b in visited_f:
            return visited_f[curr_b] + path_b, states_history + [(curr_b, "🎉 HAI MA TRẬN ĐÃ GẶP NHAU TẠI ĐÂY! Hoàn thành kết nối.")]
        x, y = find_zero(curr_b)
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                next_b = swap(curr_b, x, y, nx, ny)
                if next_b not in visited_b:
                    new_path_b = [reverse_move[move]] + path_b
                    visited_b[next_b] = new_path_b
                    queue_b.append((next_b, new_path_b))
    return None, states_history

# THUẬT TOÁN MÙ TOÀN DIỆN
def run_blind_blind_search(max_steps):
    states_pool = list(range(9))
    while True:
        random.shuffle(states_pool)
        s1 = tuple(tuple(states_pool[i:i+3]) for i in range(0, 9, 3))
        random.shuffle(states_pool)
        s2 = tuple(tuple(states_pool[i:i+3]) for i in range(0, 9, 3))
        # Ép buộc s1 và s2 phải khác nhau VÀ phải có lời giải (Solvable)
        if s1 != s2 and is_solvable(s1, s2):
            break

    queue1, queue2 = deque([(s1, [])]), deque([(s2, [])])
    visited1, visited2 = {s1: []}, {s2: []}
    states_history = [(s1, f"🎲 Không gian mù. Tự động sinh Ma trận START ngẫu nhiên có lời giải.")]
    states_history.append((s2, f"🎲 Tự động sinh Ma trận GOAL ngẫu nhiên tương thích."))
    rev_m = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}

    while queue1 and queue2:
        if len(states_history) >= max_steps: return None, states_history
        c1, p1 = queue1.popleft()
        states_history.append((c1, f"➡️ Nhánh Xuôi mở rộng node. Tập đã duyệt: {len(visited1)} trạng thái."))
        if c1 in visited2:
            return p1 + visited2[c1], states_history + [(c1, "🎉 Hai nhánh ngẫu nhiên chạm mặt trùng khớp trạng thái! Hoàn thành.")]
        x, y = find_zero(c1)
        for move, (dx, dy), _ in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                nxt = swap(c1, x, y, nx, ny)
                if nxt not in visited1:
                    visited1[nxt] = p1 + [move]
                    queue1.append((nxt, p1 + [move]))

        c2, p2 = queue2.popleft()
        states_history.append((c2, f"⬅️ Nhánh Ngược mở rộng node. Tập đã duyệt: {len(visited2)} trạng thái."))
        if c2 in visited1:
            return visited1[c2] + p2, states_history + [(c2, "🎉 Hai nhánh ngẫu nhiên chạm mặt trùng khớp trạng thái! Hoàn thành.")]
        x, y = find_zero(c2)
        for move, (dx, dy), _ in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                nxt = swap(c2, x, y, nx, ny)
                if nxt not in visited2:
                    visited2[nxt] = [rev_m[move]] + p2
                    queue2.append((nxt, [rev_m[move]] + p2))
    return None, states_history

def run_partial_state_search(partial_start, goal, max_steps):
    flatten_partial = [num for r in partial_start for num in r]
    fixed_nums = [n for n in flatten_partial if n != -1]
    missing_nums = [n for n in range(9) if n not in fixed_nums]
    possible_starts = []

    def generate_permutations(idx, current_flat):
        if idx == 9:
            possible_starts.append(tuple(tuple(current_flat[i:i+3]) for i in range(0, 9, 3)))
            return
        if flatten_partial[idx] != -1:
            generate_permutations(idx + 1, current_flat + [flatten_partial[idx]])
        else:
            for num in missing_nums:
                if num not in current_flat:
                    generate_permutations(idx + 1, current_flat + [num])

    generate_permutations(0, [])
    states_history = [(goal, f"🔍 Phân tích ma trận mờ: Tìm thấy {len(possible_starts)} cấu hình xuất phát khả thi.")]

    queue = deque()
    visited = set()
    for st in possible_starts:
        queue.append((st, [], f"Khởi động song song xuất phát tại cấu hình mờ hợp lệ."))
        visited.add(st)

    while queue:
        if len(states_history) >= max_steps: return None, states_history
        current, path, info = queue.popleft()
        states_history.append((current, info))
        if current == goal: return path, states_history
        x, y = find_zero(current)
        for move, (dx, dy), mn in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                nxt = swap(current, x, y, nx, ny)
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [move], f"Quét không gian từ nguồn mờ. Đi hướng [{move}] {mn}."))
    return None, states_history

def run_and_or_graph_search(start, goal, max_steps):
    states_history = []
    memo_plan = {}

    def and_or_search(state, path_accumulated, visited_branch):
        if len(states_history) >= max_steps: return "FAILED"
        states_history.append((state, f"Đang xét nút OR (Ta lựa chọn hành động di chuyển)."))
        if state == goal: return []
        if state in visited_branch: return "FAILED"
        if state in memo_plan: return memo_plan[state]

        visited_branch.add(state)
        x, y = find_zero(state)
        for move, (dx, dy), mn in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                intended_state = swap(state, x, y, nx, ny)
                environment_states = [intended_state]
                for m_side, (dx_s, dy_s), _ in ACTIONS:
                    nx_s, ny_s = x + dx_s, y + dy_s
                    if 0 <= nx_s < 3 and 0 <= ny_s < 3:
                        side_state = swap(state, x, y, nx_s, ny_s)
                        if side_state != intended_state and random.random() < 0.25:
                            environment_states.append(side_state)

                action_valid_for_all_and = True
                sub_plans = {}
                for and_state in environment_states:
                    states_history.append((and_state, f"↳ Xét nút AND (Biến động môi trường xảy ra)."))
                    res = and_or_search(and_state, path_accumulated + [move], visited_branch.copy())
                    if res == "FAILED":
                        action_valid_for_all_and = False
                        break
                    sub_plans[and_state] = res

                if action_valid_for_all_and:
                    plan = [move] + (sub_plans[intended_state] if intended_state in sub_plans else [])
                    memo_plan[state] = plan
                    return plan
        return "FAILED"

    plan_result = and_or_search(start, [], set())
    if plan_result == "FAILED" or plan_result is None: return None, states_history
    return plan_result, states_history

# ==============================================================================
# 3. GIAO DIỆN ỨNG DỤNG
# ==============================================================================
class PuzzleApp:

    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver Simulation Pro")
        self.root.geometry("1150x920")
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

        note_lbl = tk.Label(self.root, text="*Lưu ý: Với thuật toán Nhìn một phần có thể để trống hoặc điền X/? ô bị ẩn. Mù toàn diện tự động sinh ngẫu nhiên.", font=("Helvetica", 9, "italic"), bg="#f0f2f5", fg="#5f6368")
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

        ttk.Button(btn_frame, text="BFS Algorithm", command=lambda: self.validate_and_start("BFS")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="DFS Algorithm", command=lambda: self.validate_and_start("DFS")).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="IDFS Algorithm", command=lambda: self.validate_and_start("IDFS")).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="UCS Algorithm", command=lambda: self.validate_and_start("UCS")).grid(row=0, column=3, padx=5, pady=5)

        ttk.Button(btn_frame, text="Greedy Search", command=lambda: self.validate_and_start("Greedy")).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="A* Algorithm", command=lambda: self.validate_and_start("A*")).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="IDA* Algorithm", command=lambda: self.validate_and_start("IDA*")).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Hill Climbing", command=lambda: self.validate_and_start("HillClimbing")).grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(btn_frame, text="Steepest Hill Climbing", command=lambda: self.validate_and_start("SteepestHC")).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Stochastic Hill Climbing", command=lambda: self.validate_and_start("StochasticHC")).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="Random Walk HC", command=lambda: self.validate_and_start("RandomWalkHC")).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Local Beam Search", command=lambda: self.validate_and_start("LocalBeam")).grid(row=2, column=3, padx=5, pady=5)

        ttk.Button(btn_frame, text="🔥 Simulated Annealing", command=lambda: self.validate_and_start("SA")).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")
        ttk.Button(btn_frame, text="🧭 Bidirectional Search", command=lambda: self.validate_and_start("Bidirectional")).grid(row=3, column=2, columnspan=2, padx=5, pady=5, sticky="we")

        ttk.Button(btn_frame, text="✨ 1. Mù Toàn Diện (No-View)", command=lambda: self.validate_and_start("BlindBlind")).grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="we")
        ttk.Button(btn_frame, text="🔍 2. Nhìn Một Phần (Partial)", command=lambda: self.validate_and_start("PartialState")).grid(row=4, column=2, columnspan=2, padx=5, pady=5, sticky="we")

        ttk.Button(btn_frame, text="🌿 3. Đồ thị AND-OR Search", command=lambda: self.validate_and_start("AndOrGraph")).grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky="we")

    def validate_and_start(self, algo_type):
        try:
            limit_val = int(self.limit_entry.get().strip())
            if limit_val <= 0: raise ValueError()
            self.max_steps = limit_val
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Vui lòng nhập số nguyên dương hợp lệ cho ô 'Giới hạn số bước duyệt tối đa'!")
            return

        if algo_type == "BlindBlind":
            self.start_state = ((0,0,0),(0,0,0),(0,0,0))
            self.goal_state = ((0,0,0),(0,0,0),(0,0,0))
        else:
            try:
                start_res = []
                goal_res = []
                for i in range(3):
                    start_row = []
                    goal_row = []
                    for j in range(3):
                        st_val = self.start_entries[i][j].get().strip()
                        gl_val = self.goal_entries[i][j].get().strip()

                        self.cached_start[i][j] = st_val
                        self.cached_goal[i][j] = gl_val

                        if algo_type == "PartialState":
                            if st_val in ["", "?", "X", "x", "-", "*"]:
                                start_row.append(-1)
                            else:
                                start_row.append(int(st_val))
                        else:
                            if st_val == "": raise ValueError("Không được để trống bất kỳ ô nào trong ma trận START!")
                            start_row.append(int(st_val))

                        if gl_val == "": raise ValueError("Không được để trống bất kỳ ô nào trong ma trận GOAL!")
                        goal_row.append(int(gl_val))

                    start_res.append(tuple(start_row))
                    goal_res.append(tuple(goal_row))

                st_tuple = tuple(start_res)
                gl_tuple = tuple(goal_res)

                if sorted([num for r in gl_tuple for num in r]) != list(range(9)):
                    raise ValueError("Ma trận GOAL phải chứa đủ các số từ 0 đến 8 và không được trùng lặp!")

                if algo_type != "PartialState":
                    if sorted([num for r in st_tuple for num in r]) != list(range(9)):
                        raise ValueError("Ma trận START phải chứa đủ các số từ 0 đến 8 và không được trùng lặp!")
                else:
                    flatten_st = [num for r in st_tuple for num in r if num != -1]
                    if len(flatten_st) != len(set(flatten_st)):
                        raise ValueError("Các ô nhìn thấy được trong ma trận START không được trùng lặp số nhau!")
                    if any(num < 0 or num > 8 for num in flatten_st):
                        raise ValueError("Các ô trong ma trận START chỉ được điền số từ 0 đến 8!")

                self.start_state = st_tuple
                self.goal_state = gl_tuple

            except ValueError as e:
                messagebox.showerror("Lỗi cấu hình ma trận", f"Phát hiện lỗi nhập liệu:\n⚠️ {e}")
                return

        if algo_type == "BFS": self.final_path, self.history = run_bfs(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "DFS": self.final_path, self.history = run_dfs(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "IDFS": self.final_path, self.history = run_idfs(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "UCS": self.final_path, self.history = run_ucs(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "A*": self.final_path, self.history = run_astar(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "Greedy": self.final_path, self.history = run_greedy(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "IDA*": self.final_path, self.history = run_idastar(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "HillClimbing": self.final_path, self.history = run_hill_climbing(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "SteepestHC": self.final_path, self.history = run_steepest_hill_climbing(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "StochasticHC": self.final_path, self.history = run_stochastic_hill_climbing(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "RandomWalkHC": self.final_path, self.history = run_hill_climbing_random_walk(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "LocalBeam": self.final_path, self.history = run_local_beam_search(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "SA": self.final_path, self.history = run_simulated_annealing(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "Bidirectional": self.final_path, self.history = run_bidirectional_search(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "AndOrGraph": self.final_path, self.history = run_and_or_graph_search(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "BlindBlind":
            self.final_path, self.history = run_blind_blind_search(self.max_steps)
            if self.history:
                self.start_state = self.history[0][0]
                self.goal_state = self.history[-1][0]
        elif algo_type == "PartialState":
            self.final_path, self.history = run_partial_state_search(self.start_state, self.goal_state, self.max_steps)
            if self.history and len(self.history) > 1: self.start_state = self.history[1][0]

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

        # Container chính chia tỷ lệ phần trăm hiển thị bằng grid để cân bằng 2 bên
        main_container = tk.Frame(self.root, bg="#f0f2f5")
        main_container.pack(fill="both", expand=True, padx=20, pady=15)
        main_container.columnconfigure(0, weight=4) # Left side
        main_container.columnconfigure(1, weight=5) # Right side
        main_container.rowconfigure(0, weight=1)

        # --- KHU VỰC BÊN TRÁI ---
        left_frame = tk.Frame(main_container, bg="#f0f2f5")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10)

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
        self.path_text.pack(anchor="w", fill="both", expand=True)

        if self.final_path is not None:
            formatted_path = " -> ".join(self.final_path)
            self.path_text.insert("1.0", f"Tìm thấy đích thành công!\nTổng số bước đi: {len(self.final_path)}\nTổng số Node đã duyệt hiển thị: {len(self.history)}\n\nLộ trình di chuyển:\n{formatted_path}")
        else:
            if len(self.history) >= self.max_steps:
                self.path_text.insert("1.0", f"❌ THẤT BẠI: VƯỢT QUÁ GIỚI HẠN DUYỆT!\n\nThuật toán đã bị ngắt cưỡng bức do chạm mốc giới hạn tối đa ({self.max_steps} nodes) mà bạn đã thiết lập nhưng chưa tìm thấy đích.")
                messagebox.showwarning("Cảnh báo giới hạn", f"Thuật toán dừng lại vì chạm ngưỡng giới hạn {self.max_steps} bước duyệt để bảo vệ bộ nhớ!")
            else:
                self.path_text.insert("1.0", "❌ KHÔNG TÌM THẤT ĐƯỜNG ĐI!\n\nĐã quét sạch toàn bộ không gian cây trạng thái khả thi của bài toán này nhưng không tồn tại lời giải nào.")

        self.path_text.config(state="disabled")

        # --- KHU VỰC BÊN PHẢI (Tối ưu hóa bố cục cố định) ---
        right_frame = tk.Frame(main_container, bg="white", relief="solid", bd=1)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        # Sử dụng grid nội bộ cho right_frame để kiểm soát không gian chặt chẽ
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(3, weight=1) # Cho phép khu vực văn bản giải thích tự co giãn trong vùng an toàn

        tk.Label(right_frame, text="Mô phỏng tiến trình duyệt cây trạng thái", font=("Helvetica", 11, "bold"), bg="#1a73e8", fg="white", pady=6).grid(row=0, column=0, sticky="ew")

        self.step_lbl = tk.Label(right_frame, text="", font=("Helvetica", 10, "italic"), bg="white", fg="#5f6368", pady=5)
        self.step_lbl.grid(row=1, column=0, pady=2)

        self.live_grid_frame = tk.Frame(right_frame, bg="#bdc3c7", bd=2)
        self.live_grid_frame.grid(row=2, column=0, pady=5)

        tk.Label(right_frame, text="Chi tiết hành động tại Node này:", font=("Helvetica", 10, "bold"), bg="white", fg="#e65100").grid(row=3, column=0, sticky="w", padx=20, pady=(10, 2))

        # Cải tiến: Đưa nhãn giải thích vào một Message widget hoặc tăng wraplength để tự động xuống hàng, tránh đẩy các nút điều khiển xuống dưới
        self.explain_text_lbl = tk.Label(right_frame, text="", font=("Helvetica", 11), bg="#fff3e0", fg="#e65100", relief="solid", bd=1, wraplength=500, justify="center", pady=6)
        self.explain_text_lbl.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 15))

        # Khung điều khiển cố định hoàn toàn ở đáy của bảng mô phỏng
        control_frame = tk.Frame(right_frame, bg="white")
        control_frame.grid(row=5, column=0, pady=(10, 15))

        ttk.Button(control_frame, text="◀ Bước trước", command=self.prev_step).grid(row=0, column=0, padx=6, pady=4)
        self.play_btn = ttk.Button(control_frame, text="▶ Tự động chạy", command=self.toggle_auto_play)
        self.play_btn.grid(row=0, column=1, padx=6, pady=4)
        ttk.Button(control_frame, text="Bước sau ▶", command=self.next_step).grid(row=0, column=2, padx=6, pady=4)

        ttk.Button(control_frame, text="⏮ Về START", command=self.jump_to_start).grid(row=1, column=0, padx=6, pady=4)
        ttk.Button(control_frame, text="⏭ Đến cuối lịch sử", command=self.jump_to_goal).grid(row=1, column=2, padx=6, pady=4)

        self.update_live_matrix()

    def draw_static_matrix(self, frame, state, is_goal=False):
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                text = "" if val == 0 else str(val)
                bg_color = "#e8eaed" if val == 0 else ("#e6f4ea" if is_goal else "#ffffff")
                fg_color = "#137333" if (is_goal and val != 0) else "#3c4043"

                lbl = tk.Label(frame, text=text, font=("Helvetica", 11, "bold"), width=4, height=2, bg=bg_color, fg=fg_color, bd=1, relief="raised")
                lbl.grid(row=i, column=j, padx=1, pady=1)

    def update_live_matrix(self):
        if not self.history: return
        current_state, explanation = self.history[self.current_index]
        for widget in self.live_grid_frame.winfo_children(): widget.destroy()

        self.step_lbl.config(text=f"Trạng thái đang xét (Node thứ: {self.current_index + 1}/{len(self.history)})")
        if current_state == self.goal_state or "🎉" in explanation or "chạm mặt" in explanation:
            self.explain_text_lbl.config(text=explanation, bg="#d4edda", fg="#155724")
            is_success_state = True
        else:
            self.explain_text_lbl.config(text=explanation, bg="#fff3e0", fg="#e65100")
            is_success_state = False

        for i in range(3):
            for j in range(3):
                val = current_state[i][j]
                text = "" if val == 0 else str(val)
                bg_color = "#e8eaed" if val == 0 else ("#d4edda" if is_success_state else "#e8f0fe")
                fg_color = "#155724" if is_success_state else "#1a73e8"
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
        if self.is_playing: self.stop_auto_play()
        else:
            self.is_playing = True
            self.play_btn.config(text="⏸ Dừng chạy")
            self.auto_play_loop()

    def auto_play_loop(self):
        if self.is_playing:
            has_next = self.next_step()
            if has_next: self.play_job = self.root.after(120, self.auto_play_loop)

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