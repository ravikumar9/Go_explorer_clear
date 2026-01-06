# Quick Start: Property Owner & Bus Operator Registration

## For Users

### Register as Property Owner
1. Go to **GoExplorer homepage**
2. Scroll down to **"Grow Your Business With GoExplorer"** section
3. Click **"Register as Property Owner"** button
4. Fill in the registration form:
   - Property name, type (Homestay/Resort/Villa/etc)
   - Your name, phone, email
   - Property location and address
   - Optional: GST, PAN, business license
   - Bank account details for payouts
5. Click **"Register as Property Owner"**
6. Your account will be verified within **24-48 hours**
7. Once verified, you can start listing your properties!

**Direct Link:** `http://yourdomain.com/properties/register/`

### Register as Bus Operator
1. Go to **GoExplorer homepage**
2. Scroll down to **"Grow Your Business With GoExplorer"** section
3. Click **"Register as Bus Operator"** button
4. Fill in the registration form:
   - Company name, phone, email
   - Company description
   - GST, PAN, business license
   - Business address
   - Create a password (must have 8+ chars, letters, numbers)
   - Confirm password
5. Click **"Register as Bus Operator"**
6. You'll be logged in automatically
7. Your account will be verified within **24-48 hours**
8. Once verified, you can list your buses and routes!

**Direct Link:** `http://yourdomain.com/buses/operator/register/`

### Access Your Dashboard
After registration, you can access your dashboard:

**Property Owner Dashboard:**
- View verification status
- See property count, bookings, ratings, earnings
- Manage your properties
- View guest bookings
- Add new properties (after verification)

**Bus Operator Dashboard:**
- View verification status
- See buses, routes, bookings, revenue
- Manage your fleet
- View passenger bookings
- Add new buses (after verification)

---

## For Developers

### Installation

1. **Update URLs** (Already done)
   ```python
   # goexplorer/urls.py
   from django.urls import path, include
   
   urlpatterns = [
       ...
       path('properties/', include('property_owners.urls')),
       path('buses/', include('buses.urls')),
   ]
   ```

2. **Install App** (Already done)
   ```python
   # goexplorer/settings.py
   INSTALLED_APPS = [
       ...
       'property_owners',
       'buses',
   ]
   ```

3. **Run Migrations** (Already done)
   ```bash
   python manage.py makemigrations property_owners
   python manage.py migrate
   ```

### File Locations

**Property Owners App:**
- Models: `property_owners/models.py`
- Forms: `property_owners/forms.py`
- Views: `property_owners/views.py`
- URLs: `property_owners/urls.py`
- Templates: `templates/property_owners/`

**Bus Operator (in buses app):**
- Forms: `buses/operator_forms.py`
- Views: `buses/operator_forms.py` (register_bus_operator, operator_dashboard)
- URLs: `buses/urls.py`
- Templates: `templates/buses/operator_register.html`, `operator_dashboard.html`

**Navigation:**
- Base template: `templates/base.html`
- Home page: `templates/home.html`

### Database Models

#### PropertyOwner
```python
class PropertyOwner(models.Model):
    owner = ForeignKey(User)
    business_name = CharField(max_length=200)
    property_type = CharField(choices=PROPERTY_TYPES)
    description = TextField()
    owner_name = CharField(max_length=200)
    owner_phone = CharField(max_length=20)
    owner_email = EmailField()
    city = ForeignKey(City)
    address = CharField(max_length=500)
    pincode = CharField(max_length=10)
    gst_number = CharField(blank=True)
    pan_number = CharField(blank=True)
    business_license = CharField(blank=True)
    bank_account_name = CharField(blank=True)
    bank_account_number = CharField(blank=True)
    bank_ifsc = CharField(blank=True)
    verification_status = CharField(choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ])
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

#### BusOperator
```python
class BusOperator(models.Model):
    operator = ForeignKey(User)
    name = CharField(max_length=200)
    email = EmailField()
    phone = CharField(max_length=20)
    description = TextField()
    gst_number = CharField()
    pan_number = CharField()
    business_license = CharField()
    address = CharField(max_length=500)
    verification_status = CharField(choices=[
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ])
    created_at = DateTimeField(auto_now_add=True)
