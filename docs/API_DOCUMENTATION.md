# GoExplorer API Documentation

## Base URL
```
Development: http://127.0.0.1:8000
Production: https://goexplorer.in
```

## Authentication
Most endpoints are public. User-specific endpoints require authentication via Django session or token.

---

## Hotels API

### List Hotels
```http
GET /api/hotels/
```

**Query Parameters:**
- `city` (integer): Filter by city ID
- `star_rating` (integer): Filter by star rating (1-5)
- `is_featured` (boolean): Filter featured hotels
- `search` (string): Search in name, description, city name
- `ordering` (string): Order by field (e.g., `-review_rating`, `name`)

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Grand Hotel",
      "city": 1,
      "city_name": "Delhi",
      "address": "123 Main Street",
      "star_rating": 5,
      "review_rating": "4.50",
      "review_count": 120,
      "image": "/media/hotels/hotel1.jpg",
      "is_featured": true
    }
  ]
}
```

### Search Hotels
```http
GET /api/hotels/search/?city=1&checkin=2024-01-15&checkout=2024-01-18
```

### Get Hotel Details
```http
GET /api/hotels/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Grand Hotel",
  "description": "Luxury hotel in the heart of Delhi",
  "city": 1,
  "city_name": "Delhi",
  "address": "123 Main Street",
  "latitude": "28.6139",
  "longitude": "77.2090",
  "star_rating": 5,
  "review_rating": "4.50",
  "review_count": 120,
  "image": "/media/hotels/hotel1.jpg",
  "images": [
    {"id": 1, "image": "/media/hotels/gallery/1.jpg", "caption": "Lobby", "is_primary": true}
  ],
  "has_wifi": true,
  "has_parking": true,
  "has_pool": true,
  "has_gym": true,
  "has_restaurant": true,
  "has_spa": false,
  "has_ac": true,
  "checkin_time": "14:00",
  "checkout_time": "11:00",
  "contact_phone": "+91-1234567890",
  "contact_email": "info@grandhotel.com",
  "room_types": [
    {
      "id": 1,
      "name": "Deluxe Room",
      "room_type": "deluxe",
      "description": "Spacious deluxe room",
      "max_occupancy": 2,
      "number_of_beds": 1,
      "room_size": 350,
      "base_price": "5000.00",
      "has_balcony": true,
      "has_tv": true,
      "has_minibar": true,
      "has_safe": true,
      "total_rooms": 20,
      "is_available": true,
      "image": "/media/hotels/rooms/deluxe.jpg"
    }
  ],
  "is_featured": true
}
```

---

## Buses API

### Search Buses
```http
GET /api/buses/search/?source=1&destination=2&date=2024-01-15
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "route": {
        "id": 1,
        "bus": {
          "id": 1,
          "operator": {
            "id": 1,
            "name": "RedBus Express",
            "logo": "/media/buses/operators/redbus.png",
            "rating": "4.20"
          },
          "bus_number": "MH01AB1234",
          "bus_name": "Express Service",
          "bus_type": "ac_sleeper",
          "total_seats": 40,
          "has_ac": true,
          "has_wifi": true,
          "has_charging_point": true,
          "has_blanket": true,
          "has_water_bottle": true,
          "has_tv": false
        },
        "route_name": "Delhi to Mumbai Express",
        "source_city": 1,
        "source_city_name": "Delhi",
        "destination_city": 2,
        "destination_city_name": "Mumbai",
        "departure_time": "22:00:00",
        "arrival_time": "10:00:00",
        "duration_hours": "12.00",
        "distance_km": "1400.00",
        "base_fare": "1200.00"
      },
      "date": "2024-01-15",
      "available_seats": 32,
      "fare": "1200.00",
      "is_active": true
    }
  ]
}
```

### List Bus Routes
```http
GET /api/buses/routes/
```

### Get Route Details
```http
GET /api/buses/routes/{id}/
```

---

## Packages API

### List Packages
```http
GET /api/packages/
```

**Query Parameters:**
- `package_type` (string): Filter by type (adventure, beach, cultural, etc.)
- `is_featured` (boolean): Featured packages
- `search` (string): Search in name, description
- `ordering` (string): Order by field

**Response:**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "name": "Goa Beach Paradise",
      "package_type": "beach",
      "duration_days": 5,
      "duration_nights": 4,
      "starting_price": "15000.00",
      "image": "/media/packages/goa.jpg",
      "is_featured": true,
      "rating": "4.70",
      "review_count": 85
    }
  ]
}
```

