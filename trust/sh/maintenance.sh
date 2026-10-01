python3 "$(dirname "$0")/../trust_teardown.py" --once                          # one shot
python3 "$(dirname "$0")/../trust_teardown.py" --interval 600 --log-file /var/log/trust.log  # daemon mode
python3 "$(dirname "$0")/../trust_teardown.py" --dry-run --once                # test without changes