# ruff: noqa: E402

try:
    from uvloop import install
    install()
except ImportError:
    pass

from subprocess import run as srun
from os import getcwd
from asyncio import Lock, new_event_loop, set_event_loop
from logging import (
    ERROR,
    INFO,
    WARNING,
    FileHandler,
    StreamHandler,
    basicConfig,
    getLogger,
)
from os import cpu_count
from time import time

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .core.config_manager import BinConfig
from sabnzbdapi import SabnzbdClient

getLogger("requests").setLevel(WARNING)
getLogger("urllib3").setLevel(WARNING)
getLogger("pyrogram").setLevel(ERROR)
getLogger("aiohttp").setLevel(ERROR)
getLogger("apscheduler").setLevel(ERROR)
getLogger("httpx").setLevel(WARNING)
getLogger("pymongo").setLevel(WARNING)
getLogger("aiohttp").setLevel(WARNING)


bot_start_time = time()

bot_loop = new_event_loop()
set_event_loop(bot_loop)

basicConfig(
    format="[%(asctime)s] [%(levelname)s] - %(message)s",  #  [%(filename)s:%(lineno)d]
    datefmt="%d-%b-%y %I:%M:%S %p",
    handlers=[FileHandler("log.txt"), StreamHandler()],
    level=INFO,
)

LOGGER = getLogger(__name__)
cpu_no = cpu_count()
threads = max(1, cpu_no // 2)
cores = ",".join(str(i) for i in range(threads))

bot_cache = {}
DOWNLOAD_DIR = "/usr/src/app/downloads/"
intervals = {"status": {}, "qb": "", "jd": "", "nzb": "", "stopAll": False}
qb_torrents = {}
jd_downloads = {}
nzb_jobs = {}
user_data = {}
aria2_options = {}
qbit_options = {}
nzb_options = {}
queued_dl = {}
queued_up = {}
status_dict = {}
task_dict = {}
rss_dict = {}
shortener_dict = {}
var_list = [
    "BOT_TOKEN",
    "TELEGRAM_API",
    "TELEGRAM_HASH",
    "OWNER_ID",
    "DATABASE_URL",
    "BASE_URL",
    "UPSTREAM_REPO",
    "UPSTREAM_BRANCH",
    "UPDATE_PKGS",
]
auth_chats = {}
excluded_extensions = ["aria2", "!qB"]
drives_names = []
drives_ids = []
index_urls = []
sudo_users = []
non_queued_dl = set()
non_queued_up = set()
multi_tags = set()
task_dict_lock = Lock()
queue_dict_lock = Lock()
qb_listener_lock = Lock()
nzb_listener_lock = Lock()
jd_listener_lock = Lock()
cpu_eater_lock = Lock()
same_directory_lock = Lock()

# Patch FreeBSD binaries in mysterysd base image to allow them to execute on Heroku Linux hosts
import os
import shutil
import subprocess

LOGGER.info("=== STARTING BINARY DIAGNOSTICS & PATCHING ===")
patched_bin_dir = "/usr/src/app/patched_bin"
try:
    os.makedirs(patched_bin_dir, exist_ok=True)
except Exception as e:
    LOGGER.warning("Failed to create patched_bin_dir: %s", e)

binary_mappings = {
    "ARIA2_NAME": BinConfig.ARIA2_NAME,
    "QBIT_NAME": BinConfig.QBIT_NAME,
    "SABNZBD_NAME": BinConfig.SABNZBD_NAME,
    "FFMPEG_NAME": BinConfig.FFMPEG_NAME,
    "RCLONE_NAME": BinConfig.RCLONE_NAME,
}

for config_attr, bin_name in binary_mappings.items():
    orig_path = None
    for dir_path in ["/usr/local/bin", "/usr/bin", "bin", "."]:
        p = os.path.join(dir_path, bin_name)
        if os.path.exists(p):
            orig_path = p
            break
            
    if not orig_path:
        LOGGER.warning("Binary %s NOT found in search paths.", bin_name)
        continue
        
    LOGGER.info("Found original binary %s at %s (Size: %d bytes)", bin_name, orig_path, os.path.getsize(orig_path))
    dest_path = os.path.join(patched_bin_dir, bin_name)
    
    try:
        # Copy to patched_bin
        shutil.copy2(orig_path, dest_path)
        LOGGER.info("Copied %s to local path %s", orig_path, dest_path)
        
        # Read header
        with open(dest_path, "rb") as f:
            header = f.read(16)
        LOGGER.info("Binary %s first 16 bytes: %s", dest_path, header.hex())
        
        # Patch OS/ABI if needed (byte index 7)
        if header.startswith(b"\x7fELF"):
            os_abi = header[7]
            LOGGER.info("Binary %s OS/ABI = %d (0x%02x)", dest_path, os_abi, os_abi)
            if os_abi == 9:
                with open(dest_path, "r+b") as f:
                    f.seek(7)
                    f.write(b"\x00")
                LOGGER.info("Patched OS/ABI of %s from 9 to 0 in local copy", dest_path)
                
            # Check interpreter path
            with open(dest_path, "rb") as f:
                data = f.read(4096)
            interp_idx = data.find(b"/lib")
            if interp_idx != -1:
                end_idx = data.find(b"\x00", interp_idx)
                if end_idx != -1:
                    interp = data[interp_idx:end_idx].decode('utf-8', errors='ignore')
                    LOGGER.info("Binary %s Dynamic Interpreter: %s", dest_path, interp)
                    
        # Make executable
        os.chmod(dest_path, 0o755)
        
        # Test execute
        try:
            res = subprocess.run([dest_path, "--version"], capture_output=True, text=True, timeout=2)
            LOGGER.info("Test execute %s: code=%d, stdout=%s, stderr=%s", dest_path, res.returncode, res.stdout[:150], res.stderr[:150])
            # If test execution succeeds, update config
            setattr(BinConfig, config_attr, dest_path)
            LOGGER.info("Updated BinConfig.%s to %s", config_attr, dest_path)
        except Exception as e:
            LOGGER.warning("Test execute %s failed: %s", dest_path, e)
            # Still update config as fallback
            setattr(BinConfig, config_attr, dest_path)
            LOGGER.info("Updated BinConfig.%s to %s (as fallback)", config_attr, dest_path)
            
    except Exception as e:
        LOGGER.warning("Failed to analyze/patch binary %s: %s", bin_name, e)

LOGGER.info("=== END OF BINARY DIAGNOSTICS & PATCHING ===")


sabnzbd_client = SabnzbdClient(
    host="http://localhost",
    api_key="admin",
    port="8070",
)
try:
    srun([BinConfig.QBIT_NAME, "-d", f"--profile={getcwd()}"], check=False)
except FileNotFoundError:
    LOGGER.warning("qBittorrent binary '%s' not found. qBit features will be unavailable.", BinConfig.QBIT_NAME)

scheduler = AsyncIOScheduler(event_loop=bot_loop)
