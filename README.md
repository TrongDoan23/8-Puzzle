# 8-Puzzle Solver

Ứng dụng desktop mô phỏng và trực quan hóa các thuật toán AI Search.  
Xây dựng bằng **Python 3** + **PyQt6**, thiết kế theo hướng OOP.

---

## Cài đặt

```bash
pip install -r requirements.txt
python main.py
```

**Yêu cầu:** Python 3.10+, PyQt6 ≥ 6.7

---

## Ba chế độ hoạt động

Ứng dụng tự động chuyển chế độ dựa trên thuật toán được chọn trong combobox.

---

## 1 — 8-Puzzle

Giải bài toán 8 ô số (3×3) từ trạng thái ngẫu nhiên về trạng thái đích.

```
Đích:  1 2 3
       4 5 6
       7 8 _
```

### Tính năng
- **Random** — sinh board ngẫu nhiên (luôn giải được, không trùng Goal)
- **Solve** — chạy thuật toán được chọn, hiển thị animation từng bước
- **Pause / Continue / Stop / Reset** — kiểm soát quá trình animation
- **Solution Steps** — danh sách các bước, click để nhảy tới bước bất kỳ
- **Speed slider** — điều chỉnh tốc độ 0.25x → 5x ngay cả khi đang chạy
- **Statistics** — thời gian, số node mở rộng, số node sinh ra, độ sâu, bộ nhớ

### Nhóm thuật toán

#### Uninformed Search
| Thuật toán | Mô tả |
|---|---|
| BFS | Tìm kiếm theo chiều rộng, luôn tìm đường ngắn nhất |
| DFS | Tìm kiếm theo chiều sâu với depth limit |
| IDS | Iterative Deepening — kết hợp ưu điểm BFS và DFS |
| UCS | Uniform Cost Search — mở rộng theo chi phí tích lũy |

#### Informed Search
| Thuật toán | Mô tả |
|---|---|
| Greedy | Chọn node có heuristic thấp nhất, nhanh nhưng không tối ưu |
| A* | f(n) = g(n) + h(n), tìm đường tối ưu |
| IDA* | A* với iterative deepening, tiết kiệm bộ nhớ |

#### Local Search
| Thuật toán | Mô tả |
|---|---|
| Hill Climbing | Leo đồi đơn giản, dừng ở cực trị địa phương |
| Steepest Ascent HC | Đánh giá toàn bộ láng giềng, chọn bước tốt nhất |
| Stochastic HC | Chọn ngẫu nhiên trong các bước cải thiện |
| Random Restart HC | Khởi động lại từ vị trí ngẫu nhiên khi bị kẹt |
| Local Beam Search | Giữ k trạng thái tốt nhất ở mỗi bước |
| Simulated Annealing | Chấp nhận bước xấu theo xác suất giảm dần |

#### Partial Observable Search
| Thuật toán | Mô tả |
|---|---|
| Sensorless Search | Không có cảm biến — tìm chuỗi hành động cho mọi trạng thái ban đầu |
| Belief State Search | Duy trì tập trạng thái có thể, chọn hành động tốt nhất trung bình |
| Contingency Search | Lập kế hoạch online, tái lập kế hoạch sau mỗi hành động |
| AND-OR Graph Search | Tìm kiếm trong môi trường phi tất định |

#### Heuristic
Các thuật toán có heuristic hỗ trợ 3 loại:
- **Manhattan Distance** — tổng khoảng cách Manhattan
- **Misplaced Tiles** — số ô sai vị trí
- **Linear Conflict** — Manhattan + 2 × số xung đột tuyến tính

---

## 2 — Graph Coloring (CSP)

Khi chọn một trong 4 thuật toán CSP, ứng dụng chuyển sang chế độ **Graph Coloring**.  
Bài toán: tô màu các vùng của một đồ thị sao cho không có 2 vùng kề nhau cùng màu.

### Tính năng
- **🎲 Random Graph** — sinh đồ thị ngẫu nhiên mới (6–9 node, luôn 4-colorable)
- **Auto Solve** — thuật toán tự động tô màu với animation từng bước
- **Tô màu thủ công** — click vào một node → chọn màu từ 4 nút màu
  - Cạnh đỏ = xung đột (2 node kề cùng màu)
  - ✅ khi hoàn thành không có xung đột
