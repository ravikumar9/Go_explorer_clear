# 🚀 PRODUCTION DEPLOYMENT GUIDE - GoExplorer Platform

**Last Updated:** January 3, 2026  
**Status:** Ready for Production Deployment

---

## 📋 TABLE OF CONTENTS

1. [Pre-Production Checklist](#pre-production-checklist)
2. [What You Need to Provide](#what-you-need-to-provide)
3. [Recommended Services & Providers](#recommended-services--providers)
4. [Deployment Architecture](#deployment-architecture)
5. [Step-by-Step Deployment](#step-by-step-deployment)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Cost Estimates](#cost-estimates)

---

## ✅ PRE-PRODUCTION CHECKLIST

Before moving to production, ensure:

### Code Quality
- [x] All Django checks pass
- [x] All migrations applied
- [x] Security settings configured
- [x] Environment variables documented
- [x] Error handling implemented
- [x] Logging configured
- [ ] HTTPS/SSL configured
- [ ] CORS headers configured
- [ ] Rate limiting implemented

### Database
- [x] Database schema finalized
- [x] Indexes created for performance
- [ ] Backup strategy defined
- [ ] Data migration plan created
- [ ] Database monitoring enabled

### Testing
- [x] Feature testing completed
- [x] Admin panel verified
- [x] API endpoints tested
- [ ] Load testing performed
- [ ] Security testing completed

### Infrastructure
- [ ] Cloud hosting selected
- [ ] Domain registered
- [ ] SSL certificate obtained
- [ ] CDN configured (optional)
- [ ] Email service configured
- [ ] SMS service configured

---

## 📦 WHAT YOU NEED TO PROVIDE

### Essential (Required)
1. **Domain Name**
   - Example: `goexplorer.com`
   - Budget: $10-15/year
   - Registrar: GoDaddy, Namecheap, Route53

2. **Cloud Hosting Provider** (Pick ONE)
   - Credentials and admin access
   - Database details
   - API keys for services

3. **Email Service Credentials**
   - SMTP configuration
   - From email address
   - API keys (if applicable)

4. **Database Details**
   - Database name
   - Master username
   - Master password
   - Database host

5. **Payment Gateway Integration**
   - Razorpay/PayU merchant account
   - API Key & Secret
   - Webhook credentials

6. **SMS Service** (Optional but recommended)
   - Twilio/AWS SNS credentials
   - Phone number for OTP

7. **File Storage** (Images, Documents)
   - AWS S3 bucket
   - Access keys
   - Bucket policies

### Nice-to-Have
- Google Analytics ID
- Error tracking (Sentry)
- Performance monitoring (New Relic)
- Log aggregation (LogDNA, Datadog)

---

## 🏆 RECOMMENDED SERVICES & PROVIDERS

### 1. CLOUD HOSTING

#### Option A: AWS (Amazon Web Services) ⭐ RECOMMENDED
**Pros:**
- Global infrastructure
- Best for scaling
- 12 months free tier
- Excellent support

**Services You'll Use:**
- EC2 (Virtual Servers) - $5-20/month
- RDS (Managed Database) - $10-50/month
- S3 (File Storage) - $1-5/month
- CloudFront (CDN) - $0.085 per GB
- Route53 (DNS) - $0.50/hosted zone
- **Total:** $50-100/month

**Get Started:**
```
1. Create AWS account: aws.amazon.com
2. Select region: Mumbai (ap-south-1) for lower latency in India
3. Launch EC2 instance: t3.micro or t3.small
4. Create RDS PostgreSQL database
5. Create S3 bucket for media
```

---

#### Option B: DigitalOcean
**Pros:**
- Simplicity & transparency
- Better for startups
- Good pricing

**Services:**
- Droplet (Server) - $5-24/month
- Managed Database - $15-50/month
- Spaces (File Storage) - $5/month
- **Total:** $25-80/month

**Get Started:**
```
1. Create account: digitalocean.com
2. Create Droplet: Ubuntu 24.04 LTS
3. Create Managed Database: PostgreSQL
4. Create Space for media storage
```

---

#### Option C: Heroku
**Pros:**
- Easiest deployment
- Perfect for beginners
- No infrastructure management

**Services:**
- Dyno (Server) - $7-50/month
- PostgreSQL - $9-200/month
- Add-ons (Sendgrid, etc.) - $0-50/month
- **Total:** $50-150/month

**Get Started:**
```
1. Create account: heroku.com
2. Install Heroku CLI
3. Push code: git push heroku main
4. Setup database: heroku addons:create heroku-postgresql
```

---

### 2. DOMAIN REGISTRAR

#### Recommended Registrars
| Provider | Price/Year | Features | Recommendation |
|----------|-----------|----------|-----------------|
| **Namecheap** | $8.95 | WhoisGuard, Fast support | ⭐ Best Value |
| **GoDaddy** | $12.99 | Popular, Easy | Good |
| **Route53 (AWS)** | $0.50 + DNS | Integrated with AWS | If using AWS |
| **Hostinger** | $2.99 (Year 1) | Cheap, Good support | Budget option |

**Action Required:**
- [ ] Buy domain (e.g., goexplorer.com)
- [ ] Configure DNS records
- [ ] Point to hosting provider

---

### 3. DATABASE

#### PostgreSQL (Recommended) ⭐
**Why:** Production-grade, perfect for Django

**Hosting Options:**
- AWS RDS PostgreSQL: $10-50/month
- DigitalOcean Managed DB: $15-50/month
- Self-hosted on EC2: $5/month (needs management)

**Setup:**
```sql
CREATE DATABASE goexplorer;
CREATE USER goexplorer_user WITH PASSWORD 'SecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE goexplorer TO goexplorer_user;
```

---

### 4. EMAIL SERVICE

#### SendGrid ⭐ RECOMMENDED
**Pricing:** Free up to 100 emails/day, then $15/month for 10K emails

**Setup:**
```python
# settings.py
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = 'SG.xxxxxxxxxxx'
EMAIL_HOST_USER = 'noreply@goexplorer.com'
```

**Alternatives:**
- **Mailgun**: $35/month (more affordable)
- **AWS SES**: $0.10 per 1K emails (cheapest)
- **Brevo (Sendinblue)**: Free up to 300/day

---

### 5. PAYMENT GATEWAY

#### Razorpay ⭐ RECOMMENDED FOR INDIA
**Fees:** 2.99% + ₹0 per transaction

**Setup:**
```python
# settings.py
RAZORPAY_KEY_ID = 'rzp_live_xxxxx'
RAZORPAY_KEY_SECRET = 'xxxxxx'
```

**Alternatives:**
- **PayU**: 2.99% + ₹5 (similar)
- **Stripe**: 2.9% + $0.30 (international)
- **PhonePe**: 2% (merchant payments)

---

### 6. SMS SERVICE

#### Twilio (Optional)
**Pricing:** $0.0075 per SMS (India)

**Setup:**
```python
# settings.py
TWILIO_ACCOUNT_SID = 'ACxxxxxxx'
TWILIO_AUTH_TOKEN = 'xxxx'
TWILIO_PHONE_NUMBER = '+1234567890'
```

**Alternatives:**
- **MSG91**: ₹0.50 per SMS (cheaper in India)
- **AWS SNS**: $0.50 per 100 SMS (if using AWS)

---

### 7. FILE STORAGE

#### AWS S3 ⭐ RECOMMENDED
**Pricing:** Free for 1GB/month, then $0.025 per GB

**Setup:**
```python
# settings.py
USE_S3 = True
AWS_STORAGE_BUCKET_NAME = 'goexplorer-media'
AWS_S3_REGION_NAME = 'ap-south-1'
AWS_ACCESS_KEY_ID = 'xxxx'
AWS_SECRET_ACCESS_KEY = 'xxxx'
```

**Alternatives:**
- **DigitalOcean Spaces**: $5/month (10GB)
- **Azure Blob Storage**: $0.018 per GB

---

### 8. MONITORING & LOGGING

#### Sentry (Error Tracking) ⭐ RECOMMENDED
**Pricing:** Free for small projects, $29/month for teams

**Setup:**
```python
import sentry_sdk
sentry_sdk.init(
    dsn="https://xxxxxxx@sentry.io/xxxxx",
    traces_sample_rate=1.0
)
```

---

#### Datadog (Full Monitoring)
**Pricing:** $15/month

**Setup:** Monitor server, database, application metrics

---

## 🏗️ DEPLOYMENT ARCHITECTURE

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT BROWSERS                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
           ┌──────────────────┐
           │   CloudFront     │ (CDN - Optional)
           │   (CDN Cache)    │
           └────────┬─────────┘
                     │
                     ▼
      ┌──────────────────────────────┐
      │   Route53 / DNS Provider     │
      └────────────┬─────────────────┘
                     │
                     ▼
      ┌──────────────────────────────────┐
      │      Load Balancer (Optional)    │
      │    (If using multiple servers)   │
      └────────────┬─────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    ┌──────────────┐    ┌──────────────┐
    │   Django     │    │   Django     │
    │   Server 1   │    │   Server 2   │
    │   (EC2/     │    │   (EC2/      │
    │   Droplet)   │    │   Droplet)   │
    └──────────────┘    └──────────────┘
          │                     │
          └──────────┬──────────┘
                     ▼
      ┌──────────────────────────────┐
      │   PostgreSQL Database        │
      │   (RDS / Managed DB)         │
      └──────────────────────────────┘
          │          │
          ▼          ▼
      ┌────────┐  ┌────────┐
      │Backup  │  │Replica │
      │Server  │  │Server  │
      └────────┘  └────────┘

    Additional Services:
    ├── S3 / Spaces (File Storage)
    ├── SendGrid (Email)
    ├── Razorpay (Payments)
    ├── Sentry (Error Tracking)
    └── Datadog (Monitoring)
```

---

## 🔧 STEP-BY-STEP DEPLOYMENT

### Step 1: Prepare Code for Production

**Update settings.py:**

```python
# goexplorer/settings.py

# Security
DEBUG = False
ALLOWED_HOSTS = ['goexplorer.com', 'www.goexplorer.com', 'api.goexplorer.com']
SECRET_KEY = os.environ.get('SECRET_KEY')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
    }
}

# Static & Media Files (AWS S3)
STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        'OPTIONS': {
            'bucket_name': os.environ.get('AWS_STORAGE_BUCKET_NAME'),
            'region_name': os.environ.get('AWS_S3_REGION_NAME'),
        }
    },
    'staticfiles': {
        'BACKEND': 'storages.backends.s3boto3.S3StaticStorage',
    },
}

# Email
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'noreply@goexplorer.com'

# HTTPS & Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
        },
    },
    'root': {
        'handlers': ['console', 'sentry'],
        'level': 'INFO',
    },
}

