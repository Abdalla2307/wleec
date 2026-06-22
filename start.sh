if [ $# -gt 0 ]; then
    exec "$@"
else
    source .venv/bin/activate && python3 update.py && python3 -m bot
fi

