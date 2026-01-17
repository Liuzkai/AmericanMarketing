#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Web 服务启动脚本
美股量化分析系统 Web 界面

使用方法:
    python run_web.py

访问地址:
    http://localhost:5000
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from web.app import create_app

if __name__ == '__main__':
    app = create_app()

    print("\n" + "=" * 60)
    print("  美股量化分析系统 Web 服务")
    print("=" * 60)
    print("\n访问地址:")
    print("  - 本地: http://localhost:5001")
    print("  - 网络: http://0.0.0.0:5001")
    print("\n功能页面:")
    print("  - 首页: http://localhost:5001/")
    print("  - 单股分析: http://localhost:5001/analyze")
    print("  - 市场扫描: http://localhost:5001/scanner")
    print("\nAPI 端点:")
    print("  - 股票分析: http://localhost:5001/api/v1/stock/<TICKER>/analyze")
    print("  - 快速报价: http://localhost:5001/api/v1/stock/<TICKER>/quote")
    print("  - 市场扫描: http://localhost:5001/api/v1/market/scan")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60 + "\n")

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=True
    )
