import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.config import Config
from app.services.graph_builder import GraphBuilderService

def cleanup():
    if not Config.ZEP_API_KEY:
        print("ZEP_API_KEY not found.")
        return
    
    gb = GraphBuilderService()
    # List of known graph IDs to delete to free up space
    to_delete = ["mirofish_5e1f9e8506c7467b", "mirofish_54febd34f1384516"]
    
    for gid in to_delete:
        print(f"Attempting to delete graph: {gid}")
        try:
            gb.delete_graph(gid)
            print(f"SUCCESS: Deleted {gid}")
        except Exception as e:
            print(f"FAILED to delete {gid}: {e}")

if __name__ == "__main__":
    cleanup()
