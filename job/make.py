import json
import re
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd  # 新增：导入pandas处理CSV

# ===================== 1. 配置中文显示 =====================
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 解决中文乱码
plt.rcParams["axes.unicode_minus"] = False    # 解决负号显示问题

# ===================== 2. 加载并清洗数据 =====================
def load_and_clean_data():
    # 注意：将此处替换为你的 job_data.json 文件路径
    file_path = "job_data.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 数据清洗：去除标签空格、标准化字段
    cleaned_data = []
    for job in data:
        # 清洗 tags（如" Gym" → "Gym"）
        job['tags'] = [re.sub(r'^\s+|\s+$', '', tag) for tag in job['tags']]
        # 清洗学历/专业字段
        job['education']['degree'] = job['education']['degree'].strip()
        job['education']['majors'] = [m.strip() for m in job['education']['majors']]
        cleaned_data.append(job)
    return cleaned_data

# ===================== 3. 构建知识图谱 =====================
def build_knowledge_graph(job_data):
    # 初始化无向图
    G = nx.Graph()
    
    # 限制节点数量（避免图形过密，可选前50条数据）
    demo_data = job_data[:50]
    
    # 遍历数据，添加节点和边
    for job in demo_data:
        job_id = job["job_id"]
        job_title = job["job_title"]
        
        # 1. 添加职位节点（红色）
        G.add_node(job_id, type="Job", label=job_title, color="#FF9999")
        
        # 2. 添加技能节点（蓝色）+ 职位-技能边
        for skill in job["tags"]:
            if skill not in G.nodes:
                G.add_node(skill, type="Skill", label=skill, color="#99CCFF")
            G.add_edge(job_id, skill, relation="需要技能")
        
        # 3. 添加行业节点（绿色）+ 职位-行业边
        industry = job["company_industry"]
        if industry not in G.nodes:
            G.add_node(industry, type="Industry", label=industry, color="#99FF99")
        G.add_edge(job_id, industry, relation="属于行业")
        
        # 4. 添加学历节点（黄色）+ 职位-学历边
        degree = job["education"]["degree"]
        if degree not in G.nodes:
            G.add_node(degree, type="Degree", label=degree, color="#FFFF99")
        G.add_edge(job_id, degree, relation="要求学历")
    
    return G

# ===================== 新增：保存知识图谱为GraphML/GEXF =====================
def save_knowledge_graph(G, save_path="ai_job_kg.graphml", file_format="graphml"):
    """
    保存知识图谱到文件（GraphML/GEXF格式）
    :param G: 知识图谱网络x对象
    :param save_path: 保存路径（含文件名）
    :param file_format: 保存格式，支持 graphml / gexf（推荐graphml，兼容性更好）
    """
    try:
        if file_format.lower() == "graphml":
            nx.write_graphml(G, save_path, encoding='utf-8')
        elif file_format.lower() == "gexf":
            nx.write_gexf(G, save_path, encoding='utf-8')
        else:
            raise ValueError("仅支持 graphml / gexf 格式")
        print(f"知识图谱已保存为 {file_format} 格式：{save_path}")
    except Exception as e:
        print(f"保存知识图谱失败：{str(e)}")

# ===================== 新增：保存知识图谱为CSV文件 =====================
def save_kg_to_csv(G, nodes_csv_path="kg_nodes.csv", edges_csv_path="kg_edges.csv"):
    """
    将知识图谱的节点和边分别保存为CSV文件（结构化表格）
    :param G: 知识图谱networkx对象
    :param nodes_csv_path: 节点CSV保存路径
    :param edges_csv_path: 边CSV保存路径
    """
    try:
        # 1. 提取节点数据并保存
        node_list = []
        for node_id in G.nodes:
            node_attr = G.nodes[node_id]
            node_list.append({
                "节点ID": node_id,
                "节点类型": node_attr.get("type", ""),
                "节点标签": node_attr.get("label", ""),
                "节点颜色": node_attr.get("color", "")
            })
        nodes_df = pd.DataFrame(node_list)
        # utf-8-sig 解决Excel打开中文乱码问题
        nodes_df.to_csv(nodes_csv_path, index=False, encoding="utf-8-sig")
        print(f"节点数据已保存为CSV：{nodes_csv_path}")
        
        # 2. 提取边数据并保存
        edge_list = []
        for source, target, edge_attr in G.edges(data=True):
            edge_list.append({
                "源节点ID": source,
                "目标节点ID": target,
                "关系类型": edge_attr.get("relation", "")
            })
        edges_df = pd.DataFrame(edge_list)
        edges_df.to_csv(edges_csv_path, index=False, encoding="utf-8-sig")
        print(f"边数据已保存为CSV：{edges_csv_path}")
        
    except Exception as e:
        print(f"保存CSV失败：{str(e)}")

