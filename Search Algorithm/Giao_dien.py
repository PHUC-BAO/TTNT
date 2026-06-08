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
            states_history.append((current, f"KẸT CỤC BỘ (Local Optimum)! Không có hướng nào quanh đây giảm h xuống dưới {curr_h}. Thuật toán dừng lại."))
            return None, states_history

    return path, states_history

# 2.9 THUẬT TOÁN STEEPEST-ASCENT HILL CLIMBING (Leo đồi dốc nhất)
def run_steepest_hill_climbing(start, goal, max_steps):
    current = start
    path = []
    states_history = []

    curr_h = manhattan_distance(current, goal)
    states_history.append((current, f"Bắt đầu tại START. Heuristic hiện tại h = {curr_h}"))

    while current != goal:
        if len(states_history) >= max_steps:
            return None, states_history

        x, y = find_zero(current)
        best_neighbor = None
        best_h = curr_h
        best_move = None
        best_move_name = None

        # Duyệt TẤT CẢ các hướng để tìm trạng thái tối ưu nhất
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

        # Nếu tìm được láng giềng tốt hơn hẳn trạng thái hiện tại
        if best_neighbor is not None:
            current = best_neighbor
            curr_h = best_h
            path.append(best_move)
            swapped_val = current[x][y]
            desc = f"Hành động [{best_move}]: Chọn hướng TỐT NHẤT {best_move_name} (đổi số {swapped_val}). h mới = {curr_h}."
            states_history.append((current, desc))
        else:
            states_history.append((current, f"KẸT CỤC BỘ (Local Optimum)! Không hướng nào quanh đây tốt hơn h = {curr_h}."))
            return None, states_history

    return path, states_history


# 2.10 THUẬT TOÁN STOCHASTIC HILL CLIMBING (Leo đồi ngẫu nhiên)
def run_stochastic_hill_climbing(start, goal, max_steps):
    current = start
    path = []
    states_history = []

    curr_h = manhattan_distance(current, goal)
    states_history.append((current, f"Bắt đầu tại START. Heuristic hiện tại h = {curr_h}"))

    while current != goal:
        if len(states_history) >= max_steps:
            return None, states_history

        x, y = find_zero(current)
        better_neighbors = []

        # Thu thập toàn bộ các hướng đi giúp cải thiện Heuristic
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)
                if neighbor_h < curr_h:
                    better_neighbors.append((neighbor, neighbor_h, move, move_name))

        if better_neighbors:
            # Chọn NGẪU NHIÊN một trong số các hướng tốt
            current, curr_h, move, move_name = random.choice(better_neighbors)
            path.append(move)
            swapped_val = current[x][y]
            desc = f"Hành động [{move}]: Lựa chọn NGẪU NHIÊN hướng đi tốt {move_name} (đổi số {swapped_val}). h mới = {curr_h}."
            states_history.append((current, desc))
        else:
            states_history.append((current, f"KẸT CỤC BỘ! Không có hướng đi ngẫu nhiên nào cải thiện được h = {curr_h}."))
            return None, states_history

    return path, states_history


# 2.11 THUẬT TOÁN HILL CLIMBING WITH RANDOM WALKS (Leo đồi vượt kẹt ngẫu nhiên)
def run_hill_climbing_random_walk(start, goal, max_steps, walk_steps=6):
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

        # 1. Cố gắng leo đồi bình thường
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)

                if neighbor_h < curr_h:
                    current = neighbor
                    curr_h = neighbor_h
                    path.append(move)
                    swapped_val = current[x][y]
                    states_history.append((current, f"Hành động [{move}]: Leo đồi sang {move_name} (đổi số {swapped_val}). h mới = {curr_h}."))
                    neighbor_moved = True
                    break

        # 2. Nếu kẹt, thực hiện chuỗi Random Walk để dịch chuyển sang thung lũng khác
        if not neighbor_moved:
            states_history.append((current, f"⚠️ KẸT CỤC BỘ tại h = {curr_h}! Thực hiện Random Walk {walk_steps} bước để phá kẹt..."))

            for _ in range(walk_steps):
                if current == goal:
                    break
                x, y = find_zero(current)
                valid_moves = []
                for move, (dx, dy), move_name in ACTIONS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 3 and 0 <= ny < 3:
                        valid_moves.append((move, dx, dy, move_name))

                if valid_moves:
                    move, dx, dy, move_name = random.choice(valid_moves)
                    current = swap(current, x, y, x + dx, y + dy)
                    curr_h = manhattan_distance(current, goal)
                    path.append(move)
                    swapped_val = current[x][y]
                    states_history.append((current, f"🎲 [Random Walk]: Đi ngẫu nhiên hướng [{move}] {move_name} (đổi số {swapped_val}) -> h = {curr_h}"))

    return path, states_history


