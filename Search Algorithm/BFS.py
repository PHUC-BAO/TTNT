###### 8-puzzle BFS (Duyệt theo chiều rộng)
from collections import deque
###### Khởi tạo trạng thái đầu và trạng thái đích
start = (
    (2, 8, 3),
    (1, 6, 4),
    (7, 0, 5)
)
goal = (
    (1, 2, 3),
    (8, 0, 4),
    (7, 6, 5)
)

###### Các bước di chuyển: Up, Down, Left, Right
moves = {
    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1)
}

###### Duyệt từng ô
def find_zero(state):
    for i in range(3):
        for j in range(3):
            ###### Gặp số 0 ta trả về vị trí
            if state[i][j] == 0:
                return i, j

###### Đổi chỗ ô trống với ô kế bên nó
def swap(state, x1, y1, x2, y2):
    state = [list(row) for row in state]

    state[x1][y1], state[x2][y2] = \
        state[x2][y2], state[x1][y1]

    return tuple(tuple(row) for row in state)

def bfs(start, goal):
    ###### Tạo hàng đợi
    queue = deque()
    ###### Thêm vào hàng đợi: (Trạng thái, đường đi)
    queue.append((start, []))

    ###### Lưu node đã được duyệt
    visited = set()
    visited.add(start)

    while queue:
        ###### Lấy node đầu tiên
        current, path = queue.popleft()

        ###### Kiểm tra đã đến đích chưa
        if current == goal:
            return path

        x, y = find_zero(current)

        ###### Sinh node con
        for move, (dx, dy) in moves.items():

            nx = x + dx
            ny = y + dy

            ###### Kiểm tra hợp lệ
            if 0 <= nx < 3 and 0 <= ny < 3:
                ###### Khởi tạo trạng thái mới
                new_state = swap(current, x, y, nx, ny)

                ###### Nếu chưa được duyệt qua thì thêm vào (Tránh bị lặp mãi mãi)
                if new_state not in visited:

                    visited.add(new_state)

                    queue.append(
                        (new_state, path + [move])
                    )

    return None

###### KQ
result = bfs(start, goal)
print("Đường đi:", result)