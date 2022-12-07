from asyncio import get_event_loop
from faulthandler import enable as faulthandler_enable
from logging import INFO, FileHandler, StreamHandler, basicConfig
from logging import error as log_error
from logging import getLogger
from logging import info as log_info
from logging import warning as log_warning
from os import environ
from os import path as ospath
from os import remove as osremove
from socket import setdefaulttimeout
from subprocess import Popen
from subprocess import run as srun
from threading import Lock, Thread
from time import sleep, time

from aria2p import API as ariaAPI
from aria2p import Client as ariaClient
from dotenv import load_dotenv
from pymongo import MongoClient
from pyrogram import Client, enums
from qbittorrentapi import Client as qbClient
from telegram.ext import Updater as tgUpdater

main_loop = get_event_loop()

faulthandler_enable()

setdefaulttimeout(600)

botStartTime = time()

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[FileHandler('log.txt'), StreamHandler()],
            level=INFO)

LOGGER = getLogger(__name__)

load_dotenv('config.env', override=True)

Interval = []
QbInterval = []
DRIVES_NAMES = []
DRIVES_IDS = []
INDEX_URLS = []
CATEGORY_NAMES = []
CATEGORY_IDS = []
SHORTENERES = []
SHORTENER_APIS = []
BUTTON_NAMES = []
BUTTON_URLS = []
CATEGORY_INDEXS = []
GLOBAL_EXTENSION_FILTER = ['.aria2']
user_data = {}
aria2_options = {}
qbit_options = {}

try:
    if bool(environ.get('_____REMOVE_THIS_LINE_____')):
        log_error('The README.md file there to be read! Exiting now!')
        exit()
except:
    pass

download_dict_lock = Lock()
status_reply_dict_lock = Lock()
# Key: update.effective_chat.id
# Value: telegram.Message
status_reply_dict = {}
# Key: update.message.message_id
# Value: An object of Status
download_dict = {}
# key: rss_title
# value: {link, last_feed, last_title, filter}
rss_dict = {}
# key: msg_id
# value: [listener, extras, isNeedEngine, time_out]
btn_listener = {}

BOT_TOKEN = environ.get('BOT_TOKEN', '')
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

bot_id = int(BOT_TOKEN.split(':', 1)[0])

DATABASE_URL = environ.get('DATABASE_URL', '')
if len(DATABASE_URL) == 0:
    DATABASE_URL = ''

if DATABASE_URL:
    conn = MongoClient(DATABASE_URL)
    db = conn.mltb
    # retrun config dict (all env vars)
    if config_dict := db.settings.config.find_one({'_id': bot_id}):
        del config_dict['_id']
        for key, value in config_dict.items():
            environ[key] = str(value)
    if pf_dict := db.settings.files.find_one({'_id': bot_id}):
        del pf_dict['_id']
        for key, value in pf_dict.items():
            if value:
                file_ = key.replace('__', '.')
                with open(file_, 'wb+') as f:
                    f.write(value)
    if a2c_options := db.settings.aria2c.find_one({'_id': bot_id}):
        del a2c_options['_id']
        aria2_options = a2c_options
    if qbit_opt := db.settings.qbittorrent.find_one({'_id': bot_id}):
        del qbit_opt['_id']
        qbit_options = qbit_opt
    BOT_TOKEN = environ.get('BOT_TOKEN', '')
    bot_id = int(BOT_TOKEN.split(':', 1)[0])
    DATABASE_URL = environ.get('DATABASE_URL', '')
    conn.close()
else:
    config_dict = {}

OWNER_ID = environ.get('OWNER_ID', '')
if len(OWNER_ID) == 0:
    log_error("OWNER_ID variable is missing! Exiting now")
    exit(1)
else:
    OWNER_ID = int(OWNER_ID)

TELEGRAM_API = environ.get('TELEGRAM_API', '')
if len(TELEGRAM_API) == 0:
    log_error("TELEGRAM_API variable is missing! Exiting now")
    exit(1)
else:
    TELEGRAM_API = int(TELEGRAM_API)

