# GoExplorer Deployment Guide

## Local Development

### 1. Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Populate Sample Data
```bash
python manage.py populate_cities
```

### 5. Run Development Server
```bash
python manage.py runserver
```

## Production Deployment

### Option 1: Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Steps
```bash
# Login to Heroku
heroku login

# Create app
heroku create goexplorer-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Add Redis
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=.herokuapp.com,goexplorer.in
heroku config:set RAZORPAY_KEY_ID=your_razorpay_key
heroku config:set RAZORPAY_KEY_SECRET=your_razorpay_secret

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Populate cities
heroku run python manage.py populate_cities

# Collect static files
heroku run python manage.py collectstatic --noinput

# Open app
heroku open
```

### Option 2: AWS EC2

#### Prerequisites
- AWS account
- EC2 instance (Ubuntu 22.04)
- Domain name

#### Steps

1. **Connect to EC2**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

2. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx redis-server
```

3. **Setup PostgreSQL**
```bash
sudo -u postgres psql
CREATE DATABASE goexplorer;
CREATE USER goexploreruser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE goexplorer TO goexploreruser;
\q
```

4. **Clone Repository**
```bash
cd /home/ubuntu
git clone https://github.com/ravikumar9/Go_explorer_clear.git
cd Go_explorer_clear
```

5. **Setup Python Environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Configure Environment**
```bash
cp .env.example .env
nano .env
# Update with production values
```

7. **Run Migrations**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py populate_cities
python manage.py collectstatic --noinput
```

8. **Setup Gunicorn**
```bash
sudo nano /etc/systemd/system/goexplorer.service
```

Add:
```ini
[Unit]
Description=GoExplorer Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Go_explorer_clear
Environment="PATH=/home/ubuntu/Go_explorer_clear/venv/bin"
ExecStart=/home/ubuntu/Go_explorer_clear/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/ubuntu/Go_explorer_clear/goexplorer.sock \
          goexplorer.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start goexplorer
sudo systemctl enable goexplorer
```

9. **Setup Nginx**
```bash
sudo nano /etc/nginx/sites-available/goexplorer
```

Add:
```nginx
server {
    listen 80;
    server_name goexplorer.in www.goexplorer.in;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/ubuntu/Go_explorer_clear;
    }
    
    location /media/ {
        root /home/ubuntu/Go_explorer_clear;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/Go_explorer_clear/goexplorer.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/goexplorer /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

10. **Setup SSL (Let's Encrypt)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d goexplorer.in -d www.goexplorer.in
```

11. **Setup Celery**
```bash
sudo nano /etc/systemd/system/celery.service
```

Add:
```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Go_explorer_clear
Environment="PATH=/home/ubuntu/Go_explorer_clear/venv/bin"
ExecStart=/home/ubuntu/Go_explorer_clear/venv/bin/celery -A goexplorer worker -l info

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start celery
sudo systemctl enable celery
```

### Option 3: DigitalOcean App Platform

1. **Connect GitHub repository**
2. **Configure build settings:**
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Run Command: `gunicorn goexplorer.wsgi`
3. **Add PostgreSQL database**
4. **Add Redis instance**
5. **Set environment variables**
6. **Deploy**

## Post-Deployment

### 1. Verify Installation
```bash
# Check if site is running
curl https://goexplorer.in

# Check admin panel
curl https://goexplorer.in/admin/
```

### 2. Setup Monitoring
- Configure error tracking (Sentry)
- Setup uptime monitoring
- Configure log aggregation

### 3. Backup Configuration
```bash
# Database backup
pg_dump goexplorer > backup.sql

# Media files backup
tar -czf media-backup.tar.gz media/
```

### 4. Configure CDN (Optional)
- CloudFlare for static files
- AWS CloudFront
- DigitalOcean Spaces

## Domain Configuration

### Point Domain to Server
```
A Record:  goexplorer.in     -> YOUR_SERVER_IP
A Record:  www.goexplorer.in -> YOUR_SERVER_IP
```

## Payment Gateway Setup

### Razorpay
1. Go to https://dashboard.razorpay.com
2. Create account
3. Get API keys from Settings > API Keys
4. Add to environment variables:
   - `RAZORPAY_KEY_ID`
   - `RAZORPAY_KEY_SECRET`

### Testing Payments
Use test cards:
- Card: 4111 1111 1111 1111
- CVV: Any 3 digits
- Expiry: Any future date

## Troubleshooting

### Common Issues

1. **Static files not loading**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

2. **Database connection error**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check credentials in .env
```

3. **Celery not working**
```bash
sudo systemctl status celery
sudo journalctl -u celery -f
```

4. **502 Bad Gateway**
```bash
sudo systemctl status goexplorer
sudo journalctl -u goexplorer -f
```

## Security Checklist

- [ ] Set DEBUG=False
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up firewall (UFW)
- [ ] Regular security updates
- [ ] Database backups
- [ ] Rate limiting
- [ ] Input validation
- [ ] XSS protection

## Maintenance

### Regular Tasks
- Update dependencies
- Database backups
- Monitor error logs
- Check disk space
- Review security patches

### Update Deployment
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart goexplorer
sudo systemctl restart celery
```

## Support

For deployment issues:
- Email: support@goexplorer.in
- Documentation: https://github.com/ravikumar9/Go_explorer_clear

---

**Production Ready** ✅
