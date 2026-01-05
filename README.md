# GoExplorer - Travel Booking Platform

A full-featured Django-based travel booking platform supporting bus, hotel, and vacation package bookings with property management, payment processing, and comprehensive testing.

**Status**: ✅ Production Ready | **Tests**: 11/11 Passing | **Python**: 3.12+

## Features

- 🚌 **Bus Booking** - Mixed gender reservations with gender-specific seating
- 🏨 **Hotel Booking** - Room availability and reservation system
- 📦 **Package Tours** - Multi-destination itineraries with departures
- 🏠 **Property Management** - Property owner registration and verification
- 💳 **Payment Integration** - Razorpay secure payments
- 📱 **Notifications** - SMS/WhatsApp via Twilio
- ⭐ **Ratings** - User reviews and ratings system
- 🔐 **Authentication** - User registration and login

## Quick Start

```bash
# Clone repository
git clone https://github.com/ravikumar9/Go_explorer_clear.git
cd Go_explorer_clear

# Setup environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver

# Test (11 comprehensive E2E tests)
python manage.py test tests.test_features_e2e --verbosity=2
```

Visit: http://localhost:8000/

## Project Structure

```
bookings/              # Booking models and APIs
buses/                 # Bus operations and seat management
core/                  # Shared utilities and base models
hotels/                # Hotel management and booking
packages/              # Travel packages and itineraries
payments/              # Payment processing
property_owners/       # Property listing and verification
users/                 # User authentication
notifications/         # SMS and WhatsApp notifications
templates/             # HTML templates
static/                # CSS, JS, images
tests/
  └── test_features_e2e.py  # 11 E2E tests covering all features
```

## Technology Stack

- **Framework**: Django 4.2+
- **API**: Django REST Framework
- **Database**: PostgreSQL / SQLite
- **Task Queue**: Celery + Redis
- **Payment**: Razorpay API
- **Notifications**: Twilio (SMS/WhatsApp)
- **Testing**: Django TestCase + pytest

## Core Models

### Bookings
- `Booking` - Base booking model (hotel, bus, package)
- `BusBooking` - Bus-specific bookings
- `BusBookingSeat` - Individual seat assignments
- `HotelBooking` - Hotel reservations
- `PackageBooking` - Package tour bookings

### Buses
- `BusOperator` - Bus company registration
- `Bus` - Bus details (type, amenities, capacity)
- `BusRoute` - Route information
- `BusSchedule` - Date-specific schedules
- `SeatLayout` - Seat configuration with gender restrictions

### Hotels
- `Hotel` - Hotel information
- `RoomType` - Room categories
- `RoomAvailability` - Availability tracking

### Packages
- `Package` - Package details
- `PackageItinerary` - Day-by-day itinerary
- `PackageDeparture` - Available departure dates

### Properties
- `PropertyOwner` - Owner registration and verification
- `Property` - Individual property listings

## API Endpoints

```
Auth:
  POST   /api/register/
  POST   /api/login/
  
Buses:
  GET    /api/buses/
  GET    /api/buses/{id}/
  POST   /api/bus-bookings/
  
Hotels:
  GET    /api/hotels/
  POST   /api/hotel-bookings/
  
Packages:
  GET    /api/packages/
  POST   /api/package-bookings/
  
Properties:
  GET    /api/properties/
  POST   /api/property-owners/
```

## Testing

**Comprehensive E2E Test Suite** (`tests/test_features_e2e.py`):

1. ✅ Bus Operator Registration
2. ✅ Mixed Gender Bus Booking
3. ✅ General Seat Booking
4. ✅ Ladies-Only Seat Booking
5. ✅ Multiple Female Bookings
6. ✅ Package Booking
7. ✅ Package Search & Filter
8. ✅ Property Owner Registration
9. ✅ Property Creation
10. ✅ Property Registration
11. ✅ Complete User Journey