# 2.12 THUẬT TOÁN LOCAL BEAM SEARCH (Tìm kiếm chùm cục bộ với k = 3)
def run_local_beam_search(start, goal, max_steps, k=3):
    # Mỗi phần tử trong beam lưu dạng: (h_value, trạng_thái, lộ_trình_đã_đi)
    curr_h = manhattan_distance(start, goal)
    beam = [(curr_h, start, [])]
    states_history = []
    states_history.append((start, f"Khởi tạo chùm (Beam Search) với độ rộng k = {k}. Gốc có h = {curr_h}"))

    step_count = 0
    while step_count < max_steps:
        # Kiểm tra xem có node nào trong chùm chạm đích chưa
        for _, state, path in beam:
            if state == goal:
                states_history.append((state, "Thành công! Một nhánh trong chùm tìm kiếm đã chạm tới ĐÍCH."))
                return path, states_history

        successors = []
        # Tạo tất cả các trạng thái con của TOÀN BỘ các trạng thái trong chùm hiện tại
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

        # Sắp xếp tất cả các con của chùm theo Heuristic tăng dần và chọn lọc lấy k cái tốt nhất
        successors.sort(key=lambda x: x[0])
        beam = successors[:k]
        step_count += 1

        # Lấy trạng thái đứng đầu chùm (tốt nhất) để hiển thị lịch sử lên GUI trực quan
        best_h, best_state, _ = beam[0]
        desc = f"Vòng duyệt {step_count}: Sàng lọc chùm mới. Trạng thái tốt nhất hiện tại có h = {best_h} (Độ rộng chùm giữ lại: {len(beam)} node)."
        states_history.append((best_state, desc))

    return None, states_history