TELEGRAM_HASH = environ.get('TELEGRAM_HASH', '')
if len(TELEGRAM_HASH) == 0:
    log_error("TELEGRAM_HASH variable is missing! Exiting now")
    exit(1)

GDRIVE_ID = environ.get('GDRIVE_ID', '')
if len(GDRIVE_ID) == 0:
    log_warning('GDRIVE_ID not provided!')
    GDRIVE_ID = ''

DOWNLOAD_DIR = environ.get('DOWNLOAD_DIR', '')
if len(DOWNLOAD_DIR) == 0:
    DOWNLOAD_DIR = '/usr/src/app/downloads/'
elif not DOWNLOAD_DIR.endswith("/"):
    DOWNLOAD_DIR = f'{DOWNLOAD_DIR}/'

AUTHORIZED_CHATS = environ.get('AUTHORIZED_CHATS', '')
if len(AUTHORIZED_CHATS) != 0:
    aid = AUTHORIZED_CHATS.split()
    for id_ in aid:
        user_data[int(id_.strip())] = {'is_auth': True}

SUDO_USERS = environ.get('SUDO_USERS', '')
if len(SUDO_USERS) != 0:
    aid = SUDO_USERS.split()
    for id_ in aid:
        user_data[int(id_.strip())] = {'is_sudo': True}

EXTENSION_FILTER = environ.get('EXTENSION_FILTER', '')
if len(EXTENSION_FILTER) > 0:
    fx = EXTENSION_FILTER.split()
    for x in fx:
        GLOBAL_EXTENSION_FILTER.append(x.strip().lower())

IS_PREMIUM_USER = False
IS_USER_SESSION = False
USER_SESSION_STRING = environ.get('USER_SESSION_STRING', '')
if len(USER_SESSION_STRING) == 0:
    log_info("Creating client from BOT_TOKEN")
    app = Client(name='pyrogram', api_id=TELEGRAM_API, api_hash=TELEGRAM_HASH,
                 bot_token=BOT_TOKEN, parse_mode=enums.ParseMode.HTML, no_updates=True)
else:
    log_info("Creating client from USER_SESSION_STRING")
    app = Client(name='pyrogram', api_id=TELEGRAM_API, api_hash=TELEGRAM_HASH,
                 session_string=USER_SESSION_STRING, parse_mode=enums.ParseMode.HTML, no_updates=True)
    with app:
        IS_PREMIUM_USER = app.me.is_premium
    IS_USER_SESSION = True

RSS_USER_SESSION_STRING = environ.get('RSS_USER_SESSION_STRING', '')
if len(RSS_USER_SESSION_STRING) == 0:
    rss_session = ''
else:
    log_info("Creating client from RSS_USER_SESSION_STRING")
    rss_session = Client(name='rss_session', api_id=TELEGRAM_API, api_hash=TELEGRAM_HASH,
                         session_string=RSS_USER_SESSION_STRING, parse_mode=enums.ParseMode.HTML, no_updates=True)

MEGA_API_KEY = environ.get('MEGA_API_KEY', '')
if len(MEGA_API_KEY) == 0:
    log_warning('MEGA API KEY not provided!')
    MEGA_API_KEY = ''

MEGA_EMAIL_ID = environ.get('MEGA_EMAIL_ID', '')
MEGA_PASSWORD = environ.get('MEGA_PASSWORD', '')
if len(MEGA_EMAIL_ID) == 0 or len(MEGA_PASSWORD) == 0:
    log_warning('MEGA Credentials not provided!')
    MEGA_EMAIL_ID = ''
    MEGA_PASSWORD = ''

UPTOBOX_TOKEN = environ.get('UPTOBOX_TOKEN', '')
if len(UPTOBOX_TOKEN) == 0:
    UPTOBOX_TOKEN = ''

INDEX_URL = environ.get('INDEX_URL', '').rstrip("/")
if len(INDEX_URL) == 0:
    INDEX_URL = ''

SEARCH_API_LINK = environ.get('SEARCH_API_LINK', '').rstrip("/")
if len(SEARCH_API_LINK) == 0:
    SEARCH_API_LINK = ''

