import networkx as nx  # Thư viện để tạo và thao tác với đồ thị
from heapq import heappush, heappop  # Cấu trúc hàng đợi ưu tiên để thực hiện thuật toán Dijkstra
import matplotlib.pyplot as plt  # Thư viện vẽ đồ thị
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Tích hợp matplotlib với Tkinter
import tkinter as tk  # Thư viện tạo giao diện người dùng
from tkinter import messagebox, ttk  # Các thành phần giao diện Tkinter (hộp thoại, widget)

# ============================
# THUẬT TOÁN DIJKSTRA
# ============================
def dijkstra(graph, source, target):  # Hàm tìm đường đi ngắn nhất từ nguồn đến đích
    distances = {node: float('inf') for node in graph.nodes}  # Khởi tạo khoảng cách ban đầu là vô cực cho mọi node
    distances[source] = 0  # Khoảng cách từ nguồn đến chính nó là 0
    predecessors = {node: None for node in graph.nodes}  # Lưu node trước đó để truy vết đường đi
    pq = [(0, source)]  # Hàng đợi ưu tiên với (khoảng cách, node), bắt đầu từ nguồn

    while pq:  # Lặp cho đến khi hàng đợi rỗng
        current_distance, current_node = heappop(pq)  # Lấy node có khoảng cách nhỏ nhất
        if current_node == target:  # Nếu đến đích, dừng lại
            break
        if current_distance > distances[current_node]:  # Bỏ qua nếu đã tìm được đường ngắn hơn
            continue
        for neighbor, attrs in graph[current_node].items():  # Duyệt các node láng giềng
            weight = attrs['weight']  # Lấy trọng số cạnh
            distance = current_distance + weight  # Tính khoảng cách mới
            if distance < distances[neighbor]:  # Nếu tìm được đường ngắn hơn
                distances[neighbor] = distance  # Cập nhật khoảng cách
                predecessors[neighbor] = current_node  # Lưu node trước
                heappush(pq, (distance, neighbor))  # Thêm vào hàng đợi

    path = []  # Danh sách lưu đường đi
    current_node = target  # Bắt đầu từ đích
    while current_node is not None:  # Truy vết ngược từ đích về nguồn
        path.append(current_node)
        current_node = predecessors[current_node]
    path.reverse()  # Đảo ngược để có đường đi từ nguồn đến đích

    return path, distances[target] if distances[target] != float('inf') else None  # Trả về đường đi và độ dài

# ============================
# THUẬT TOÁN K-SHORTEST PATHS
# ============================
def yen_k_shortest_paths(graph, source, target, k):  # Hàm tìm K đường đi ngắn nhất (Yen's algorithm)
    A = []  # Danh sách các đường đi ngắn nhất đã tìm được
    B = []  # Hàng đợi chứa các đường đi tiềm năng

    path, length = dijkstra(graph, source, target)  # Tìm đường đi ngắn nhất đầu tiên
    if not path:  # Nếu không có đường đi, trả về rỗng
        return []
    A.append((path, length))  # Thêm đường đi đầu tiên vào A

    for _ in range(1, k):  # Tìm thêm K-1 đường đi
        prev_path, _ = A[-1]  # Lấy đường đi ngắn nhất trước đó

        for i in range(len(prev_path) - 1):  # Duyệt từng node trong đường đi trước đó
            spur_node = prev_path[i]  # Node kích hoạt (spur node)
            root_path = prev_path[:i+1]  # Phần đường đi từ nguồn đến spur node

            temp_graph = graph.copy()  # Sao chép đồ thị để sửa đổi tạm thời
            edges_to_remove = set()  # Tập hợp các cạnh cần xóa
            for a_path, _ in A:  # Duyệt các đường đi trong A
                if len(a_path) > i and a_path[:i+1] == root_path:  # Nếu đường đi có cùng root path
                    edge = (a_path[i], a_path[i+1])  # Cạnh cần xóa
                    if temp_graph.has_edge(*edge) or temp_graph.has_edge(*edge[::-1]):
                        edges_to_remove.add(tuple(sorted(edge)))  # Thêm cạnh vào tập xóa

            for edge in edges_to_remove:  # Xóa các cạnh trong danh sách
                try:
                    temp_graph.remove_edge(*edge)
                except:
                    continue

            spur_path, spur_length = dijkstra(temp_graph, spur_node, target)  # Tìm đường đi từ spur node đến đích
            if not spur_path:  # Nếu không tìm được, bỏ qua
                continue

            total_path = root_path[:-1] + spur_path  # Ghép root path và spur path
            try:
                total_length = sum(graph[total_path[j]][total_path[j+1]]['weight']
                                   for j in range(len(total_path)-1))  # Tính độ dài đường đi
            except KeyError:  # Nếu có lỗi (cạnh không tồn tại), bỏ qua
                continue

            if (total_path, total_length) not in B:  # Nếu đường đi chưa có trong B
                heappush(B, (total_length, total_path))  # Thêm vào hàng đợi B

        if not B:  # Nếu không còn đường đi tiềm năng
            break
        length, path = heappop(B)  # Lấy đường đi ngắn nhất từ B
        A.append((path, length))  # Thêm vào danh sách kết quả

    return [(path, length) for path, length in A]  # Trả về danh sách K đường đi