# 2.13 THUẬT TOÁN LUYỆN KIM (Simulated Annealing - SA)
def run_simulated_annealing(start, goal, max_steps):
    current = start
    path = []
    states_history = []

    curr_h = manhattan_distance(current, goal)
    states_history.append((current, f"Bắt đầu Luyện Kim tại START. h = {curr_h}, Nhiệt độ ban đầu T = 100.0"))

    # Thiết lập các tham số tôi luyện kim
    T = 100.0          # Nhiệt độ ban đầu
    alpha = 0.95        # Hệ số hạ nhiệt (cooling rate)

    while current != goal:
        if len(states_history) >= max_steps:
            return None, states_history

        if T < 0.001:
            states_history.append((current, f"Lò nguội hoàn toàn (T đạt giới hạn dưới). Thuật toán dừng lại tại h = {curr_h}."))
            return None, states_history

        x, y = find_zero(current)
        valid_neighbors = []

        # Lấy tất cả các láng giềng hợp lệ quanh vị trí ô trống
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                neighbor = swap(current, x, y, nx, ny)
                neighbor_h = manhattan_distance(neighbor, goal)
                valid_neighbors.append((neighbor, neighbor_h, move, move_name))

        if not valid_neighbors:
            return None, states_history

        # Chọn ngẫu nhiên MỘT láng giềng bất kỳ (bản chất của SA là chọn ngẫu nhiên trạng thái kế tiếp)
        next_state, next_h, move, move_name = random.choice(valid_neighbors)

        # Tính toán độ chênh lệch năng lượng (Delta E). Vì ta muốn giảm h nên Delta E = h_cũ - h_mới
        # Nếu next_h nhỏ hơn (tốt hơn), delta_e sẽ > 0
        delta_e = curr_h - next_h

        if delta_e > 0:
            # Trạng thái mới tốt hơn -> Chấp nhận ngay lập tức
            current = next_state
            curr_h = next_h
            path.append(move)
            states_history.append((current, f"✅ Hướng tốt: Di chuyển [{move}] {move_name}. h mới = {curr_h} (Giảm được {-delta_e} đơn vị). T = {T:.3f}"))
        else:
            # Trạng thái mới tệ hơn hoặc bằng -> Chấp nhận với xác suất Boltzmann P = e^(delta_e / T)
            # Vì delta_e <= 0 nên toán tử mũ cơ số e sẽ cho ra kết quả trong khoảng (0, 1]
            prob = math.exp(delta_e / T)
            rand_val = random.random()

            if rand_val < prob:
                # Chấp nhận bước nhảy tệ này để phá kẹt
                current = next_state
                curr_h = next_h
                path.append(move)
                states_history.append((current, f"🎲 Chấp nhận hướng tệ hơn nhờ nhiệt độ! Hướng [{move}] {move_name}. h tăng lên {curr_h} (Xác suất P={prob:.3f} > {rand_val:.3f}). T = {T:.3f}"))
            else:
                # Từ chối, giữ nguyên trạng thái cũ ở bước này
                states_history.append((current, f"❌ Từ chối hướng tệ [{move}] {move_name} (h={next_h}). Xác suất P={prob:.3f} <= {rand_val:.3f}. Giữ nguyên. T = {T:.3f}"))

        # Hạ nhiệt độ theo chu kỳ
        T *= alpha

    return path, states_history


# 2.14 THUẬT TOÁN TÌM KIẾM HAI HƯỚNG (Bidirectional BFS)
def run_bidirectional_search(start, goal, max_steps):
    # Hai hàng đợi cho hai đầu
    queue_f = deque([(start, [])])  # Xuôi từ Start (Forward)
    queue_b = deque([(goal, [])])   # Ngược từ Goal (Backward)

    # Hai tập đã duyệt lưu vết cùng lộ trình tương ứng dẫn đến trạng thái đó
    # key: state -> value: list of moves
    visited_f = {start: []}
    visited_b = {goal: []}

    states_history = []
    states_history.append((start, "🧭 Khởi tạo Tìm kiếm Hai hướng: Nhánh Xuôi (Start) và Nhánh Ngược (Goal) bắt đầu quét song song."))

    # Bản đồ đảo ngược ký tự hướng di chuyển để tính toán lộ trình nhánh Ngược
    reverse_move = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}

    step_count = 0
    while queue_f and queue_b:
        if len(states_history) >= max_steps:
            return None, states_history

        # 1. Phát triển 1 bước bên phía Nhánh Xuôi (Forward)
        curr_f, path_f = queue_f.popleft()
        states_history.append((curr_f, f"➡️ [Nhánh Xuôi] Đang xét một Node. Kích thước tập duyệt xuôi: {len(visited_f)}"))

        # Kiểm tra giao điểm ngay lập tức
        if curr_f in visited_b:
            # Hai nhánh đã chạm nhau! Kết hợp lộ trình
            full_path = path_f + visited_b[curr_f]
            states_history.append((curr_f, "🎉 HAI MA TRẬN ĐÃ GẶP NHAU TẠI ĐÂY! Hoàn thành kết nối lộ trình giữa Start và Goal."))
            return full_path, states_history

        x, y = find_zero(curr_f)
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                next_f = swap(curr_f, x, y, nx, ny)
                if next_f not in visited_f:
                    visited_f[next_f] = path_f + [move]
                    queue_f.append((next_f, path_f + [move]))

        # 2. Phát triển 1 bước bên phía Nhánh Ngược (Backward)
        curr_b, path_b = queue_b.popleft()
        states_history.append((curr_b, f"⬅️ [Nhánh Ngược] Đang xét một Node. Kích thước tập duyệt ngược: {len(visited_b)}"))

        # Kiểm tra giao điểm
        if curr_b in visited_f:
            # Hai nhánh gặp nhau
            full_path = visited_f[curr_b] + path_b
            states_history.append((curr_b, "🎉 HAI MA TRẬN ĐÃ GẶP NHAU TẠI ĐÂY! Hoàn thành kết nối lộ trình giữa Start và Goal."))
            return full_path, states_history

        x, y = find_zero(curr_b)
        for move, (dx, dy), move_name in ACTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 3 and 0 <= ny < 3:
                next_b = swap(curr_b, x, y, nx, ny)
                if next_b not in visited_b:
                    # Chú ý: Hành động đẩy ô trống nhánh ngược từ Goal lên cần đảo ngược hướng di chuyển thực tế
                    actual_move = reverse_move[move]
                    # Đường đi nhánh ngược được chèn vào ĐẦU danh sách để đảm bảo đúng thứ tự khi nối chuỗi
                    new_path_b = [actual_move] + path_b
                    visited_b[next_b] = new_path_b
                    queue_b.append((next_b, new_path_b))

        step_count += 1

    return None, states_history