# ===================== 4. 可视化图谱 =====================
def visualize_graph(G, save_img_path=None):
    """
    可视化图谱并可选保存图片
    :param G: 知识图谱网络x对象
    :param save_img_path: 图片保存路径（如 "ai_job_kg.png"），None则仅展示不保存
    """
    # 提取节点颜色和标签
    node_colors = [G.nodes[node]["color"] for node in G.nodes]
    node_labels = {node: G.nodes[node]["label"] for node in G.nodes}
    
    # 布局算法（spring布局，固定种子保证可视化稳定）
    pos = nx.spring_layout(G, seed=42, k=1.2)  # k控制节点间距
    
    # 绘制图形
    plt.figure(figsize=(18, 12))
    
    # 绘制节点
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=1000,
        alpha=0.8
    )
    
    # 绘制边
    nx.draw_networkx_edges(
        G, pos,
        edge_color="#CCCCCC",
        alpha=0.6,
        width=1
    )
    
    # 绘制标签
    nx.draw_networkx_labels(
        G, pos,
        labels=node_labels,
        font_size=8,
        font_weight="bold"
    )
    
    # 绘制边的关系标签（可选，注释掉可简化视图）
    edge_labels = {(u, v): G.edges[u, v]["relation"] for u, v in G.edges}
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=6,
        alpha=0.7
    )
    
    # 配置标题和样式
    plt.title("AI职业知识图谱（轻量化版）", fontsize=16, pad=20)
    plt.axis("off")  # 关闭坐标轴
    plt.tight_layout()
    
    # 保存图片（如果指定路径）
    if save_img_path:
        try:
            plt.savefig(
                save_img_path,
                dpi=300,  # 分辨率，越高越清晰
                bbox_inches='tight',  # 防止标签被裁剪
                facecolor='white'  # 背景色（默认透明）
            )
            print(f"可视化图片已保存：{save_img_path}")
        except Exception as e:
            print(f"保存图片失败：{str(e)}")
    
    # 展示图谱
    plt.show()

# ===================== 主函数：一键运行 =====================
if __name__ == "__main__":
    # 安装依赖（首次运行需执行）
    # pip install pandas networkx matplotlib
    
    # 步骤1：加载数据
    print("正在加载并清洗数据...")
    job_data = load_and_clean_data()
    print(f"成功加载 {len(job_data)} 条职位数据")
    
    # 步骤2：构建图谱
    print("正在构建知识图谱...")
    kg_graph = build_knowledge_graph(job_data)
    print(f"图谱构建完成，包含 {len(kg_graph.nodes)} 个节点，{len(kg_graph.edges)} 条边")
    
    # 步骤3：保存为GraphML格式（可选）
    save_knowledge_graph(kg_graph, save_path="ai_job_kg.graphml", file_format="graphml")
    
    # 步骤4：保存为CSV文件（核心新增功能）
    save_kg_to_csv(kg_graph, nodes_csv_path="kg_nodes.csv", edges_csv_path="kg_edges.csv")
    
    # 步骤5：可视化并保存图片
    print("正在生成可视化图谱...")
    visualize_graph(kg_graph, save_img_path="ai_job_kg.png")
    print("所有操作完成！")