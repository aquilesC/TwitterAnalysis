HEADER = {
    'Host': 'twitter.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://twitter.com/mauriciomacri',
    'X-Twitter-Active-User': 'yes',
    'X-Requested-With': 'XMLHttpRequest',
    'DNT': '1',
    'Connection': 'keep-alive'
    }

from .utils import (parse_response,
                    get_tweets,
                    get_timeline_user)