RSS_COMMAND = environ.get('RSS_COMMAND', '')
if len(RSS_COMMAND) == 0:
    RSS_COMMAND = ''

LEECH_FILENAME_PERFIX = environ.get('LEECH_FILENAME_PERFIX', '')
if len(LEECH_FILENAME_PERFIX) == 0:
    LEECH_FILENAME_PERFIX = ''

SEARCH_PLUGINS = environ.get('SEARCH_PLUGINS', '')
if len(SEARCH_PLUGINS) == 0:
    SEARCH_PLUGINS = ''

MAX_SPLIT_SIZE = 4194304000 if IS_PREMIUM_USER else 2097152000

LEECH_SPLIT_SIZE = environ.get('LEECH_SPLIT_SIZE', '')
if len(LEECH_SPLIT_SIZE) == 0 or int(LEECH_SPLIT_SIZE) > MAX_SPLIT_SIZE:
    LEECH_SPLIT_SIZE = MAX_SPLIT_SIZE
else:
    LEECH_SPLIT_SIZE = int(LEECH_SPLIT_SIZE)

DOWNLOAD_STATUS_UPDATE_INTERVAL = environ.get('STATUS_UPDATE_INTERVAL', '')
if len(DOWNLOAD_STATUS_UPDATE_INTERVAL) == 0:
    DOWNLOAD_STATUS_UPDATE_INTERVAL = 10
else:
    DOWNLOAD_STATUS_UPDATE_INTERVAL = int(DOWNLOAD_STATUS_UPDATE_INTERVAL)

AUTO_DELETE_MESSAGE_DURATION = environ.get('AUTO_DELETE_MESSAGE_DURATION', '')
if len(AUTO_DELETE_MESSAGE_DURATION) == 0:
    AUTO_DELETE_MESSAGE_DURATION = 30
else:
    AUTO_DELETE_MESSAGE_DURATION = int(AUTO_DELETE_MESSAGE_DURATION)

YT_DLP_QUALITY = environ.get('YT_DLP_QUALITY', '')
if len(YT_DLP_QUALITY) == 0:
    YT_DLP_QUALITY = ''

SEARCH_LIMIT = environ.get('SEARCH_LIMIT', '')
SEARCH_LIMIT = 0 if len(SEARCH_LIMIT) == 0 else int(SEARCH_LIMIT)

DUMP_CHAT = environ.get('DUMP_CHAT', '')
DUMP_CHAT = '' if len(DUMP_CHAT) == 0 else int(DUMP_CHAT)

STATUS_LIMIT = environ.get('STATUS_LIMIT', '')
STATUS_LIMIT = '' if len(STATUS_LIMIT) == 0 else int(STATUS_LIMIT)

CMD_PERFIX = environ.get('CMD_PERFIX', '')

RSS_CHAT_ID = environ.get('RSS_CHAT_ID', '')
RSS_CHAT_ID = '' if len(RSS_CHAT_ID) == 0 else int(RSS_CHAT_ID)

RSS_DELAY = environ.get('RSS_DELAY', '')
RSS_DELAY = 900 if len(RSS_DELAY) == 0 else int(RSS_DELAY)

TORRENT_TIMEOUT = environ.get('TORRENT_TIMEOUT', '')
TORRENT_TIMEOUT = '' if len(TORRENT_TIMEOUT) == 0 else int(TORRENT_TIMEOUT)

INCOMPLETE_TASK_NOTIFIER = environ.get('INCOMPLETE_TASK_NOTIFIER', '')
INCOMPLETE_TASK_NOTIFIER = INCOMPLETE_TASK_NOTIFIER.lower() == 'true'

STOP_DUPLICATE = environ.get('STOP_DUPLICATE', '')
STOP_DUPLICATE = STOP_DUPLICATE.lower() == 'true'

VIEW_LINK = environ.get('VIEW_LINK', '')
VIEW_LINK = VIEW_LINK.lower() == 'true'

IS_TEAM_DRIVE = environ.get('IS_TEAM_DRIVE', '')
IS_TEAM_DRIVE = IS_TEAM_DRIVE.lower() == 'true'

