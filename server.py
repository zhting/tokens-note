#!/usr/bin/env python3
# 本地服务器：静态托管 + 读写固定数据文件 ai-tools-data.json
import http.server
import json
import os
import socketserver
from functools import partial

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(ROOT, 'ai-tools-data.json')


class Handler(http.server.SimpleHTTPRequestHandler):
    def _read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length) if length else b''

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        path = self.path.split('?')[0].rstrip('/')
        if path == '/api/refresh-quota':
            try:
                from quota_fetch import refresh_data_file
                tools, results = refresh_data_file()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                body = json.dumps({
                    'ok': True,
                    'tools': tools,
                    'results': [
                        {
                            'id': r.get('id'),
                            'name': r.get('name'),
                            'ok': r.get('ok'),
                            'quotaPct': r.get('quotaPct'),
                            'source': r.get('source'),
                            'detail': r.get('detail'),
                            'error': r.get('error'),
                        } for r in results
                    ],
                }, ensure_ascii=False)
                self.wfile.write(body.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
            return

        # 仅支持保存固定数据文件
        if path in ('/ai-tools-data.json', '/api/save'):
            body = self._read_body()
            try:
                # 校验为合法 JSON 数组
                data = json.loads(body.decode('utf-8'))
                if not isinstance(data, list):
                    raise ValueError('顶层必须是数组')
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def end_headers(self):
        # 开发期禁用缓存，避免读到旧数据
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # 静默日志


class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main():
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    os.chdir(ROOT)
    with ReuseTCPServer(('127.0.0.1', port), Handler) as httpd:
        print(f'Serving {ROOT} at http://127.0.0.1:{port}/')
        print(f'数据文件: {DATA_FILE}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n已停止')


if __name__ == '__main__':
    main()
