"""
Flask 应用主入口
美股量化分析系统 Web 界面
"""
from flask import Flask, render_template
from flask_cors import CORS
import os


def create_app(config=None):
    """创建并配置 Flask 应用"""
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    # 基础配置
    app.config['JSON_AS_ASCII'] = False  # 支持中文 JSON
    app.config['JSON_SORT_KEYS'] = False  # 保持 JSON 键顺序
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 应用自定义配置
    if config:
        app.config.update(config)

    # 启用 CORS（允许跨域请求）
    CORS(app)

    # 注册 API 蓝图
    from web.api import routes
    app.register_blueprint(routes.api_bp, url_prefix='/api/v1')

    # 注册页面路由
    @app.route('/')
    def index():
        """首页"""
        return render_template('index.html')

    @app.route('/analyze')
    @app.route('/analyze/<ticker>')
    def analyze(ticker=None):
        """单股分析页面"""
        return render_template('analyze.html', ticker=ticker)

    @app.route('/scanner')
    def scanner():
        """市场扫描页面"""
        return render_template('scanner.html')

    @app.route('/about')
    def about():
        """关于页面"""
        return render_template('about.html')

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('500.html'), 500

    return app