# ==============================================================================
# 3. GIAO DIỆN ỨNG DỤNG
# ==============================================================================
class PuzzleApp:

    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver Simulation Pro")
        self.root.geometry("1150x880") # Tăng chiều cao một chút để chứa giao diện 14 nút bấm thông thoáng
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

        # Hàng 3: Các thuật toán Tìm kiếm cục bộ nâng cao (Local Search)
        ttk.Button(btn_frame, text="Steepest Hill Climbing", command=lambda: self.validate_and_start("SteepestHC")).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(btn_frame, text="Stochastic Hill Climbing", command=lambda: self.validate_and_start("StochasticHC")).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(btn_frame, text="Random Walk HC", command=lambda: self.validate_and_start("RandomWalkHC")).grid(row=2, column=2, padx=5, pady=5)
        ttk.Button(btn_frame, text="Local Beam Search", command=lambda: self.validate_and_start("LocalBeam")).grid(row=2, column=3, padx=5, pady=5)

        # CẬP NHẬT: Hàng 4: Các thuật toán mới yêu cầu bổ sung
        ttk.Button(btn_frame, text="🔥 Simulated Annealing", command=lambda: self.validate_and_start("SA")).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="we")
        ttk.Button(btn_frame, text="🧭 Bidirectional Search", command=lambda: self.validate_and_start("Bidirectional")).grid(row=3, column=2, columnspan=2, padx=5, pady=5, sticky="we")

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
        elif algo_type == "SteepestHC":
            self.final_path, self.history = run_steepest_hill_climbing(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "StochasticHC":
            self.final_path, self.history = run_stochastic_hill_climbing(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "RandomWalkHC":
            self.final_path, self.history = run_hill_climbing_random_walk(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "LocalBeam":
            self.final_path, self.history = run_local_beam_search(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "SA":
            self.final_path, self.history = run_simulated_annealing(self.start_state, self.goal_state, self.max_steps)
        elif algo_type == "Bidirectional":
            self.final_path, self.history = run_bidirectional_search(self.start_state, self.goal_state, self.max_steps)

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
            self.path_text.insert("1.0", f"Tìm thấy đích thành công!\nTổng số bước đi: {len(self.final_path)}\nTổng số Node đã duyệt hiển thị: {len(self.history)}\n\nLộ trình di chuyển:\n{formatted_path}")
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

        # CẬP NHẬT: Xử lý màu sắc hiển thị linh hoạt cho cả điểm kết nối của Bidirectional Search
        if current_state == self.goal_state or "🎉" in explanation:
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