# Sentry
import sentry_sdk
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)
```

---

### Step 2: Create Environment Files

**Create `.env.production`:**

```env
# Django
DEBUG=False
SECRET_KEY=your-super-secret-key-here-minimum-50-chars

# Database
DB_ENGINE=postgresql
DB_NAME=goexplorer
DB_USER=goexplorer_user
DB_PASSWORD=YourSecurePassword123!
DB_HOST=your-db-instance.xxxx.rds.amazonaws.com
DB_PORT=5432

# AWS S3
USE_S3=True
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=goexplorer-media
AWS_S3_REGION_NAME=ap-south-1
AWS_S3_CUSTOM_DOMAIN=goexplorer-media.s3.amazonaws.com

# Email (SendGrid)
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here

# Razorpay
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxxx

# Twilio (Optional)
TWILIO_ACCOUNT_SID=ACxxxxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_PHONE_NUMBER=+1234567890

# Sentry
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# Domain
ALLOWED_HOSTS=goexplorer.com,www.goexplorer.com,api.goexplorer.com
```

**Never commit `.env` files to Git!**

---

### Step 3: Deploy to Cloud

#### Option A: AWS EC2 Deployment

```bash
# 1. SSH into your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 2. Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql-client git nginx supervisor -y

# 3. Clone repository
git clone https://github.com/yourusername/Go_explorer_clear.git
cd Go_explorer_clear

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Create .env file with production values
nano .env.production

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Run migrations
python manage.py migrate

