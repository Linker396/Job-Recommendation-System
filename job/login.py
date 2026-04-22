from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# 加载环境变量（也可以直接写死在代码里）
load_dotenv()

# 连接配置
URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASS = os.getenv("NEO4J_PASSWORD")
DB = os.getenv("NEO4J_DATABASE")

def test_connection():
    try:
        # 创建驱动
        driver = GraphDatabase.driver(URI, auth=(USER, PASS))
        
        # 验证连接
        with driver.session(database=DB) as session:
            result = session.run("RETURN 'Connection successful!' AS message")
            record = result.single()
            print("✅ 连接成功：", record["message"])
        
        driver.close()
        
    except Exception as e:
        print("❌ 连接失败：", str(e))

if __name__ == "__main__":
    test_connection()