```

### URL Routes

**Property Owners:**
```
GET  /properties/register/              → registration form
POST /properties/register/              → create account
GET  /properties/dashboard/             → view dashboard
GET  /properties/add-property/          → add property form
POST /properties/add-property/          → create property
GET  /properties/<id>/edit/             → edit property form
POST /properties/<id>/edit/             → update property
GET  /properties/<id>/bookings/         → view bookings
GET  /properties/<id>/booking/<bid>/    → view booking detail
```

**Bus Operators:**
```
GET  /buses/operator/register/          → registration form
POST /buses/operator/register/          → create account + login
GET  /buses/operator/dashboard/         → view dashboard
GET  /buses/add-bus/                    → add bus form
POST /buses/add-bus/                    → create bus
GET  /buses/<id>/routes/                → manage routes
```

### Customization

**Change Registration URL:**
```python
# property_owners/urls.py
path('my-properties/register/', register_property_owner, name='register'),
```

**Modify Form Fields:**
```python
# property_owners/forms.py
class PropertyOwnerRegistrationForm(forms.ModelForm):
    # Add custom fields
    phone_secondary = forms.CharField(required=False)
```

**Customize Dashboard:**
```python
# property_owners/views.py
def property_owner_dashboard(request):
    # Add custom context
    context['custom_data'] = get_custom_data()
    return render(request, 'property_owners/dashboard.html', context)
```

### Testing

**Manual Testing Steps:**
1. Start server: `python manage.py runserver`
2. Visit: `http://localhost:8000`
3. Scroll to "Grow Your Business" section
4. Click "Register as Property Owner"
5. Fill form with test data
6. Submit and verify account creation
7. Repeat for Bus Operator

**Admin Testing:**
1. Go to: `http://localhost:8000/admin/`
2. Login with superuser
3. Navigate to Property Owners app
4. Verify PropertyOwner records created
5. Change verification_status to 'verified'
6. Test dashboard access

### Common Issues & Fixes

**Issue:** Form not loading
- **Fix:** Check `INSTALLED_APPS` includes 'property_owners'
- **Fix:** Verify `urls.py` includes are correct

**Issue:** Template not found error
- **Fix:** Check `TEMPLATES['DIRS']` includes project templates folder
- **Fix:** Verify template files exist in correct folder

**Issue:** Database errors
- **Fix:** Run `python manage.py migrate`
- **Fix:** Check `DATABASES` configuration

**Issue:** Static files missing
- **Fix:** Run `python manage.py collectstatic`
- **Fix:** Check `STATIC_URL` and `STATIC_ROOT` settings

---

## API Integration (Optional)

If you want to expose registration via API:

```python
# In buses/serializers.py or property_owners/serializers.py
from rest_framework import serializers

class PropertyOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOwner
        fields = '__all__'

class BusOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusOperator
        fields = '__all__'
```

Then create viewsets:

```python
from rest_framework.viewsets import ModelViewSet

class PropertyOwnerViewSet(ModelViewSet):
    queryset = PropertyOwner.objects.all()
    serializer_class = PropertyOwnerSerializer
```

---

## Features Checklist

### Property Owner Features
- [x] Self-registration form
- [x] Email validation
- [x] User account creation
- [x] PropertyOwner profile creation
- [x] Account verification workflow
- [x] Dashboard with stats
- [x] Property listing management
- [x] Booking management
- [x] Revenue tracking
- [x] Bank details storage
- [x] Responsive UI
- [x] Bootstrap styling

### Bus Operator Features
- [x] Self-registration form
- [x] Password strength validation
- [x] User account creation
- [x] Auto-login after registration
- [x] BusOperator profile creation
- [x] Account verification workflow
- [x] Dashboard with stats
- [x] Bus management
- [x] Route management
- [x] Booking tracking
- [x] Revenue tracking
- [x] Responsive UI

---

## Support

For issues or questions, contact:
- **Developer Email:** dev@goexplorer.in
- **Support Email:** support@goexplorer.in

---

Last Updated: January 2, 2026  
Status: ✅ Production Ready
