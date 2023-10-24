import configparser
from urllib.parse import urlparse
import os

from loguru import logger

from src.tools import check_website_status


class Config:
    def __init__(self, path):
        if not os.path.isfile(path):
            logger.error(f"配置文件 {path} 不存在或不是一个文件")
            raise FileNotFoundError

        self.path = path
        self.config = configparser.ConfigParser()

        try:
            self.config.read(self.path)
        except configparser.ParsingError as e:
            logger.error(f"解析配置文件 {self.path} 错误： {str(e)}")
            raise

        except PermissionError as e:
            logger.error(f"没有权限读取配置文件 {self.path}： {str(e)}")
            raise

        logger.info(f"成功加载配置文件 {self.path}")

    @property
    def rss_url(self):
        try:
            url = self.config.get('blog', 'rss', fallback=None)
        except configparser.NoSectionError:
            logger.error('未找到 blog 配置项，请检查拼写')
            return None

        if not url:
            logger.error('rss 配置值为空')
            return None

        if check_website_status(url):
            return url
        else:
            logger.error(f"rss URL {url} 不可访问")
            return None

    @property
    def rss_domain(self):
        rss_url = self.rss_url
        if rss_url is None:
            return None

        parsed = urlparse(rss_url)
        domain_parts = parsed.netloc.split('.')
        if len(domain_parts) < 2:
            logger.error(f"提供的 URL {rss_url} 的域名格式错误")
            return None

        return '.'.join(domain_parts[-2:])

