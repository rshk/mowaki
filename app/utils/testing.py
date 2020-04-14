from urllib.parse import urlparse, urlunparse


def make_test_database_url(url, prefix='test_'):
    p = urlparse(url)
    return urlunparse(p._replace(path=prefix + p.path[1:]))
