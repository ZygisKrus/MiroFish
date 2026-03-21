"""
MiroFish Backend 启动入口
"""

import os
import sys
import signal
import atexit
import psutil

# 解决 Windows 控制台中文乱码问题：在所有导入之前设置 UTF-8 编码
if sys.platform == 'win32':
    # 设置环境变量确保 Python 使用 UTF-8
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    # 重新配置标准输出流为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config


def cleanup_child_processes():
    """清理所有由该应用派生的子进程（防止模拟脚本变成孤儿进程）"""
    print("\n[System] 执行清理操作，关闭所有后台模拟进程...")
    try:
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        for child in children:
            try:
                print(f"[System] 终止子进程 PID: {child.pid}")
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        
        gone, alive = psutil.wait_procs(children, timeout=3)
        for p in alive:
            print(f"[System] 强制终止子进程 PID: {p.pid}")
            p.kill()
    except Exception as e:
        print(f"[System] 清理子进程时发生错误: {e}")


def signal_handler(sig, frame):
    """处理中断信号"""
    print(f"\n[System] 收到信号 {sig}，准备退出...")
    cleanup_child_processes()
    sys.exit(0)


def main():
    """主函数"""
    # 注册退出和信号处理
    atexit.register(cleanup_child_processes)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 验证配置
    errors = Config.validate()
    if errors:
        print("配置错误:")
        for err in errors:
            print(f"  - {err}")
        print("\n请检查 .env 文件中的配置")
        sys.exit(1)
    
    # 创建应用
    app = create_app()
    
    # 获取运行配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    debug = Config.DEBUG
    
    # 启动服务
    app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=False)


if __name__ == '__main__':
    main()