USE_SERVICE_ACCOUNTS = environ.get('USE_SERVICE_ACCOUNTS', '')
USE_SERVICE_ACCOUNTS = USE_SERVICE_ACCOUNTS.lower() == 'true'

WEB_PINCODE = environ.get('WEB_PINCODE', '')
WEB_PINCODE = WEB_PINCODE.lower() == 'true'

IGNORE_PENDING_REQUESTS = environ.get('IGNORE_PENDING_REQUESTS', '')
IGNORE_PENDING_REQUESTS = IGNORE_PENDING_REQUESTS.lower() == 'true'

AS_DOCUMENT = environ.get('AS_DOCUMENT', '')
AS_DOCUMENT = AS_DOCUMENT.lower() == 'true'

EQUAL_SPLITS = environ.get('EQUAL_SPLITS', '')
EQUAL_SPLITS = EQUAL_SPLITS.lower() == 'true'

SERVER_PORT = environ.get('SERVER_PORT', '')
if len(SERVER_PORT) == 0:
    SERVER_PORT = 80
else:
    SERVER_PORT = int(SERVER_PORT)

BASE_URL = environ.get('BASE_URL', '').rstrip("/")
if len(BASE_URL) == 0:
    log_warning('BASE_URL not provided!')
    BASE_URL = ''

UPSTREAM_REPO = environ.get('UPSTREAM_REPO', '')
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = ''

UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', '')
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = 'master'

STORAGE_THRESHOLD = environ.get('STORAGE_THRESHOLD', '')
STORAGE_THRESHOLD = '' if len(STORAGE_THRESHOLD) == 0 else float(STORAGE_THRESHOLD)

TORRENT_LIMIT = environ.get('TORRENT_LIMIT', '')
TORRENT_LIMIT = '' if len(TORRENT_LIMIT) == 0 else float(TORRENT_LIMIT)

DIRECT_LIMIT = environ.get('DIRECT_LIMIT', '')
DIRECT_LIMIT = '' if len(DIRECT_LIMIT) == 0 else float(DIRECT_LIMIT)

YTDLP_LIMIT = environ.get('YTDLP_LIMIT', '')
YTDLP_LIMIT = '' if len(YTDLP_LIMIT) == 0 else float(YTDLP_LIMIT)

GDRIVE_LIMIT = environ.get('GDRIVE_LIMIT', '')
GDRIVE_LIMIT = '' if len(GDRIVE_LIMIT) == 0 else float(GDRIVE_LIMIT)

CLONE_LIMIT = environ.get('CLONE_LIMIT', '')
CLONE_LIMIT = '' if len(CLONE_LIMIT) == 0 else float(CLONE_LIMIT)

MEGA_LIMIT = environ.get('MEGA_LIMIT', '')
MEGA_LIMIT = '' if len(MEGA_LIMIT) == 0 else float(MEGA_LIMIT)

LEECH_LIMIT = environ.get('LEECH_LIMIT', '')
LEECH_LIMIT = '' if len(LEECH_LIMIT) == 0 else float(LEECH_LIMIT)

MAX_PLAYLIST = environ.get('MAX_PLAYLIST', '')
MAX_PLAYLIST = '' if len(MAX_PLAYLIST) == 0 else int(MAX_PLAYLIST)

GDTOT_CRYPT = environ.get('GDTOT_CRYPT', '')
if len(GDTOT_CRYPT) == 0:
    GDTOT_CRYPT = ''

ENABLE_CHAT_RESTRICT = environ.get('ENABLE_CHAT_RESTRICT', '')
ENABLE_CHAT_RESTRICT = ENABLE_CHAT_RESTRICT.lower() == 'true'

ENABLE_MESSAGE_FILTER = environ.get('ENABLE_MESSAGE_FILTER', '')
ENABLE_MESSAGE_FILTER = ENABLE_MESSAGE_FILTER.lower() == 'true'

STOP_DUPLICATE_TASKS = environ.get('STOP_DUPLICATE_TASKS', '')
STOP_DUPLICATE_TASKS = STOP_DUPLICATE_TASKS.lower() == 'true'

