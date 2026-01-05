#!/usr/bin/env bash
set -euo pipefail

echo "Run these commands as the deployer user on the VPS (adjust paths as needed):"
cat <<'EOF'
# From /home/deployer/goexplorer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Copy .env from secure source (DO NOT commit .env)
# Ensure DB_* vars set in .env

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_dev

# Install and enable systemd service (requires sudo)
sudo cp deploy/gunicorn.goexplorer.service /etc/systemd/system/gunicorn-goexplorer.service
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-goexplorer

# Setup nginx (requires sudo)
sudo cp deploy/nginx.goexplorer.dev.conf /etc/nginx/sites-available/goexplorer-dev
sudo ln -sf /etc/nginx/sites-available/goexplorer-dev /etc/nginx/sites-enabled/goexplorer-dev
sudo nginx -t
sudo systemctl reload nginx
EOF

echo "Done. Follow any prompts above on the server."