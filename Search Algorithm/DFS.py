###### 8-puzzle DFS (Duyệt theo chiều sâu - ĐÃ TỐI ƯU)
start = ((2, 8, 3), (1, 6, 4), (7, 0, 5))

goal = ((1, 2, 3), (8, 0, 4), (7, 6, 5))

# Thay đổi thứ tự ưu tiên duyệt để DFS tìm cận Goal nhanh hơn, tránh sa lầy nhánh cụt
moves = {"R": (0, 1), "D": (1, 0), "L": (0, -1), "U": (-1, 0)}  # Thay đổi từ U,D,L,R sang R,D,L,U


# Tìm vị trí số 0
def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None


# Đổi chỗ ô trống
def swap(state, x1, y1, x2, y2):
    state = [list(row) for row in state]
    state[x1][y1], state[x2][y2] = state[x2][y2], state[x1][y1]
    return tuple(tuple(row) for row in state)


def print_state(state):
    for row in state:
        print(row)
    print()


# DFS TỐI ƯU
def dfs(start, goal):
    stack = []
    stack.append((start, []))

    # Đánh dấu visited ngay khi một node chuẩn bị được cho vào stack
    # Điều này ngăn chặn việc trùng lặp node trong stack từ đầu
    visited = set()
    visited.add(start)

    # Giới hạn độ sâu để tránh tìm kiếm vô hạn ở các nhánh không đi đến đâu
    max_depth = 30
    step_count = 0  # Biến đếm số node thực tế phải pop ra

    while stack:
        current, path = stack.pop()
        step_count += 1

        print(f"--- Bước duyệt thứ {step_count} ---")
        print_state(current)

        # Kiểm tra goal
        if current == goal:
            print(f"Đã tìm thấy goal! Tổng số node phải duyệt qua: {step_count}")
            return path

        # Kiểm tra giới hạn độ sâu của nhánh hiện tại
        if len(path) >= max_depth:
            continue

        # Tìm vị trí ô trống
        x, y = find_zero(current)

        # Sinh node con
        for move, (dx, dy) in moves.items():
            nx = x + dx
            ny = y + dy

            # Kiểm tra hợp lệ
            if 0 <= nx < 3 and 0 <= ny < 3:
                new_state = swap(current, x, y, nx, ny)

                # TỐI ƯU: Chỉ thêm vào stack nếu trạng thái này CHƯA TỪNG xuất hiện
                if new_state not in visited:
                    visited.add(new_state)  # Khóa trạng thái này lại ngay lập tức
                    stack.append((new_state, path + [move]))
    return None


result = dfs(start, goal)

print("Đường đi tìm được:")
print(result)