SHARER_EMAIL = environ.get('SHARER_EMAIL', '')
SHARER_PASS = environ.get('SHARER_PASS', '')
if len(SHARER_EMAIL) == 0 or len(SHARER_PASS) == 0:
    SHARER_EMAIL = ''
    SHARER_PASS = ''

SHARER_DRIVE_SITE = environ.get('SHARER_DRIVE_SITE', '').rstrip("/")
if len(SHARER_DRIVE_SITE) == 0:
    SHARER_DRIVE_SITE = ''

ENABLE_SHARER_LIST = environ.get('ENABLE_SHARER_LIST', '')
ENABLE_SHARER_LIST = ENABLE_SHARER_LIST.lower() == 'true'

DISABLE_DRIVE_LINK = environ.get('DISABLE_DRIVE_LINK', '')
DISABLE_DRIVE_LINK = DISABLE_DRIVE_LINK.lower() == 'true'

DISABLE_LEECH = environ.get('DISABLE_LEECH', '')
DISABLE_LEECH = DISABLE_LEECH.lower() == 'true'

SET_COMMANDS = environ.get('SET_COMMANDS', '')
SET_COMMANDS = SET_COMMANDS.lower() == 'true'

ENABLE_DM = environ.get('ENABLE_DM', '')
ENABLE_DM = ENABLE_DM.lower() == 'true'

DELETE_LINKS = environ.get('DELETE_LINKS', '')
DELETE_LINKS = DELETE_LINKS.lower() == 'true'

MIRROR_LOG = environ.get('MIRROR_LOG', '')
if len(MIRROR_LOG) != 0 and not MIRROR_LOG.startswith('-100') or len(MIRROR_LOG) == 0:
    MIRROR_LOG = ''
else:
    MIRROR_LOG = int(MIRROR_LOG)

BUTTON_TIMEOUT = environ.get('BUTTON_TIMEOUT', '')
BUTTON_TIMEOUT = 30 if len(BUTTON_TIMEOUT) == 0 else int(BUTTON_TIMEOUT)

fsubid = environ.get('FSUB_IDS', '')
FSUB_IDS = {int(_id.strip()) for _id in fsubid.split()} if len(fsubid) != 0 else set()