- **Speed slider** — điều chỉnh tốc độ animation
- Đồ thị mặc định: **Bản đồ nước Úc** (7 vùng, kinh điển trong giáo trình AI)

### Thuật toán

| Thuật toán | Mô tả |
|---|---|
| **Backtracking** | Gán màu từng node, quay lui khi vi phạm ràng buộc |
| **Forward Checking** | Sau mỗi lần gán, loại bỏ màu không hợp lệ khỏi domain của node kề |
| **AC-3** | Cưỡng bức tính nhất quán cung (Arc Consistency), thu hẹp domain trước khi backtrack |
| **Min-Conflicts** | Khởi đầu ngẫu nhiên, lặp: chọn node có conflict → đổi sang màu ít conflict nhất |

### Bảng màu
🔴 Red &nbsp; 🔵 Blue &nbsp; 🟢 Green &nbsp; 🟡 Yellow

---

## 3 — Tic-Tac-Toe (Adversarial Search)

Khi chọn một trong 3 thuật toán Adversarial, ứng dụng chuyển sang chế độ **Tic-Tac-Toe**.  
Người dùng (X) đấu với AI (O) trên bàn cờ 3×3.

### Tính năng
- **Chọn ai đi trước** — Human (X) hoặc AI (O)
- **New Game** — bắt đầu ván mới
- **Bảng điểm** — tích lũy qua nhiều ván (Bạn / Hòa / AI)
- **Reset Score** — đặt lại điểm
- Animation đường thắng kéo dài khi có người thắng

### Thuật toán

| Thuật toán | Mô tả | Có thể thắng? |
|---|---|---|
| **Minimax** | Duyệt toàn bộ cây game, AI chơi hoàn hảo | ❌ Không thể thắng |
| **Alpha Beta** | Minimax + cắt tỉa alpha-beta, nhanh hơn, cũng hoàn hảo | ❌ Không thể thắng |
| **Expectiminimax** | Thêm 15% xác suất đi ngẫu nhiên, AI đôi khi mắc lỗi | ✅ Có thể thắng |

---

## Cấu trúc project

```
EightPuzzle/
├── main.py                        # Entry point
├── gui/
│   ├── main_window.py             # Cửa sổ chính, quản lý 3 chế độ
│   ├── board_widget.py            # Bàn cờ 8-Puzzle với animation
│   ├── control_panel.py           # Combobox chọn thuật toán (luôn hiển thị)
│   ├── solution_panel.py          # Danh sách bước giải
│   ├── stats_panel.py             # Thống kê hiệu năng
│   ├── tictactoe_widget.py        # Bàn cờ X-O
│   ├── tictactoe_panel.py         # Controls + bảng điểm X-O
│   ├── graph_coloring_widget.py   # Đồ thị với tô màu tương tác
│   ├── graph_coloring_panel.py    # Controls + swatches màu
│   └── styles.py                  # Light / Dark mode stylesheet
├── algorithms/
│   ├── base.py                    # BaseAlgorithm + SolveResult
│   ├── bfs.py, dfs.py, ids.py, ucs.py
│   ├── greedy.py, astar.py, ida.py
│   ├── hill_climbing.py, steepest_ascent.py
│   ├── stochastic_hc.py, random_restart.py
│   ├── beam_search.py, simulated_annealing.py
│   ├── sensorless.py, belief_state.py
│   ├── contingency.py, and_or.py
│   ├── minimax.py                 # Minimax + AlphaBeta + Expectiminimax + TTT logic
│   └── graph_coloring.py          # GC algorithms + graph generation
├── models/
│   ├── state.py                   # Trạng thái board 8-Puzzle
│   └── puzzle.py                  # Logic puzzle
└── utils/
    ├── heuristic.py               # Manhattan, Misplaced, Linear Conflict
    ├── random_board.py            # Sinh board solvable
    └── animation.py               # Speed presets
```

---

## Giao diện

- **Light / Dark mode** — nút toggle góc trên phải
- Layout 3 vùng: Board/Game (trái) | Solution Steps (giữa) | Controls (phải)
- Combobox thuật toán **luôn hiển thị** — đổi thuật toán bất cứ lúc nào
- Phần dưới right panel tự động swap theo chế độ được chọn
