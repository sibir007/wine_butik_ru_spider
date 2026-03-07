
# Scrapy settings for wine_butik_ru_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "wine_butik_ru_spider"

SPIDER_MODULES = ["wine_butik_ru_spider.spiders"]
NEWSPIDER_MODULE = "wine_butik_ru_spider.spiders"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 4
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

#A dict containing the downloader middlewares enabled by default in Scrapy. 
# Low orders are closer to the engine, high orders are closer to the downloader. 
# You should never modify this setting in your project, 
# modify DOWNLOADER_MIDDLEWARES instead
DOWNLOADER_MIDDLEWARES_BASE_to_see = {
    "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": 100,
    "scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware": 300,
    "scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware": 350,
    "scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware": 400,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": 500,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
    "scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware": 560,
    "scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware": 580,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 590,
    "scrapy.downloadermiddlewares.redirect.RedirectMiddleware": 600,
    "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 700,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 750,
    "scrapy.downloadermiddlewares.stats.DownloaderStats": 850,
    "scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware": 900,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES: dict = {
#    f"{BOT_NAME}.middlewares.{BOT_NAME_UPPER}ProxyDownloaderMiddleware": 749,
#    "scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware": None,
}

f"-----------------ProxyDownloaderMiddleware------------------"
# VZLJOT_PROXY = 'http://login:password@proxy:3128'



"-----------------CookiesMiddleware------------------"
# scrapy.downloadermiddlewares.cookies.CookiesMiddleware
# Disable cookies (enabled by default)
# Default: True. 
COOKIES_ENABLED = True
# Default: False. log all cookies sent in requests (i.e. Cookie header) 
# and all cookies received in responses (i.e. Set-Cookie header).
COOKIES_DEBUG = True

"-----------------DefaultHeadersMiddleware------------"
# scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware
#default headers
# {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }
# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     "Accept": "application/json, text/plain, */*",
#     "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
#     "Accept-Encoding": "gzip, deflate, br",
#     "organizationId": "null",
#     "branchId": "null",
#     "Connection": "keep-alive",
#     "Referer": "https://torgi.gov.ru/new/public/lots/reg",
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "same-origin"
# }
"-------------DownloadTimeoutMiddleware---------------"
# scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware
# Default: 180 
# The amount of time (in secs) that the downloader will wait before timing out.
DOWNLOAD_TIMEOUT = 180


"-------------HttpAuthMiddleware---------------------"
# scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False


"-----------------HttpCacheMiddleware----------------"
# scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware
# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# Default: False
HTTPCACHE_ENABLED = True
# Default: 0 Expiration time for cached requests, in seconds.
# Cached requests older than this time will be re-downloaded. 
# If zero, cached requests will never expire.
HTTPCACHE_EXPIRATION_SECS = 0
# Default: 'httpcache'
HTTPCACHE_DIR = "httpcache"
# Default: [] Don’t cache response with these HTTP codes.
HTTPCACHE_IGNORE_HTTP_CODES: list = []
# If enabled, requests not found in the cache will be ignored instead of downloaded.
# Default: False
HTTPCACHE_IGNORE_MISSING = False
# Don’t cache responses with these URI schemes. Default: ['file']
# HTTPCACHE_IGNORE_SCHEMES = []
# Default:
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"
# Default. The database module to use in the DBM storage backend. 
# This setting is specific to the DBM backend.
HTTPCACHE_DBM_MODULE = 'dbm'
# The class which implements the cache policy. Default
HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.DummyPolicy'
# If enabled, will compress all cached data with gzip. 
# This setting is specific to the Filesystem backend.
# Default: False
HTTPCACHE_GZIP  = True
# If enabled, will cache pages unconditionally. 
# Default: False
HTTPCACHE_ALWAYS_STORE = False
# List of Cache-Control directives in responses to be ignored.
# Default: []
HTTPCACHE_IGNORE_RESPONSE_CACHE_CONTROLS: list = []

"-----------------HttpCompressionMiddleware--------------"
# scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware
# Whether the Compression middleware will be enabled.
# This middleware allows compressed (gzip, deflate) traffic 
# to be sent/received from web sites.
# This middleware also supports decoding brotli-compressed 
# as well as zstd-compressed responses, provided that 
# brotli or zstandard is installed, respectively.
# Default: True
COMPRESSION_ENABLED = True

"-----------------HttpProxyMiddleware--------------"
# scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware
# Default: True
HTTPPROXY_ENABLED = True
# Default: "latin-1"
HTTPPROXY_AUTH_ENCODING = "latin-1"
# 

"-----------------RedirectMiddleware--------------"
# scrapy.downloadermiddlewares.redirect.RedirectMiddleware
# This middleware handles redirection of requests based on response status.
# Default: True
REDIRECT_ENABLED = True
# Default: 20
REDIRECT_MAX_TIMES = 20

"-----------------MetaRefreshMiddleware--------------"
# scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware
# This middleware handles redirection of requests based on meta-refresh html tag.
# Default: True
METAREFRESH_ENABLED = True
# Default: []
METAREFRESH_IGNORE_TAGS: list = []
# Default: 100
METAREFRESH_MAXDELAY = 100

"-----------------RetryMiddleware--------------"
# scrapy.downloadermiddlewares.retry.RetryMiddleware
# A middleware to retry failed requests that are potentially 
# caused by temporary problems such as a connection timeout 
# or HTTP 500 error.
# Default: True
RETRY_ENABLED = True
# Default: 2
RETRY_TIMES = 2
# Default: [500, 502, 503, 504, 522, 524, 408, 429]
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
# Default: all
RETRY_EXCEPTIONS_for_see = [
    'twisted.internet.defer.TimeoutError',
    'twisted.internet.error.TimeoutError',
    'twisted.internet.error.DNSLookupError',
    'twisted.internet.error.ConnectionRefusedError',
    'twisted.internet.error.ConnectionDone',
    'twisted.internet.error.ConnectError',
    'twisted.internet.error.ConnectionLost',
    'twisted.internet.error.TCPTimedOutError',
    'twisted.web.client.ResponseFailed',
    IOError,
    'scrapy.core.downloader.handlers.http11.TunnelError',
]
# Adjust retry request priority relative to original request:
# a positive priority adjust means higher priority.
# a negative priority adjust (default) means lower priority.
# Default: -1
RETRY_PRIORITY_ADJUST = -1
# 

"-----------------RobotsTxtMiddleware--------------"
# scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware
# This middleware filters out requests forbidden by the robots.txt exclusion standard.
# Obey robots.txt rules
ROBOTSTXT_OBEY = False


"-----------------DownloaderStats--------------"
# scrapy.downloadermiddlewares.stats.DownloaderStats
# Middleware that stores stats of all requests, responses 
# and exceptions that pass through it.
# Default: True
DOWNLOADER_STATS = True

"-----------------UserAgentMiddleware--------------"
# scrapy.downloadermiddlewares.useragent.UserAgentMiddleware
# Middleware that allows spiders to override the default user agent.
# Default
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = f"{BOT_NAME} (+http://www.yourdomain.com)"
# USER_AGENT =    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",

# USER_AGENTS_WIN = [
    
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# ]
# USER_AGENTS_LIN = [
#     "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36",
# ]
# USER_AGENTS_MAC = [
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
#     "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
# ]

"-----------------AjaxCrawlMiddleware--------------"
# scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware
# Middleware that finds ‘AJAX crawlable’ page variants based on meta-fragment html tag.
# Default: False
AJAXCRAWL_ENABLED = False

"================ Spider Middleware ==================="
# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# Default: {}
# SPIDER_MIDDLEWARES = {
#    f"{BOT_NAME}.middlewares.{BOT_NAME_UPPER}SpiderMiddleware": 543,
# }

SPIDER_MIDDLEWARES_BASE_for_see = {
    "scrapy.spidermiddlewares.httperror.HttpErrorMiddleware": 50,
    "scrapy.spidermiddlewares.offsite.OffsiteMiddleware": 500,
    "scrapy.spidermiddlewares.referer.RefererMiddleware": 700,
    "scrapy.spidermiddlewares.urllength.UrlLengthMiddleware": 800,
    "scrapy.spidermiddlewares.depth.DepthMiddleware": 900,
}

"-----------------DepthMiddleware--------------"
# scrapy.spidermiddlewares.depth.DepthMiddlewar
# The maximum depth that will be allowed to crawl for any site. 
# If zero, no limit will be imposed.
# Default: 0
DEPTH_LIMIT = 0
# An integer that is used to adjust the priority of a Request based on its depth.
# Default: 0
DEPTH_PRIORITY = 0
# Whether to collect verbose depth stats. If this is enabled, the number of requests 
# for each depth is collected in the stats.
# Default: False
DEPTH_STATS_VERBOSE = False

"-----------------HttpErrorMiddleware--------------"
# Filter out unsuccessful (erroneous) HTTP responses so that spiders don’t 
# have to deal with them, which (most of the time) imposes an overhead, 
# consumes more resources, and makes the spider logic more complex. 
# According to the HTTP standard, successful responses are those whose 
# status codes are in the 200-300 range.
# Pass all responses with non-200 status codes contained in this list.
# Default: []
HTTPERROR_ALLOWED_CODES: list = []
# Pass all responses, regardless of its status code.
# Default: False
HTTPERROR_ALLOW_ALL = False

"-----------------OffsiteMiddleware--------------"
# Filters out Requests for URLs outside the domains covered by the spider.
# This middleware filters out every request whose host names aren’t in 
# the spider’s allowed_domains attribute
# If the spider doesn’t define an allowed_domains attribute, or the attribute is empty, 
# the offsite middleware will allow all requests.
# If the request has the dont_filter attribute set, the offsite middleware 
# will allow the request even if its domain is not listed in allowed domains.

"-----------------RefererMiddleware--------------"
# Populates Request Referer header, based on the URL of the Response which generated it.
# Whether to enable referer middleware.
# Default: True
REFERER_ENABLED = True
# Referrer Policy to apply when populating Request “Referer” header.
# Default: 'scrapy.spidermiddlewares.referer.DefaultReferrerPolicy'
REFERRER_POLICY = 'scrapy.spidermiddlewares.referer.DefaultReferrerPolicy'

"-----------------UrlLengthMiddleware--------------"
# Filters out requests with URLs longer than URLLENGTH_LIMIT
# Default: 2083
URLLENGTH_LIMIT = 2083




"================ EXTENSIONS ==================="
# Typically, extensions connect to signals and perform tasks triggered by them.

EXTENSIONS_BASE_for_see = {
    "scrapy.extensions.corestats.CoreStats": 0,
    "scrapy.extensions.telnet.TelnetConsole": 0,
    "scrapy.extensions.memusage.MemoryUsage": 0,
    "scrapy.extensions.memdebug.MemoryDebugger": 0,
    "scrapy.extensions.closespider.CloseSpider": 0,
    "scrapy.extensions.feedexport.FeedExporter": 0,
    "scrapy.extensions.logstats.LogStats": 0,
    "scrapy.extensions.spiderstate.SpiderState": 0,
    "scrapy.extensions.throttle.AutoThrottle": 0,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

"-----------------LogStats--------------"
# scrapy.extensions.logstats.LogStats
# Log basic stats like crawled pages and scraped items.

"-----------------CoreStats--------------"
# scrapy.extensions.corestats.CoreStats
# Enable the collection of core statistics, provided the stats collection is enabled

"-----------------TelnetConsole--------------"
# scrapy.extensions.telnet.TelnetConsole
# Provides a telnet console for getting into a Python interpreter inside the currently 
# running Scrapy process, which can be very useful for debugging.

"-----------------MemoryUsage--------------"
# scrapy.extensions.memusage.MemoryUsage
# Monitors the memory used by the Scrapy process that runs the spider and:
# sends a notification e-mail when it exceeds a certain value
# closes the spider when it exceeds a certain value
# This extension is enabled by the MEMUSAGE_ENABLED setting and can be configured with the following settings:
# MEMUSAGE_LIMIT_MB
# MEMUSAGE_WARNING_MB
# MEMUSAGE_NOTIFY_MAIL
# MEMUSAGE_CHECK_INTERVAL_SECONDS


"-----------------MemoryDebugger--------------"
# scrapy.extensions.memdebug.MemoryDebugger
# An extension for debugging memory usage. It collects information about:
# objects uncollected by the Python garbage collector
# objects left alive that shouldn’t. For more info, see Debugging memory leaks with trackref
# To enable this extension, turn on the MEMDEBUG_ENABLED setting. The info will be stored in the stats.

"-----------------CloseSpider--------------"
# scrapy.extensions.closespider.CloseSpider
# Closes a spider automatically when some conditions are met, using a specific closing reason for each condition.
# The conditions for closing a spider can be configured through the following settings:
# CLOSESPIDER_TIMEOUT
# CLOSESPIDER_TIMEOUT_NO_ITEM
# CLOSESPIDER_ITEMCOUNT
# CLOSESPIDER_PAGECOUNT
# CLOSESPIDER_ERRORCOUNT


"-----------------StatsMailer--------------"
# scrapy.extensions.statsmailer.StatsMailer
# This simple extension can be used to send a notification e-mail every 
# time a domain has finished scraping, including the Scrapy stats collected. 
# The email will be sent to all recipients specified in the STATSMAILER_RCPTS setting.
# Emails can be sent using the MailSender class. To see a full list of parameters, 
# including examples on how to instantiate MailSender and use mail settings, 
# see Sending e-mail.

"-----------------PeriodicLog--------------"
# scrapy.extensions.periodic_log.PeriodicLog
# This extension periodically logs rich stat data as a JSON object:

"-----------------StackTraceDump--------------"
# scrapy.extensions.periodic_log.StackTraceDump
# Dumps information about the running process when a SIGQUIT or 
# SIGUSR2 signal is received. The information dumped is the following:





"================ ITEM_PIPELINE ==================="
# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES: dict = {
#    f"{BOT_NAME}.pipelines.{BOT_NAME_UPPER}CleanValuePipeline": 300,
#    f"{BOT_NAME}.pipelines.{BOT_NAME_UPPER}AbsolutUrlsPeipeline": 301,
#    f"{BOT_NAME}.pipelines.{BOT_NAME_UPPER}RemoveNotUsedPeipeline": 302,   
}



# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

"================ Feed exports ==================="
# Scrapy generates multiple output files storing up 
# to the specified number of items in each output file.
# dirname/%(batch_id)d-filename%(batch_time)s.json"
# Default: 0
# FEED_EXPORT_BATCH_ITEM_COUNT = 100

# "%(spider_name)s.jsonl"

FEEDS: dict = {
    # f'feed/{util.get_curent_date_time()}.items.json': {
    #     'format': 'json',
    #     'encoding': 'utf8',
    #     'store_empty': False,
    #     # 'item_classes': [f'{BOT_NAME}.items.TorgiGovRuItem',], # [MyItemClass1, 'myproject.items.MyItemClass2'],
    #     'fields': None,
    #     'indent': 4,
    #     'item_export_kwargs': {
    #        'export_empty_fields': True,
    #     },
    #     'overwrite': True, 
    # },
    # f'feed/{BOT_NAME}.items.xml': {
    #     'format': 'xml',
    #     # 'fields': ['reg_num', 'reg_num_href'],
    #     # 'item_filter': MyCustomFilter1,
    #     'encoding': 'utf8',
    #     'indent': 8,
    #     'overwrite': True, 
    # },
    # pathlib.Path(f'feed/{BOT_NAME}.items.csv.gz'): {
    #     'format': 'csv',
    #     # 'fields': ['date', 'p_object'],
    #     # 'item_filter': 'myproject.filters.MyCustomFilter2',
    #     # 'postprocessing': [MyPlugin1, 'scrapy.extensions.postprocessing.GzipPlugin'],
    #     # 'gzip_compresslevel': 5,
    #     'overwrite': True, 
    # },
    # 'stdout': None,
}

FEED_STORAGES_BASE_for_see = {
    "": "scrapy.extensions.feedexport.FileFeedStorage",
    "file": "scrapy.extensions.feedexport.FileFeedStorage",
    "stdout": "scrapy.extensions.feedexport.StdoutFeedStorage",
    "s3": "scrapy.extensions.feedexport.S3FeedStorage",
    "ftp": "scrapy.extensions.feedexport.FTPFeedStorage",
}

FEED_STORAGES = {
    "ftp": None,
    "stdout": None
}

FEED_EXPORTERS_BASE_for_see = {
    "json": "scrapy.exporters.JsonItemExporter",
    "jsonlines": "scrapy.exporters.JsonLinesItemExporter",
    "jsonl": "scrapy.exporters.JsonLinesItemExporter",
    "jl": "scrapy.exporters.JsonLinesItemExporter",
    "csv": "scrapy.exporters.CsvItemExporter",
    "xml": "scrapy.exporters.XmlItemExporter",
    "marshal": "scrapy.exporters.MarshalItemExporter",
    "pickle": "scrapy.exporters.PickleItemExporter",
}
# to disable the built-in exporter (without replacement)
FEED_EXPORTERS = {
    "pickle": None,
}

"================ Logging ==================="
# logging.CRITICAL - for critical errors (highest severity)
# logging.ERROR - for regular errors
# logging.WARNING - for warning messages
# logging.INFO - for informational messages
# logging.DEBUG - for debugging messages (lowest severity)
# logging.warning("This is a warning")
# logger = logging.getLogger()
# logger = logging.getLogger("mycustomlogger")
# logger = logging.getLogger(__name__)

# LOG_FILE = f"logs/{BOT_NAME}_{util.get_curent_date_time()}.log"
# False, the file will be overwritten (discarding the 
# output from previous runs, if any)
# LOG_FILE_APPEND = True
# LOG_ENABLED is True, log messages will be displayed 
# on the standard error
LOG_ENABLED = True
# Default: 'utf-8'
LOG_ENCODING = 'utf-8'
# determines the minimum level of severity to display,
# Default: 'DEBUG'
LOG_LEVEL = 'DEBUG'
# LOG_LEVEL = 'INFO'
# Default: '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
# Default: '%Y-%m-%d %H:%M:%S'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
# If True, all standard output (and error) of 
# your process will be redirected to the log. 
# For example if you print('hello') it will appear 
# in the Scrapy log.
# Default: False
LOG_STDOUT = True
# If True, the logs will just contain the root path. 
# If it is set to False then it displays the component responsible for the log output
# Default: False
LOG_SHORT_NAMES = False