config_dict = {'AS_DOCUMENT': AS_DOCUMENT,
                'AUTHORIZED_CHATS': AUTHORIZED_CHATS,
                'AUTO_DELETE_MESSAGE_DURATION': AUTO_DELETE_MESSAGE_DURATION,
                'BASE_URL': BASE_URL,
                'BOT_TOKEN': BOT_TOKEN,
                'CMD_PERFIX': CMD_PERFIX,
                'DATABASE_URL': DATABASE_URL,
                'DOWNLOAD_DIR': DOWNLOAD_DIR,
                'DUMP_CHAT': DUMP_CHAT,
                'EQUAL_SPLITS': EQUAL_SPLITS,
                'EXTENSION_FILTER': EXTENSION_FILTER,
                'GDRIVE_ID': GDRIVE_ID,
                'IGNORE_PENDING_REQUESTS': IGNORE_PENDING_REQUESTS,
                'INCOMPLETE_TASK_NOTIFIER': INCOMPLETE_TASK_NOTIFIER,
                'INDEX_URL': INDEX_URL,
                'IS_TEAM_DRIVE': IS_TEAM_DRIVE,
                'LEECH_FILENAME_PERFIX': LEECH_FILENAME_PERFIX,
                'LEECH_SPLIT_SIZE': LEECH_SPLIT_SIZE,
                'MEGA_API_KEY': MEGA_API_KEY,
                'MEGA_EMAIL_ID': MEGA_EMAIL_ID,
                'MEGA_PASSWORD': MEGA_PASSWORD,
                'OWNER_ID': OWNER_ID,
                'RSS_USER_SESSION_STRING': RSS_USER_SESSION_STRING,
                'RSS_CHAT_ID': RSS_CHAT_ID,
                'RSS_COMMAND': RSS_COMMAND,
                'RSS_DELAY': RSS_DELAY,
                'SEARCH_API_LINK': SEARCH_API_LINK,
                'SEARCH_LIMIT': SEARCH_LIMIT,
                'SEARCH_PLUGINS': SEARCH_PLUGINS,
                'SERVER_PORT': SERVER_PORT,
                'STATUS_LIMIT': STATUS_LIMIT,
                'DOWNLOAD_STATUS_UPDATE_INTERVAL': DOWNLOAD_STATUS_UPDATE_INTERVAL,
                'STOP_DUPLICATE': STOP_DUPLICATE,
                'SUDO_USERS': SUDO_USERS,
                'TELEGRAM_API': TELEGRAM_API,
                'TELEGRAM_HASH': TELEGRAM_HASH,
                'TORRENT_TIMEOUT': TORRENT_TIMEOUT,
                'UPSTREAM_REPO': UPSTREAM_REPO,
                'UPSTREAM_BRANCH': UPSTREAM_BRANCH,
                'UPTOBOX_TOKEN': UPTOBOX_TOKEN,
                'USER_SESSION_STRING': USER_SESSION_STRING,
                'USE_SERVICE_ACCOUNTS': USE_SERVICE_ACCOUNTS,
                'VIEW_LINK': VIEW_LINK,
                'WEB_PINCODE': WEB_PINCODE,
                'YT_DLP_QUALITY': YT_DLP_QUALITY,
                'STORAGE_THRESHOLD': STORAGE_THRESHOLD,
                'TORRENT_LIMIT': TORRENT_LIMIT,
                'DIRECT_LIMIT': DIRECT_LIMIT,
                'YTDLP_LIMIT': YTDLP_LIMIT,
                'GDRIVE_LIMIT': GDRIVE_LIMIT,
                'CLONE_LIMIT': CLONE_LIMIT,
                'MEGA_LIMIT': MEGA_LIMIT,
                'LEECH_LIMIT': LEECH_LIMIT,
                'MAX_PLAYLIST': MAX_PLAYLIST,
                'GDTOT_CRYPT': GDTOT_CRYPT,
                'ENABLE_CHAT_RESTRICT': ENABLE_CHAT_RESTRICT,
                'ENABLE_MESSAGE_FILTER': ENABLE_MESSAGE_FILTER,
                'STOP_DUPLICATE_TASKS': STOP_DUPLICATE_TASKS,
                'SHARER_DRIVE_SITE': SHARER_DRIVE_SITE,
                'ENABLE_SHARER_LIST': ENABLE_SHARER_LIST,
                'DISABLE_DRIVE_LINK': DISABLE_DRIVE_LINK,
                'SET_COMMANDS': SET_COMMANDS,
                'MIRROR_LOG': MIRROR_LOG,
                'SHARER_EMAIL': SHARER_EMAIL,
                'SHARER_PASS': SHARER_PASS,
                'DISABLE_LEECH': DISABLE_LEECH,
                'ENABLE_DM': ENABLE_DM,
                'DELETE_LINKS': DELETE_LINKS,
                'BUTTON_TIMEOUT': BUTTON_TIMEOUT}

if GDRIVE_ID:
    DRIVES_NAMES.append("Main")
    DRIVES_IDS.append(GDRIVE_ID)
    INDEX_URLS.append(INDEX_URL)

if ospath.exists('list_drives.txt'):
    with open('list_drives.txt', 'r+') as f:
        lines = f.readlines()
        for line in lines:
            temp = line.strip().split()
            DRIVES_IDS.append(temp[1])
            DRIVES_NAMES.append(temp[0].replace("_", " "))
            if len(temp) > 2:
                INDEX_URLS.append(temp[2])
            else:
                INDEX_URLS.append('')

if ospath.exists('buttons.txt'):
    with open('buttons.txt', 'r+') as f:
        lines = f.readlines()
        for line in lines:
            temp = line.strip().split()
            if len(BUTTON_NAMES) == 4:
                break
            if len(temp) == 2:
                BUTTON_NAMES.append(temp[0].replace("_", " "))
                BUTTON_URLS.append(temp[1])

