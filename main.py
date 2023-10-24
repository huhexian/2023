from src.analyzer import *
from src.config import Config
from src.scraper import Blog
from loguru import logger

if __name__ == '__main__':
    # 持久化日志
    # logger.add("endofyear_{time}.log")
    config = Config("config.ini")

    my_blog = Blog(config.rss_url)

    logger.info(f"Blog title: {my_blog.title}")
    logger.info(f"Blog link: {my_blog.link}")
    logger.info(f"Blog life: {my_blog.life}")
    logger.info(f"Total words: {my_blog.article_word_count}")

    for i, post in enumerate(my_blog.post_lists(), 1):
        # 情感分
        post.score = analyze_sentiment(post.content)
        # 分类, 关键字
        post.category, post.keys = classify_and_extract_keywords(text=post.content, topK=7,
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



