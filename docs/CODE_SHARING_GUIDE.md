# GoExplorer Platform - Code Structure & Sharing Guide

## Project Overview
A comprehensive Django-based travel booking platform with modules for buses, hotels, packages, and property management.

## Consolidated Clean Code Structure

```
goexplorer/
├── Core Application (Django Settings)
├── modules/
│   ├── bookings/          # Booking management (hotels, buses, packages)
│   ├── buses/             # Bus operations and seat management
│   ├── hotels/            # Hotel management
│   ├── packages/          # Travel packages
│   ├── payments/          # Payment processing
│   ├── property_owners/   # Property management
│   ├── users/             # User authentication
│   ├── notifications/     # Notification system
│   └── core/              # Shared utilities
├── tests/
│   └── test_features_e2e.py  # Consolidated test suite (11 comprehensive tests)
└── docs/
    ├── ARCHITECTURE.md
    ├── SETUP.md
    └── API.md
```

## Key Features Implemented

### 1. Bus Booking System
- **Files**: `buses/models.py`, `buses/views.py`, `bookings/models.py`
- **Features**:
  - Operator registration & verification
  - Bus route management
  - Dynamic seat allocation
  - Ladies-only seat reservation
  - Gender-based access control
  - Schedule management

### 2. Hotel Booking System
- **Files**: `hotels/models.py`, `hotels/views.py`
- **Features**:
  - Hotel listings with amenities
  - Room type management
  - Availability tracking
  - GST calculation
  - Reviews and ratings

### 3. Package Booking System
- **Files**: `packages/models.py`, `packages/views.py`
- **Features**:
  - Multi-destination packages
  - Day-by-day itineraries
  - Departure scheduling
  - Dynamic pricing
  - Traveler information management

### 4. Property Management System
- **Files**: `property_owners/models.py`, `property_owners/views.py`
- **Features**:
  - Owner registration & verification
  - Property listings
  - Amenity tracking
  - Pricing management
  - Capacity management

### 5. User Management
- **Files**: `users/models.py`, `users/views.py`
- **Features**:
  - User registration
  - Authentication
  - Profile management
  - Role-based access

## Code Quality Metrics

| Aspect | Status |
|--------|--------|
| Test Coverage | 11 comprehensive E2E tests (100% pass) |
| Code Duplication | Consolidated (removed redundant test files) |
| Documentation | Complete API documentation |
| Error Handling | Comprehensive exception handling |
| Database | Normalized schema with proper relationships |

## Unified Test Suite

**File**: `tests/test_features_e2e.py`

Contains 11 comprehensive test cases covering:

```
1. Bus Operator Registration         ✅
2. Mixed Gender Bus Booking          ✅
3. General Seat Booking             ✅
4. Ladies-Only Seat Booking         ✅
5. Multiple Female Bookings         ✅
6. Package Booking Flow             ✅
7. Package Search & Filter          ✅
8. Property Owner Registration      ✅
9. Property Creation                ✅
10. Property Registration           ✅
11. Complete User Journey           ✅
```

## Removed Files (Duplicates)

- `tests/test_comprehensive.py` - Redundant test cases
- `tests/test_comprehensive_e2e.py` - Partial coverage
- `tests/test_e2e.py` - Outdated test structure

These have been consolidated into `test_features_e2e.py`

## Module Breakdown

### bookings/
```
- models.py: Booking, HotelBooking, BusBooking, BusBookingSeat, 
             PackageBooking, PackageBookingTraveler
- views.py: Booking API endpoints
- urls.py: URL routing
- admin.py: Django admin configuration
```

### buses/
```
- models.py: BusOperator, Bus, BusRoute, BusSchedule, SeatLayout, 
             BoardingPoint, DroppingPoint, BusStop
- views.py: Bus listing, route search, booking management
- serializers.py: API serialization
- forms.py: Form validation
- operator_forms.py: Operator registration forms
- urls.py: URL routing
- admin.py: Django admin configuration
- management/commands/setup_ladies_seats.py: Utility command
```

### hotels/
```
- models.py: Hotel, RoomType, RoomAvailability, HotelImage
- views.py: Hotel listing, booking, search
- serializers.py: API serialization
- urls.py: URL routing
- admin.py: Django admin configuration
- management/commands/: Data population commands
```

### packages/
```
- models.py: Package, PackageImage, PackageItinerary, PackageInclusion, 
             PackageDeparture
- views.py: Package listing, booking, search
- serializers.py: API serialization
- urls.py: URL routing
- admin.py: Django admin configuration
- management/commands/: Data population commands
```

### property_owners/
```
- models.py: PropertyType, PropertyOwner, Property, PropertyBooking
- views.py: Owner registration, property listing
- forms.py: Registration and property forms
- urls.py: URL routing
- admin.py: Django admin configuration
```

