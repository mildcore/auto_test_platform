"""
开发环境启动入口
"""
from app import create_app

if __name__ == '__main__':
    app = create_app('development')
    app.run(host='127.0.0.1', port=5000, debug=True)
