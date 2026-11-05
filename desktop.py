"""StudyHub Windows desktop entry point."""
import ctypes
import socket
import sys
import threading
import time
import traceback

def show_error(message):
    ctypes.windll.user32.MessageBoxW(0, message, 'StudyHub', 0x10)


def main():
    import uvicorn
    import webview
    from app.main import app
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    sock.listen(128)
    port = sock.getsockname()[1]
    config = uvicorn.Config(app, host='127.0.0.1', port=port, log_level='warning', access_log=False, loop='asyncio', http='h11', lifespan='on')
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
    thread.start()
    for _ in range(200):
        if server.started: break
        if not thread.is_alive(): raise RuntimeError('本地服务无法启动。请检查数据目录的访问权限。')
        time.sleep(.05)
    else: raise RuntimeError('本地服务启动超时。')
    webview.settings['ALLOW_DOWNLOADS'] = True
    webview.create_window('StudyHub · 个人知识库', f'http://127.0.0.1:{port}/', width=1380, height=900, min_size=(900, 600), background_color='#f8f9fc')
    try:
        webview.start(gui='edgechromium', debug=False)
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        import os
        from pathlib import Path
        log_dir=Path(os.environ.get('LOCALAPPDATA', Path.home()))/'StudyHub'
        log_dir.mkdir(parents=True,exist_ok=True)
        (log_dir/'startup-error.log').write_text(traceback.format_exc(),encoding='utf-8')
        show_error(f'StudyHub 无法启动：{exc}\n\n请确认已安装 Microsoft Edge WebView2 Runtime。')
        if not getattr(sys, 'frozen', False): traceback.print_exc()
