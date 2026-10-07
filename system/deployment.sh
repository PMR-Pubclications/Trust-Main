# 1. Copy unit files into systemd directory
sudo cp trust-*.service /etc/systemd/system/

# 2. Reload systemd manager configuration
sudo systemctl daemon-reload

# 3. Enable all services to auto-start on system boot
sudo systemctl enable trust-firstresponder trust-ems trust-fire trust-police

# 4. Start all services simultaneously
sudo systemctl start trust-firstresponder trust-ems trust-fire trust-police

# 5. Check operational status across all modules
sudo systemctl status "trust-*"

sudo journalctl -u trust-firstresponder -u trust-ems -u trust-fire -u trust-police -f
