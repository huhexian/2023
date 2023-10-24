import os

import jieba.analyse
from loguru import logger

from snownlp import SnowNLP


def classify_and_extract_keywords(text, topK, stopwords,
                                  tech_terms_file):
    """
    判断文章是否为技术类文章，并提取关键词。

    :param text: 输入的文本
    :param topK: 提取的关键词数量，建议为 7
    :param stopwords: 停用词表文件路径，默认为'data/stop_words.txt'
    :param tech_terms_file: 技术相关词汇文件路径，默认为'data/tech_terms.txt'
    :return: 文章类别(True: '生活类', False: '技术类')，以及关键词列表
    """
    if not isinstance(text, str):
        logger.error("输入错误：文本应为字符串类型")
        return None, []
    if not isinstance(topK, int) or topK < 1:
        logger.error("输入错误：topK应为大于0的整数")
        return None, []

    if not os.path.exists(stopwords):
        logger.error("输入错误：停用词文件不存在")
        return None, []
    if not os.path.exists(tech_terms_file):
        logger.error("输入错误：技术术语文件不存在")
        return None, []

    try:
        jieba.analyse.set_stop_words(stopwords)
        keywords = jieba.analyse.extract_tags(text, topK=topK)
    except Exception as e:
        logger.error(f"关键词提取出错：{e}")
        return None, []

    with open(tech_terms_file, 'r', encoding='utf-8') as f:
        tech_terms = [line.strip().lower() for line in f]

    for keyword in keywords:
        if keyword.lower() in tech_terms:
            logger.debug(f"文章：{text[:10]}……,类别：技术,关键词：{topK} - {keywords}")
            return False, keywords

    logger.debug(f"文章：{text[:10]}……,类别：生活,关键词：{topK} - {keywords}")
    return True, keywords


def analyze_sentiment(text):
    s = SnowNLP(text)
    return round(s.sentiments * 100)

