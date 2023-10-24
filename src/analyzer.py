import os

import jieba.analyse
import pytz
from dateutil.parser import parse
from loguru import logger
from lunardate import LunarDate
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


def calculate_weight(time_str):
    # 使用 dateutil.parser.parse() 函数解析日期和时间
    dt = parse(time_str)
    # 转换为中国时区
    dt = dt.astimezone(pytz.timezone('Asia/Shanghai'))
    # 初始化权重
    weight = 0
    date_str = ""

    # 因素1: 中国传统节假日
    # 首先将日期转换为农历
    lunar_date = LunarDate.fromSolarDate(dt.year, dt.month, dt.day)
    # 然后检查是否是节假日
    holidays = {
        (1, 1): '春节',
        (1, 15): '元宵节',
        (5, 5): '端午节',
        (7, 7): '七夕节',
        (7, 15): '中元节',
        (8, 15): '中秋节',
        (9, 9): '重阳节'
    }
    if (lunar_date.month, lunar_date.day) in holidays:
        weight += 5
        date_str = holidays[(lunar_date.month, lunar_date.day)]
    if dt.month == 4 and dt.day == 4:
        weight += 5
        date_str = "清明节"
    if dt.month == 12 and 21 <= dt.day <= 23:
        weight += 5
        date_str = "冬至节"
    if not date_str:
        date_str = f"{dt.month}月{dt.day}日"

    # 因素2: 22点到24点，0点到7点
    if 22 <= dt.hour or dt.hour < 7:
        weight += 5
    # 因素3: 7点-12点
    elif 7 <= dt.hour < 12:
        weight += 4
    # 因素4: 12 点-18点
    elif 12 <= dt.hour < 18:
        weight += 3
    # 因素5: 18点到22点
    elif 18 <= dt.hour < 22:
        weight += 2

    return weight, date_str
