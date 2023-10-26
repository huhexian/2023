from flask import Flask, render_template, redirect, url_for
from loguru import logger

from src.config import Config
from src.generator import build_data

app = Flask(__name__)
logger.add("endofyear_{time}.log")


@app.route('/')
def home():
    # 默认主题 painting
    return redirect(url_for('painting'))


@app.route('/painting')
def painting():
    # 如果数据存在，直接返回
    if blog_data := Config("config.ini").blog_data:
        return render_template('painting.html', data=blog_data)

    # 如果数据不存在，需要时间生成，并写入配置
    return render_template('painting.html', data=build_data())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True)