# 9. Create superuser
python manage.py createsuperuser

# 10. Configure Nginx
sudo nano /etc/nginx/sites-available/goexplorer
# Add configuration below

# 11. Enable Nginx site
sudo ln -s /etc/nginx/sites-available/goexplorer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 12. Configure Supervisor for Gunicorn
sudo nano /etc/supervisor/conf.d/goexplorer.conf
# Add configuration below

# 13. Start services
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start goexplorer
```

**Nginx Configuration:**

```nginx
server {
    listen 80;
    server_name goexplorer.com www.goexplorer.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name goexplorer.com www.goexplorer.com;
    
    # SSL certificates (from Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/goexplorer.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/goexplorer.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /home/ubuntu/Go_explorer_clear/staticfiles/;
        expires 30d;
    }
    
    # Media files (if not using S3)
    location /media/ {
        alias /home/ubuntu/Go_explorer_clear/media/;
        expires 7d;
    }
}
```

**Supervisor Configuration:**

```ini
[program:goexplorer]
command=/home/ubuntu/Go_explorer_clear/venv/bin/gunicorn goexplorer.wsgi:application --bind 127.0.0.1:8000 --workers 4 --worker-class sync
directory=/home/ubuntu/Go_explorer_clear
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/goexplorer.log
environment=PATH="/home/ubuntu/Go_explorer_clear/venv/bin",HOME="/home/ubuntu",DB_HOST="your-db-host"
```

---

#### Option B: Heroku Deployment

```bash
# 1. Install Heroku CLI
curl https://cli.heroku.com/install.sh | sh

