"""
开发环境启动入口
开发环境默认使用 development，可通过 FLASK_ENV 环境变量覆盖
"""
import os
from app import create_app

if __name__ == '__main__':
    config = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config)
    app.run(host='127.0.0.1', port=5000, debug=app.config.get('DEBUG', True))