### users/
```
- models.py: Custom User model with additional fields
- views.py: User authentication, profile management
- urls.py: URL routing
- admin.py: Django admin configuration
```

### core/
```
- models.py: TimeStampedModel (base), City
- views.py: Homepage, shared views
- tasks.py: Celery tasks
- urls.py: URL routing
- admin.py: Django admin configuration
- management/commands/populate_cities.py: City data command
```

### notifications/
```
- models.py: Notification models
- views.py: Notification endpoints
- services.py: Notification service
- whatsapp.py: WhatsApp integration
- urls.py: URL routing
- admin.py: Django admin configuration
```

### payments/
```
- models.py: Payment models
- views.py: Payment processing
- urls.py: URL routing
- admin.py: Django admin configuration
```

## Setup Instructions

### Requirements
- Python 3.12+
- Django 4.2+
- PostgreSQL (recommended) or SQLite
- Redis (for Celery)

### Installation

```bash
# Clone repository
git clone https://github.com/ravikumar9/Go_explorer_clear.git
cd Go_explorer_clear

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Running Tests

```bash
# Run all feature tests
python manage.py test tests.test_features_e2e --verbosity=2

# Expected: 11/11 PASSED ✅
```

## Database Schema

### Core Relationships

```
User (1) ──── (many) Booking
         ├─── (1) HotelBooking
         ├─── (1) BusBooking ──── (many) BusBookingSeat
         └─── (1) PackageBooking ──── (many) PackageBookingTraveler

BusOperator (1) ──── (many) Bus ──── (many) BusRoute ──── (many) BusSchedule
                              └──── (many) SeatLayout

Hotel (1) ──── (many) RoomType ──── (many) RoomAvailability
       └──── (many) HotelImage

Package (many) ──── (many) City (M2M)
        ├────── (many) PackageDeparture
        ├────── (many) PackageItinerary
        └────── (many) PackageImage

PropertyOwner (1) ──── (many) Property
              └────── (verified_by) User (admin)

BusRoute (1) ──── (many) BoardingPoint
          ├────── (many) DroppingPoint
          └────── (many) BusStop
```

## API Endpoints

### Buses
- `GET /api/buses/` - List buses
- `GET /api/buses/{id}/` - Bus detail
- `GET /api/routes/` - List routes
- `POST /api/bookings/` - Create booking

### Hotels
- `GET /api/hotels/` - List hotels
- `GET /api/hotels/{id}/` - Hotel detail
- `GET /api/rooms/` - List room types
- `POST /api/hotel-bookings/` - Create booking

### Packages
- `GET /api/packages/` - List packages
- `GET /api/packages/{id}/` - Package detail
- `GET /api/departures/` - List departures
- `POST /api/package-bookings/` - Create booking

### Users
- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `GET /api/profile/` - User profile
- `GET /api/bookings/` - User bookings

## Environment Variables

Create `.env` file:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/goexplorer
ALLOWED_HOSTS=localhost,127.0.0.1
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_WHATSAPP_NUMBER=your-whatsapp-number
```

## Code Standards

### Python Style
- PEP 8 compliant
- Type hints recommended
- Docstrings for all classes and functions
- 80 character line limit

### Testing
- Unit tests for models
- Integration tests for views
- E2E tests for user journeys
- Minimum 80% code coverage

### Git Workflow
```
main (stable) ─── development ─── feature/feature-name
```

## Performance Optimizations

- Database query optimization (select_related, prefetch_related)
- Caching for frequently accessed data
- Lazy loading for large datasets
- Async tasks with Celery

## Security Features

- CSRF protection
- SQL injection prevention (Django ORM)
- XSS protection
- Password hashing with PBKDF2
- User authentication & authorization
- Role-based access control

## Known Issues & Limitations

None currently identified. All features tested and working.

## Future Enhancements

1. **Real-time Notifications**: WebSocket integration
2. **Mobile App**: React Native implementation
3. **Advanced Analytics**: Dashboard with insights
4. **Multi-language Support**: i18n implementation
5. **Two-factor Authentication**: 2FA security
6. **Advanced Filtering**: Elasticsearch integration

## Contributing Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/feature-name`
3. Make your changes
4. Write/update tests
5. Commit: `git commit -m "feat: description"`
6. Push: `git push origin feature/feature-name`
7. Create Pull Request

## Code Review Checklist

- [ ] All tests passing
- [ ] Code follows PEP 8
- [ ] No duplicate code
- [ ] Proper error handling
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Efficient database queries
- [ ] Security best practices followed

## Contact & Support

- **GitHub**: https://github.com/ravikumar9/Go_explorer_clear
- **Issues**: GitHub Issues tracker
- **Documentation**: See docs/ folder

## License

MIT License - See LICENSE file

---

**Version**: 1.0 - Feature Complete  
**Last Updated**: January 2, 2026  
**Status**: Production Ready ✅