# 2. Login to Heroku
heroku login

# 3. Create Heroku app
heroku create goexplorer-app

# 4. Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0 --app goexplorer-app

# 5. Set environment variables
heroku config:set DEBUG=False --app goexplorer-app
heroku config:set SECRET_KEY='your-secret-key' --app goexplorer-app
heroku config:set SENDGRID_API_KEY='your-key' --app goexplorer-app
heroku config:set RAZORPAY_KEY_ID='your-key' --app goexplorer-app
heroku config:set RAZORPAY_KEY_SECRET='your-secret' --app goexplorer-app

# 6. Deploy
git push heroku main

# 7. Run migrations
heroku run python manage.py migrate --app goexplorer-app

# 8. Create superuser
heroku run python manage.py createsuperuser --app goexplorer-app

# 9. Collect static files
heroku run python manage.py collectstatic --noinput --app goexplorer-app
```

---

### Step 4: Setup SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Generate certificate
sudo certbot certonly --nginx -d goexplorer.com -d www.goexplorer.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

---

## 📊 POST-DEPLOYMENT CONFIGURATION

### 1. Database Backups

**AWS RDS:**
- Automated backups: 35 days retention
- Manual snapshots: Create weekly
- Cross-region replication: Enable for disaster recovery

**Command (if self-hosted):**
```bash
# Daily backup at 2 AM
0 2 * * * pg_dump goexplorer > /backups/goexplorer-$(date +\%Y\%m\%d).sql
```

---

### 2. DNS Configuration

**Add DNS Records:**

| Type | Name | Value |
|------|------|-------|
| A | @ | Your EC2/Server IP |
| A | www | Your EC2/Server IP |
| CNAME | api | Your EC2/Server IP |
| MX | @ | mail.goexplorer.com |
| TXT | @ | v=spf1 include:sendgrid.net ~all |

---

### 3. Email Configuration Test

```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test Email',
...     'This is a test email',
...     'noreply@goexplorer.com',
...     ['your-email@example.com'],
... )
```

---

### 4. Payment Gateway Testing

**Razorpay Test Mode:**
- Use test API keys before going live
- Test credit card: 4111 1111 1111 1111
- Test OTP: any 6 digits

---

## 📈 MONITORING & MAINTENANCE

### Daily Tasks
- [ ] Check Sentry for errors
- [ ] Monitor server CPU/Memory
- [ ] Review application logs

### Weekly Tasks
- [ ] Backup database
- [ ] Check disk space
- [ ] Review performance metrics
- [ ] Update security patches

### Monthly Tasks
- [ ] Review AWS/hosting costs
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Analyze user metrics
- [ ] Plan feature releases

### Quarterly Tasks
- [ ] Security audit
- [ ] Performance optimization
- [ ] Disaster recovery drill
- [ ] Capacity planning

---

## 💰 COST ESTIMATES

### Monthly Costs Breakdown

#### Minimal Setup (₹3,000-5,000 / month)
- Cloud Server (AWS t3.micro): ₹1,000
- Database (AWS RDS): ₹1,500
- Storage (AWS S3): ₹300
- Email (SendGrid Free): ₹0
- Domain: ₹0 (already paid)
- **Total: ₹2,800**

---

#### Small Business Setup (₹8,000-12,000 / month)
- Cloud Server (AWS t3.small): ₹2,000
- Database (AWS RDS): ₹3,000
- Storage (AWS S3): ₹500
- Email (SendGrid): ₹1,000
- Monitoring (Datadog): ₹1,500
- CDN (CloudFront): ₹500
- SMS (Twilio): ₹1,000
- **Total: ₹9,500**

---

#### Enterprise Setup (₹20,000-30,000 / month)
- Load Balancer: ₹2,000
- Multiple Servers: ₹6,000
- High-Performance DB: ₹8,000
- Multiple Backups: ₹2,000
- Advanced Monitoring: ₹2,500
- CDN: ₹1,000
- All Services: ₹3,000
- **Total: ₹24,500**

---

## 🎯 QUICK STARTUP PLAN

### Month 1: Preparation
- [ ] Buy domain
- [ ] Create AWS account
- [ ] Setup database
- [ ] Configure email
- [ ] Setup payment gateway

### Month 2: Deployment
- [ ] Deploy to AWS
- [ ] Setup SSL certificate
- [ ] Configure monitoring
- [ ] Load testing
- [ ] Security audit

### Month 3: Launch
- [ ] Go live
- [ ] Monitor closely
- [ ] Gather feedback
- [ ] Optimize performance
- [ ] Plan next features

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues & Solutions

**Database Connection Error:**
```bash
python manage.py dbshell
# If this fails, check:
# 1. Database host/port
# 2. Credentials
# 3. Network security groups
```

**Static Files Not Loading:**
```bash
python manage.py collectstatic --noinput --clear
# If using S3, verify:
# 1. AWS credentials
# 2. S3 bucket exists
# 3. Bucket policy allows public access
```

**Email Not Sending:**
```bash
# Check SendGrid API key
python manage.py shell
>>> import sendgrid
>>> sg = sendgrid.SendGridAPIClient('your-key')
>>> sg.get_account()
```

---

## ✅ PRE-LAUNCH CHECKLIST

- [ ] All migrations applied
- [ ] Django checks passed
- [ ] SSL certificate installed
- [ ] Database backed up
- [ ] Email configured & tested
- [ ] Payment gateway working
- [ ] Monitoring enabled
- [ ] Admin panel accessible
- [ ] API endpoints tested
- [ ] Performance acceptable (<2s load time)
- [ ] Mobile responsive verified
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Logging configured
- [ ] Error tracking (Sentry) working
- [ ] Database replicas setup
- [ ] Backup automation enabled

---

## 🎉 NEXT STEPS

1. **Prepare Details**: Gather all required information from section "What You Need to Provide"
2. **Choose Services**: Select cloud provider, email service, payment gateway
3. **Provision Infrastructure**: Create accounts and configure services
4. **Deploy Code**: Follow deployment steps for your chosen platform
5. **Test Everything**: Run through testing checklist
6. **Go Live**: Launch to production
7. **Monitor**: Watch metrics and logs closely for first week

---

**Ready to proceed? Contact the development team with your service selections and credentials!**

**Document Version:** 1.0  
**Last Updated:** January 3, 2026  
**Status:** ✅ PRODUCTION READY
