import networkx as nx
import matplotlib.pyplot as plt

def build_system_graph():
    # Создаем направленный граф
    G = nx.DiGraph()

    # --- 1. Добавляем узлы (ноды) ---
    # Вход и выход
    G.add_node("u", type="input")
    G.add_node("y", type="output")
    
    # Сумматоры
    G.add_node("S1", type="sum")
    G.add_node("S2", type="sum")
    G.add_node("S3", type="sum")
    G.add_node("Sy", type="sum")
    
    # Интеграторы (представлены переменными состояния)
    G.add_node("x1", type="state")
    G.add_node("x2", type="state")
    G.add_node("x3", type="state")

    # --- 2. Добавляем связи (ребра) с весами ---
    
    # Связи от входа u
    G.add_edge("u", "S1", weight="-7")
    G.add_edge("u", "S2", weight="4")
    G.add_edge("u", "S3", weight="5")

    # Связи к сумматору S1 (для x1_dot)
    G.add_edge("x1", "S1", weight="-7.4")
    G.add_edge("x2", "S1", weight="4.8")
    G.add_edge("x3", "S1", weight="-4")
    G.add_edge("S1", "x1", weight="1/p") # Интегратор

    # Связи к сумматору S2 (для x2_dot)
    G.add_edge("x1", "S2", weight="-9.2")
    G.add_edge("x2", "S2", weight="8.4")
    G.add_edge("x3", "S2", weight="-17")
    G.add_edge("S2", "x2", weight="1/p") # Интегратор

    # Связи к сумматору S3 (для x3_dot)
    G.add_edge("x1", "S3", weight="-2.2")
    G.add_edge("x2", "S3", weight="3.4")
    G.add_edge("x3", "S3", weight="-9")
    G.add_edge("S3", "x3", weight="1/p") # Интегратор

    # Связи к сумматору Sy (для выхода y)
    G.add_edge("x1", "Sy", weight="-3.4")
    G.add_edge("x2", "Sy", weight="3.8")
    G.add_edge("x3", "Sy", weight="-7")
    G.add_edge("Sy", "y", weight="1")

    # --- 3. Настройка визуализации ---
    
    # Позиции узлов (задаем вручную для красоты)
    pos = {
        "u": (0, 0.5),
        "S1": (1.5, 1.5), "x1": (3, 1.5),
        "S2": (1.5, 0.5), "x2": (3, 0.5),
        "S3": (1.5, -0.5), "x3": (3, -0.5),
        "Sy": (4.5, 0.5), "y": (6, 0.5)
    }

    plt.figure(figsize=(12, 8))
    
    # Цвета для разных типов узлов
    node_colors = []
    for node in G.nodes():
        ntype = G.nodes[node].get("type")
        if ntype == "input": node_colors.append("lightgreen")
        elif ntype == "output": node_colors.append("lightcoral")
        elif ntype == "sum": node_colors.append("lightgray")
        elif ntype == "state": node_colors.append("skyblue")

    # Рисуем узлы
    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color=node_colors, edgecolors="black")
    
    # Рисуем подписи узлов
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight="bold")

    # Рисуем связи
    # Используем connectionstyle, чтобы стрелки были изогнутыми и не пересекались
    nx.draw_networkx_edges(
        G, pos, 
        arrowstyle="-|>", 
        arrowsize=20, 
        edge_color="gray", 
        connectionstyle="arc3,rad=0.1",
        node_size=2500
    )

    # Рисуем подписи к связям (коэффициенты)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(
        G, pos, 
        edge_labels=edge_labels, 
        font_color="red", 
        font_size=10,
        label_pos=0.7 # Сдвигаем подпись ближе к концу стрелки, чтобы не перекрывать узлы
    )

    plt.title("Граф системы в пространстве состояний", fontsize=16)
    plt.axis("off") # Отключаем оси
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    build_system_graph()