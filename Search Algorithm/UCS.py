import heapq
import copy

# Định nghĩa trạng thái Đích (Goal)
GOAL = ((1, 2, 3),
        (4, 5, 6),
        (7, 8, 0))

# Thứ tự ưu tiên hành động khi chi phí bằng nhau: Left, Right, Up, Down
ACTIONS = ['L', 'R', 'U', 'D']

# Hàm tìm vị trí hàng và cột của ô trống (số 0) trong ma trận
def find_zero(state):
    for r in range(3):
        for c in range(3):
            if state[r][c] == 0:
                return r, c
    return -1, -1

# Hàm thực hiện hành động dịch chuyển ô trống
# Trả về ma trận mới và chi phí của hành động (bằng giá trị ô số bị đổi chỗ)
def move(state, action):
    r, c = find_zero(state)
    new_r, new_c = r, c

    if action == 'L': new_c -= 1
    elif action == 'R': new_c += 1
    elif action == 'U': new_r -= 1
    elif action == 'D': new_r += 1

    # Kiểm tra xem hành động có vượt ra khỏi biên ma trận 3x3 không
    if 0 <= new_r < 3 and 0 <= new_c < 3:
        # Chuyển tuple thành list để có thể thay đổi giá trị
        new_state = [list(row) for row in state]

        # Giá trị của ô số bị đổi chỗ với ô trống chính là chi phí bước đi
        cost = new_state[new_r][new_c]

        # Hoán đổi ô trống (0) và ô số
        new_state[r][c], new_state[new_r][new_c] = new_state[new_r][new_c], new_state[r][c]

        # Trả về ma trận dạng tuple (để có thể lưu vào set/dict) và chi phí
        return tuple(tuple(row) for row in new_state), cost

    return None, 0

# Hàm in ma trận ra màn hình cho đẹp và dễ nhìn
def print_matrix(state):
    for row in state:
        print(f"  {list(row)}")
    print()

# Hàm thuật toán Uniform Cost Search (UCS)
def uniform_cost_search(start_state):
    # Đếm số vòng lặp (để theo dõi các bước duyệt/step)
    step_count = 0

    # Frontier là một Heap Queue (Priority Queue)
    # Lưu cấu trúc: (tổng_chi_phí_g, thứ_tự_vào, trạng_thái_hiện_tại, đường_đi)
    # "thứ_tự_vào" giúp heapq phân tách độ ưu tiên khi tổng chi phí g bằng nhau
    frontier = []

    # Đưa nút gốc vào Frontier
    # g = 0, thứ tự vào = 0, trạng thái đầu, danh sách hành động trống
    heapq.heappush(frontier, (0, step_count, start_state, []))

    # Tập Explored để lưu các trạng thái đã duyệt xong (chỉ lưu ma trận)
    explored = set()

    # Từ điển lưu chi phí thấp nhất để tới một trạng thái nằm trong Frontier (để cập nhật chi phí rẻ hơn)
    frontier_costs = {start_state: 0}

    print(u"--- Bắt đầu chạy thuật toán UCS ---")

    while frontier:
        # 1. Lấy nút có chi phí g nhỏ nhất ra khỏi Frontier
        g_cost, _, current_state, path = heapq.heappop(frontier)
        step_count += 1

        print(f"==========================================")
        print(f"VÒNG LẶP {step_count} (Lấy ra nút có g = {g_cost}):")
        print_matrix(current_state)

        # 2. Kiểm tra đích (Chỉ kiểm tra khi nút được lấy ra khỏi Frontier)
        if current_state == GOAL:
            print(u"🎉 TÌM THẤY ĐÍCH RỒI!")
            print(f"-> Tổng chi phí tối ưu: {g_cost}")
            print(f"-> Chuỗi hành động di chuyển ô trống: {path}")
            return path

        # 3. Thêm trạng thái vào Explored
        explored.add(current_state)

        # 4. Mở rộng nút hiện tại theo thứ tự ưu tiên: L, R, U, D
        for action in ACTIONS:
            next_state, action_cost = move(current_state, action)

            # Nếu hành động hợp lệ (không kịch biên)
            if next_state is not None:
                new_g = g_cost + action_cost

                # Nếu trạng thái con đã nằm trong Explored -> Bỏ qua
                if next_state in explored:
                    continue

                # Nếu trạng thái con CHƯA nằm trong Frontier HOẶC tìm được đường mới RẺ HƠN đường cũ trong Frontier
                if next_state not in frontier_costs or new_g < frontier_costs[next_state]:
                    # Cập nhật chi phí tốt nhất cho trạng thái này
                    frontier_costs[next_state] = new_g

                    # Nạp vào Frontier xếp hàng
                    new_path = path + [action]
                    heapq.heappush(frontier, (new_g, step_count, next_state, new_path))
                    print(f" -> Sinh nút con qua hành động [{action}]: g = {new_g}")

    print(u"Không tìm thấy đường đi đến đích.")
    return None

# Chạy thử nghiệm với ví dụ của bạn
if __name__ == "__main__":
    START = ((1, 2, 3),
             (4, 0, 6),
             (7, 5, 8))

    uniform_cost_search(START)