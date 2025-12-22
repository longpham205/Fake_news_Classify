# main/run_web.py
import os
import sys
import uvicorn

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

def main():
    print("Run backend...")
    uvicorn.run(
        "web.backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