Run tests:
```bash
# All tests
python manage.py test tests.test_features_e2e --verbosity=2

# Specific test
python manage.py test tests.test_features_e2e.BusBookingMixedGenderTestCase

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## Environment Configuration

Create `.env` file in project root:

```env
# Django
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost/goexplorer

# Payment
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret

# Notifications
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_WHATSAPP_NUMBER=+1234567890

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Redis
REDIS_URL=redis://localhost:6379/0
```

## Development (DEV only)

Follow these steps for local development with PostgreSQL:

1. Copy `.env.example` to `.env` and update values (do not commit `.env`).

2. Set DB_* variables in `.env` (DEV values):

   DB_NAME=goexplorer_dev
   DB_USER=goexplorer_dev_user
   DB_PASSWORD=your_password_here
   DB_HOST=localhost
   DB_PORT=5432

3. Install dependencies and run migrations:

```bash
pip install -r requirements.txt
python manage.py migrate
```

4. Create superuser and seed sample data:

```bash
python manage.py createsuperuser
python manage.py seed_dev
```

5. Verify DEV environment & static files:

```bash
python manage.py check_dev --collectstatic
```

6. Run server (DEV):

```bash
python manage.py runserver
```

Or using Gunicorn (DEV server with systemd + nginx):

- Copy `.env.example` -> `.env` and update values as described earlier
- Install dependencies and create virtualenv on server:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run migrations, collectstatic and seed:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_dev
```

- Deploy Gunicorn systemd unit and NGINX (templates provided under `deploy/`):

```bash
# copy service file
sudo cp deploy/gunicorn.goexplorer.service /etc/systemd/system/gunicorn-goexplorer.service
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn-goexplorer

# copy nginx conf (verify path and server_name)
sudo cp deploy/nginx.goexplorer.dev.conf /etc/nginx/sites-available/goexplorer-dev
sudo ln -s /etc/nginx/sites-available/goexplorer-dev /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

After this the app should be accessible at http://goexplorer-dev.cloud

This is a dev-only setup: keep `DEBUG=True`, use the dev DB, and do not set production secrets here.

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use environment variables for secrets
- [ ] Setup PostgreSQL database
- [ ] Configure HTTPS/SSL
- [ ] Set up Redis for Celery
- [ ] Run `python manage.py collectstatic`
- [ ] Configure logging and monitoring
- [ ] Setup database backups

### Deploy to Heroku
```bash
heroku create your-app-name
heroku config:set DEBUG=False SECRET_KEY=your-key
git push heroku main
heroku run python manage.py migrate
```

## Code Quality

- PEP 8 compliant
- Type hints included
- Comprehensive test coverage
- Docstrings for modules and functions
- Removed duplicate code
- No unnecessary dependencies

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m "feat: description"`
4. Push to branch: `git push origin feature/your-feature`
5. Create Pull Request

## Documentation

- **[COMPREHENSIVE_FEATURE_TESTING_REPORT.md](COMPREHENSIVE_FEATURE_TESTING_REPORT.md)** - Detailed test results
- **[TEST_COMPLETION_SUMMARY.md](TEST_COMPLETION_SUMMARY.md)** - Test summary and validation
- **[CODE_SHARING_GUIDE.md](CODE_SHARING_GUIDE.md)** - Code architecture and sharing guidelines
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference

## Key Improvements Made

✅ Consolidated 3 duplicate test files → 1 unified test suite  
✅ Removed 58 old documentation files → Archived to `docs/archived/`  
✅ Removed unnecessary files excluded by .gitignore  
✅ Code verified and all 11 tests passing  
✅ Production-ready codebase  

## Support & Contact

- **Repository**: https://github.com/ravikumar9/Go_explorer_clear
- **Issues**: GitHub Issues tracker
- **Tests**: Run `python manage.py test tests.test_features_e2e`

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Django & Django REST Framework
- Razorpay for payment processing
- Twilio for notifications
- All contributors

---

**Ready to use!** Start with `python manage.py runserver` 🚀

*Version 1.0 | Production Ready | Last Updated: January 2, 2026*