### Search Packages
```http
GET /api/packages/search/?type=beach&min_price=10000&max_price=20000&duration=5
```

### Get Package Details
```http
GET /api/packages/{id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Goa Beach Paradise",
  "description": "Enjoy the sun, sand, and sea in beautiful Goa",
  "package_type": "beach",
  "destination_cities": [3],
  "destination_city_names": ["Goa"],
  "duration_days": 5,
  "duration_nights": 4,
  "starting_price": "15000.00",
  "image": "/media/packages/goa.jpg",
  "images": [
    {"id": 1, "image": "/media/packages/gallery/goa1.jpg", "caption": "Beach", "is_primary": true}
  ],
  "includes_hotel": true,
  "includes_transport": true,
  "includes_meals": true,
  "includes_sightseeing": true,
  "includes_guide": true,
  "breakfast_included": true,
  "lunch_included": false,
  "dinner_included": true,
  "max_group_size": 20,
  "min_group_size": 2,
  "is_featured": true,
  "rating": "4.70",
  "review_count": 85,
  "itinerary": [
    {
      "id": 1,
      "day_number": 1,
      "title": "Arrival & Beach Visit",
      "description": "Check-in at hotel and visit Baga Beach",
      "activities": "Swimming, Beach Sports, Sunset View",
      "meals_included": "Dinner",
      "accommodation": "Beach Resort"
    }
  ],
  "departures": [
    {
      "id": 1,
      "departure_date": "2024-02-01",
      "return_date": "2024-02-05",
      "available_slots": 15,
      "price_per_person": "15000.00",
      "is_active": true
    }
  ]
}
```

---

## Bookings API

### List User Bookings
```http
GET /api/bookings/
```
**Requires:** Authentication

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "booking_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
      "booking_type": "hotel",
      "status": "confirmed",
      "total_amount": "10000.00",
      "paid_amount": "10000.00",
      "customer_name": "John Doe",
      "customer_email": "john@example.com",
      "customer_phone": "+919876543210",
      "created_at": "2024-01-10T10:30:00Z"
    }
  ]
}
```

### Get Booking Details
```http
GET /api/bookings/{booking_id}/
```
**Requires:** Authentication

---

## Payments API

### Create Payment Order
```http
POST /api/payments/create-order/
```
**Requires:** Authentication

**Request Body:**
```json
{
  "booking_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
  "amount": "10000.00"
}
```

**Response:**
```json
{
  "order_id": "order_xyz123",
  "amount": "10000.00",
  "currency": "INR",
  "key": "rzp_test_1234567890"
}
```

### Verify Payment
```http
POST /api/payments/verify/
```
**Requires:** Authentication

**Request Body:**
```json
{
  "razorpay_order_id": "order_xyz123",
  "razorpay_payment_id": "pay_abc456",
  "razorpay_signature": "signature_string"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment verified successfully"
}
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error description"
}
```

**HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limiting

API rate limits (when enabled):
- Anonymous: 100 requests/hour
- Authenticated: 1000 requests/hour

---

## Pagination

List endpoints support pagination:
- Default page size: 20
- Query parameter: `?page=2`
- Custom page size: `?page_size=50` (max 100)

---

## Testing

Use the following test credentials for payments:

**Razorpay Test Cards:**
- Card: 4111 1111 1111 1111
- CVV: 123
- Expiry: Any future date
- OTP: 000000

**Test UPI:**
- UPI: success@razorpay

---

For more information, visit: https://github.com/ravikumar9/Go_explorer_clear
