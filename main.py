from collections import Counter

from flask import Flask, render_template

from src.analyzer import *
from src.config import Config
from src.scraper import Blog

app = Flask(__name__)


@app.route('/')
def home():
    # 持久化日志
    # logger.add("endofyear_{time}.log")

    # 读取配置
    config = Config("config.ini")

    # 博客
    my_blog = Blog(config.rss_url)

    logger.info(f"Blog title: {my_blog.title}")
    logger.info(f"Blog link: {my_blog.link}")
    logger.info(f"Blog life: {my_blog.life}")
    logger.info(f"Blog count: {my_blog.article_count}")
    logger.info(f"Total words: {my_blog.article_word_count}")

    data = {
        "blog_name": my_blog.title,
        "blog_link": my_blog.link,
        "blog_life_year": my_blog.life // 365,
        "blog_life_day": my_blog.life % 365,
        "blog_article_count": my_blog.article_count,
        "blog_article_word_count": my_blog.article_word_count,
    }

    # 文章处理
    for i, post in enumerate(my_blog.post_lists(), 1):
        # 情感分
        post.score = analyze_sentiment(post.content)
        # 分类, 关键字
        post.category, post.keys = classify_and_extract_keywords(text=post.content, topK=21,
                                                                 stopwords='data/stop_words.txt',
                                                                 tech_terms_file='data/tech_terms.txt')

        # 权重, 日子计算
        post.weight, post.date = calculate_weight(post.time)

        # 输出展示
        logger.info(f"Post #{i}:")
        logger.info(f"{type(post.time)}")
        logger.info(post)
        logger.info(f"Keys: {post.score}")
        logger.info(f"Category: {post.category}")
        logger.info(f"Keys: {post.keys}")
        logger.info(f"Weight: {post.weight}")
        logger.info(f"Date: {post.date}")

    # 权重计算
    weights = [post.weight for post in my_blog.post_lists()]
    max_weight = max(weights)
    max_item = [post for post in my_blog.post_lists() if post.weight == max_weight][0]

    data.update({
        "blog_title": max_item.title,
        "blog_content": max_item.content[0:50],
        "blog_content_date": max_item.date,
    })

    # 关键词计算
    all_keys = []
    for post in my_blog.post_lists():
        all_keys.extend(post.keys)

    keyword_counts = Counter(all_keys)
    top_keywords = keyword_counts.most_common(5)
    data.update({
        "blog_top_keywords": top_keywords
    })

    # 分类计算
    categories = [post.category for post in my_blog.post_lists()]
    cat_counts = Counter(categories)
    most_common_cat = cat_counts.most_common(1)[0][0]

    data.update({
        "blog_category": "技术" if most_common_cat == 1 else "生活"
    })

    logger.debug(data)

    return render_template('painting.html', data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