if ospath.exists('shorteners.txt'):
    with open('shorteners.txt', 'r+') as f:
        lines = f.readlines()
        for line in lines:
            temp = line.strip().split()
            if len(temp) == 2:
                SHORTENERES.append(temp[0])
                SHORTENER_APIS.append(temp[1])

if GDRIVE_ID:
    CATEGORY_NAMES.append("Root")
    CATEGORY_IDS.append(GDRIVE_ID)
    CATEGORY_INDEXS.append(INDEX_URL)

if ospath.exists('categories.txt'):
    with open('categories.txt', 'r+') as f:
        lines = f.readlines()
        for line in lines:
            temp = line.strip().split()
            CATEGORY_IDS.append(temp[1])
            CATEGORY_NAMES.append(temp[0].replace("_", " "))
            if len(temp) > 2:
                CATEGORY_INDEXS.append(temp[2])
            else:
                CATEGORY_INDEXS.append('')

if BASE_URL:
    Popen(f"gunicorn web.wserver:app --bind 0.0.0.0:{SERVER_PORT}", shell=True)

srun(["qbittorrent-nox", "-d", "--profile=."])
if not ospath.exists('.netrc'):
    srun(["touch", ".netrc"])
srun(["cp", ".netrc", "/root/.netrc"])
srun(["chmod", "600", ".netrc"])
srun(["chmod", "+x", "aria.sh"])
srun("./aria.sh", shell=True)
if ospath.exists('accounts.zip'):
    if ospath.exists('accounts'):
        srun(["rm", "-rf", "accounts"])
    srun(["unzip", "-q", "-o", "accounts.zip", "-x", "accounts/emails.txt"])
    srun(["chmod", "-R", "777", "accounts"])
    osremove('accounts.zip')
if not ospath.exists('accounts'):
    config_dict['USE_SERVICE_ACCOUNTS'] = False
sleep(0.5)

aria2 = ariaAPI(ariaClient(host="http://localhost", port=6800, secret=""))


def get_client():
    return qbClient(host="localhost", port=8090, VERIFY_WEBUI_CERTIFICATE=False, REQUESTS_ARGS={'timeout': (30, 60)})


def aria2c_init():
    try:
        log_info("Initializing Aria2c")
        link = "https://linuxmint.com/torrents/lmde-5-cinnamon-64bit.iso.torrent"
        dire = DOWNLOAD_DIR.rstrip("/")
        aria2.add_uris([link], {'dir': dire})
        sleep(3)
        downloads = aria2.get_downloads()
        sleep(15)
        aria2.remove(downloads, force=True, files=True, clean=True)
    except Exception as e:
        log_error(f"Aria2c initializing error: {e}")

aria2c_global = ['bt-max-open-files', 'download-result', 'keep-unfinished-download-result', 'log', 'log-level',
                 'max-concurrent-downloads', 'max-download-result', 'max-overall-download-limit', 'save-session',
                 'max-overall-upload-limit', 'optimize-concurrent-downloads', 'save-cookies', 'server-stat-of']

if not aria2_options:
    aria2_options = aria2.client.get_global_option()
    del aria2_options['dir']
else:
    a2c_glo = {}
    for op in aria2c_global:
        if op in aria2_options:
            a2c_glo[op] = aria2_options[op]
    aria2.set_global_options(a2c_glo)

qb_client = get_client()
if not qbit_options:
    qbit_options = dict(qb_client.app_preferences())
    del qbit_options['listen_port']
    for k in list(qbit_options.keys()):
        if k.startswith('rss'):
            del qbit_options[k]
else:
    qb_opt = {**qbit_options}
    for k, v in list(qb_opt.items()):
        if v in ["", "*"]:
            del qb_opt[k]
    qb_client.app_set_preferences(qb_opt)

Thread(target=aria2c_init).start()
sleep(1.5)

updater = tgUpdater(token=BOT_TOKEN, request_kwargs={'read_timeout': 20, 'connect_timeout': 15})
bot = updater.bot
dispatcher = updater.dispatcher
job_queue = updater.job_queue
botname = bot.username
