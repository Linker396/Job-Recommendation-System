from neo4j import GraphDatabase

# 1. 配置云数据库连接信息 (必须用官方库)
URI = "neo4j+s://a25e42b3.databases.neo4j.io"
AUTH = ("a25e42b3", "thsCz6IGG9-PxVVDsfvc6Sn-DAavCk8v7bIwhueQSIs")

# 2. 模拟前端传来的用户求职技能 (可以随时改成别的测试)
user_skills = ['Python', 'C++']

# 3. 编写推荐查询语句 
# 【注意这里的核心改变】: WHERE s.name IN $skills 
# 使用 $skills 作为占位符，而不是用 f-string 拼接，这样更安全且查询速度更快！
query = """
    MATCH (j:Job)-[:REQUIRE_SKILL]->(s:Skill)
    WHERE s.name IN $skills
    RETURN j.job_title AS title, j.min_salary AS min_salary, j.max_salary AS max_salary, collect(s.name) as matched
    ORDER BY size(matched) DESC
    LIMIT 5
"""

# 4. 连接数据库并执行查询
def get_job_recommendations(skills):
    # 初始化驱动
    driver = GraphDatabase.driver(URI, auth=AUTH)
    recommendations = []
    
    try:
        # 开启一个会话 (session)
        with driver.session() as session:
            # 执行查询，并将 Python 的 user_skills 赋值给 Cypher 中的 $skills 参数
            result = session.run(query, skills=skills)
            
            # 将返回的记录提取为标准的 Python 字典列表 (类似以前的 .data())
            recommendations = [record.data() for record in result]
            return recommendations
    finally:
        driver.close() # 记得关闭连接

# 5. 调用函数并打印结果给队友看
if __name__ == "__main__":
    results = get_job_recommendations(user_skills)
    
    print("=== 为用户推荐的职位 ===")
    if not results:
        print("没有找到匹配的职位。")
    else:
        for row in results:
            print(f"职位: {row['title']} | 薪资: {row['min_salary']}-{row['max_salary']} | 匹配技能: {row['matched']}")