# ============================
# GIAO DIỆN TKINTER
# ============================
class NetworkApp:  # Lớp chính của ứng dụng
    def __init__(self, root):  # Hàm khởi tạo
        self.root = root  # Cửa sổ chính
        self.root.title("Ứng Dụng K-Shortest Paths Tối Ưu Hóa Định Tuyến Internet")  # Tiêu đề
        self.root.geometry("1000x900")  # Kích thước cửa sổ

        # Đồ thị mẫu
        self.G = nx.Graph()  # Tạo đồ thị vô hướng
        edges = [  # Danh sách các cạnh mẫu
            ('PC1', 'Router1', 5), ('PC1', 'Router2', 8),
            ('Router1', 'Router2', 3), ('Router1', 'Router3', 6),
            ('Router2', 'Router3', 4), ('Router2', 'Router4', 7),
            ('Router3', 'Router4', 2), ('Router3', 'PC2', 5),
            ('Router4', 'PC2', 4)
        ]
        self.G.add_weighted_edges_from(edges)  # Thêm các cạnh vào đồ thị

        # Giao diện nhập liệu
        self.input_frame = ttk.Frame(self.root)  # Khung nhập liệu
        self.input_frame.pack(padx=30, pady=20, fill="x")  # Đặt khung vào cửa sổ

        ttk.Label(self.input_frame, text="PC/Router Nguồn:").grid(row=0, column=0, sticky="w", pady=5)  # Nhãn nguồn
        self.source_entry = ttk.Entry(self.input_frame, width=20)  # Ô nhập nguồn
        self.source_entry.grid(row=0, column=1, padx=15)  # Đặt ô nhập
        self.source_entry.insert(0, "PC1")  # Giá trị mặc định

        ttk.Label(self.input_frame, text="PC/Router Đích:").grid(row=1, column=0, sticky="w", pady=5)  # Nhãn đích
        self.target_entry = ttk.Entry(self.input_frame, width=20)  # Ô nhập đích
        self.target_entry.grid(row=1, column=1, padx=15)  # Đặt ô nhập
        self.target_entry.insert(0, "PC2")  # Giá trị mặc định

        ttk.Label(self.input_frame, text="Số đường đi (K):").grid(row=2, column=0, sticky="w", pady=5)  # Nhãn K
        self.k_entry = ttk.Entry(self.input_frame, width=20)  # Ô nhập K
        self.k_entry.grid(row=2, column=1, padx=15)  # Đặt ô nhập
        self.k_entry.insert(0, "3")  # Giá trị mặc định

        # Nút điều khiển
        self.button_frame = ttk.Frame(self.root)  # Khung chứa các nút
        self.button_frame.pack(pady=10)  # Đặt khung

        ttk.Button(self.button_frame, text="Tìm K Đường Đi Ngắn Nhất", command=self.run_simulation).pack(side="left", padx=10)  # Nút chạy mô phỏng
        ttk.Button(self.button_frame, text="Thêm PC/Router", command=self.open_add_node_window).pack(side="left", padx=10)  # Nút thêm node
        ttk.Button(self.button_frame, text="Xóa PC/Router", command=self.open_delete_node_window).pack(side="left", padx=10)  # Nút xóa node
        ttk.Button(self.button_frame, text="Lưu Sơ Đồ Mạng", command=self.save_network).pack(side="left", padx=10)  # Nút lưu đồ thị

        # Vẽ đồ thị chính
        self.fig, self.ax = plt.subplots(figsize=(14, 8))  # Tạo hình vẽ matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # Tích hợp với Tkinter
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)  # Đặt canvas vào cửa sổ

        # Tạo cửa sổ kết quả
        self.result_window = tk.Toplevel(self.root)  # Cửa sổ hiển thị kết quả
        self.result_window.title("Kết quả Tìm Đường Đi")  # Tiêu đề
        self.result_window.geometry("600x400")  # Kích thước
        self.result_window.protocol("WM_DELETE_WINDOW", lambda: None)  # Ngăn đóng cửa sổ

        # Khung kết quả với Treeview và Scrollbar
        self.result_frame = ttk.Frame(self.result_window)  # Khung chứa kết quả
        self.result_frame.pack(padx=10, pady=10, fill="both", expand=True)  # Đặt khung

        ttk.Label(self.result_frame, text="Kết quả Tìm Đường Đi:", font=("Arial", 12, "bold")).pack(anchor="w")  # Nhãn tiêu đề kết quả

        # Thêm khung chứa Treeview và Scrollbar
        tree_frame = ttk.Frame(self.result_frame)  # Khung cho Treeview
        tree_frame.pack(fill="both", expand=True)  # Đặt khung

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")  # Thanh cuộn dọc
        scrollbar.pack(side="right", fill="y")  # Đặt thanh cuộn

        self.result_tree = ttk.Treeview(tree_frame, columns=("Path", "Latency"), show="headings", yscrollcommand=scrollbar.set)  # Bảng hiển thị kết quả
        self.result_tree.heading("Path", text="Đường nắng")  # Tiêu đề cột đường đi
        self.result_tree.heading("Latency", text="Độ trễ (ms)")  # Tiêu đề cột độ trễ
        self.result_tree.column("Path", width=400)  # Độ rộng cột đường đi
        self.result_tree.column("Latency", width=100)  # Độ rộng cột độ trễ
        self.result_tree.pack(fill="both", expand=True)  # Đặt bảng

        scrollbar.config(command=self.result_tree.yview)  # Liên kết thanh cuộn với bảng

        self.draw_network([], "PC1", "PC2")  # Vẽ đồ thị ban đầu

    def draw_network(self, k_paths, source, target):  # Hàm vẽ đồ thị
        """Vẽ sơ đồ mạng cùng các đường đi ngắn nhất."""
        self.ax.clear()  # Xóa hình vẽ cũ
        pos = nx.spring_layout(self.G, seed=42, k=1.8)  # Tạo bố cục cho đồ thị
        node_colors = ['lightgreen' if node.startswith("PC") else '#FF8C00' for node in self.G.nodes]  # Màu node (PC: xanh, Router: cam)

        nx.draw(self.G, pos, ax=self.ax, with_labels=True, node_color=node_colors,
                node_size=1800, font_size=13, font_weight='bold',
                edge_color='gray', width=3, alpha=0.8)  # Vẽ đồ thị

        # Vẽ nhãn trọng số
        edge_labels = {(u, v): f"{d['weight']}ms" for u, v, d in self.G.edges(data=True)}  # Tạo nhãn trọng số
        nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, font_size=11)  # Vẽ nhãn

        # Vẽ các đường đi ngắn nhất
        colors = ['red', 'blue', 'purple']  # Màu cho các đường đi
        for i, (path, length) in enumerate(k_paths):  # Duyệt các đường đi
            edges = list(zip(path[:-1], path[1:]))  # Tạo danh sách cạnh
            nx.draw_networkx_edges(self.G, pos, edgelist=edges,
                                   edge_color=colors[i % len(colors)],
                                   width=7, style='dashed', alpha=0.9)  # Vẽ đường đi

        self.ax.set_title(f"Tối Ưu Hóa Định Tuyến ({len(k_paths)} đường từ {source} đến {target})", fontsize=16)  # Tiêu đề hình
        self.canvas.draw()  # Cập nhật hình vẽ

    def run_simulation(self):  # Hàm chạy mô phỏng tìm đường
        """Chạy tìm đường đi và hiển thị kết quả."""
        source = self.source_entry.get().strip()  # Lấy node nguồn
        target = self.target_entry.get().strip()  # Lấy node đích
        try:
            k = int(self.k_entry.get())  # Lấy số đường đi K
            if k <= 0:
                raise ValueError()  # Kiểm tra K hợp lệ
        except:
            messagebox.showerror("Lỗi", "K phải là số nguyên dương.")  # Báo lỗi nếu K không hợp lệ
            return

        if source not in self.G.nodes or target not in self.G.nodes:  # Kiểm tra node tồn tại
            messagebox.showerror("Lỗi", f"{source} hoặc {target} không tồn tại.")
            return

        k_paths = yen_k_shortest_paths(self.G, source, target, k)  # Tìm K đường đi ngắn nhất

        # Xóa dữ liệu cũ trong Treeview
        for item in self.result_tree.get_children():  # Xóa các hàng cũ
            self.result_tree.delete(item)

        if not k_paths:  # Nếu không tìm được đường đi
            self.result_tree.insert("", "end", values=("Không tìm thấy đường đi", ""))
        else:
            for i, (path, length) in enumerate(k_paths, 1):  # Hiển thị từng đường đi
                path_str = " -> ".join(path)  # Chuỗi đường đi
                self.result_tree.insert("", "end", values=(path_str, f"{length}ms"))  # Thêm vào bảng

        self.draw_network(k_paths, source, target)  # Vẽ lại đồ thị với đường đi

    def open_add_node_window(self):  # Hàm mở cửa sổ thêm node
        """Cửa sổ thêm node mới."""
        add_window = tk.Toplevel(self.root)  # Tạo cửa sổ mới
        add_window.title("Thêm PC/Router")  # Tiêu đề
        add_window.geometry("300x300")  # Kích thước

        ttk.Label(add_window, text="Tên node mới:").pack(pady=5)  # Nhãn tên node
        node_entry = ttk.Entry(add_window)  # Ô nhập tên node
        node_entry.pack()

        ttk.Label(add_window, text="Loại node:").pack()  # Nhãn loại node
        node_type = tk.StringVar(value="PC")  # Biến lưu loại node
        ttk.Radiobutton(add_window, text="PC", value="PC", variable=node_type).pack()  # Nút chọn PC
        ttk.Radiobutton(add_window, text="Router", value="Router", variable=node_type).pack()  # Nút chọn Router

        ttk.Label(add_window, text="Kết nối đến node:").pack(pady=5)  # Nhãn node kết nối
        connect_node = ttk.Combobox(add_window, values=list(self.G.nodes))  # Ô chọn node kết nối
        connect_node.pack()

        ttk.Label(add_window, text="Độ trễ (ms):").pack()  # Nhãn độ trễ
        weight_entry = ttk.Entry(add_window)  # Ô nhập độ trễ
        weight_entry.pack()

        def add_node():  # Hàm thêm node
            node_name = node_entry.get().strip()  # Lấy tên node
            connect_to = connect_node.get().strip()  # Lấy node kết nối
            try:
                weight = float(weight_entry.get().strip())  # Lấy độ trễ
                if weight <= 0:
                    raise ValueError()  # Kiểm tra độ trễ hợp lệ
            except:
                messagebox.showerror("Lỗi", "Độ trễ không hợp lệ.")  # Báo lỗi
                return

            if not node_name or node_name in self.G.nodes:  # Kiểm tra tên node hợp lệ
                messagebox.showerror("Lỗi", "Tên node không hợp lệ hoặc đã tồn tại.")
                return
            if connect_to not in self.G.nodes:  # Kiểm tra node kết nối tồn tại
                messagebox.showerror("Lỗi", "Node kết nối không tồn tại.")
                return

            self.G.add_node(node_name)  # Thêm node mới
            self.G.add_edge(node_name, connect_to, weight=weight)  # Thêm cạnh
            self.draw_network([], self.source_entry.get(), self.target_entry.get())  # Vẽ lại đồ thị
            add_window.destroy()  # Đóng cửa sổ

        ttk.Button(add_window, text="Thêm", command=add_node).pack(pady=15)  # Nút thêm

    def open_delete_node_window(self):  # Hàm mở cửa sổ xóa node
        """Cửa sổ xóa node mới."""
        delete_window = tk.Toplevel(self.root)  # Tạo cửa sổ mới
        delete_window.title("Xóa PC/Router")  # Tiêu đề
        delete_window.geometry("300x300")  # Kích thước

        ttk.Label(delete_window, text="Chọn node cần xóa:").pack(pady=5)  # Nhãn chọn node
        delete_node_combobox = ttk.Combobox(delete_window, values=list(self.G.nodes))  # Ô chọn node
        delete_node_combobox.pack(pady=5)

        def delete_node():  # Hàm xóa node
            node_to_delete = delete_node_combobox.get().strip()  # Lấy node cần xóa
            if node_to_delete not in self.G.nodes:  # Kiểm tra node tồn tại
                messagebox.showerror("Lỗi", f"{node_to_delete} không tồn tại.")
                return
            self.G.remove_node(node_to_delete)  # Xóa node
            messagebox.showinfo("Thành công", f"Đã xóa node {node_to_delete}.")  # Thông báo
            delete_window.destroy()  # Đóng cửa sổ
            self.draw_network([], self.source_entry.get(), self.target_entry.get())  # Vẽ lại đồ thị

        ttk.Button(delete_window, text="Xóa", command=delete_node).pack(pady=15)  # Nút xóa

    def save_network(self):  # Hàm lưu đồ thị
        """Lưu sơ đồ mạng ra file."""
        nx.write_gml(self.G, "network.gml")  # Lưu đồ thị dưới dạng file GML
        messagebox.showinfo("Thành công", "Đã lưu sơ đồ mạng.")  # Thông báo

# ============================
# KHỞI TẠO ỨNG DỤNG
# ============================
if __name__ == "__main__":  # Kiểm tra nếu chạy trực tiếp
    root = tk.Tk()  # Tạo cửa sổ chính
    app = NetworkApp(root)  # Khởi tạo ứng dụng
    root.mainloop()  # Chạy vòng lặp chính của Tkinter