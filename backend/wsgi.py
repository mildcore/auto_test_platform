"""
WSGI入口文件
生产环境默认使用 production，可通过 FLASK_ENV 环境变量覆盖
"""
import os
from app import create_app

config = os.environ.get('FLASK_ENV', 'production')
app = create_app(config)

if __name__ == '__main__':
    app.run()
