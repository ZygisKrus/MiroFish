import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.config import Config
from app.services.graph_builder import GraphBuilderService

def check():
    gb = GraphBuilderService()
    gid = "mirofish_54febd34f1384516"
    try:
        # Just try to get it
        g = gb.client.graph.get(graph_id=gid)
        print(f"Graph {gid} is ACTIVE")
    except Exception as e:
        print(f"Graph {gid} is NOT ACTIVE: {e}")

if __name__ == "__main__":
    check()
