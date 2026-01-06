import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format, addDays, isAfter } from 'date-fns';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * HotelSearch - Main component for hotel search and listing
 * Features:
 * - Sticky search bar
 * - Filter sidebar
 * - Hotel listings with carousel
 * - Sorting options
 * - Price filtering
 */
export default function HotelSearch() {
  // Search parameters
  const [city, setCity] = useState('');
  const [checkIn, setCheckIn] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [checkOut, setCheckOut] = useState(format(addDays(new Date(), 1), 'yyyy-MM-dd'));
  const [rooms, setRooms] = useState(1);
  const [guests, setGuests] = useState(2);

  // Filters
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(100000);
  const [starRating, setStarRating] = useState('');
  const [amenities, setAmenities] = useState({
    wifi: false,
    parking: false,
    pool: false,
    gym: false,
    restaurant: false,
    spa: false,
  });

  // Results
  const [hotels, setHotels] = useState([]);
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sortBy, setSortBy] = useState('name');
  const [page, setPage] = useState(1);

  // State for selected hotel details
  const [selectedHotel, setSelectedHotel] = useState(null);
  const [showHotelDetails, setShowHotelDetails] = useState(false);

  // Fetch cities on mount
  useEffect(() => {
    fetchCities();
  }, []);

  // Fetch cities
  const fetchCities = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/hotels/api/list/?page_size=1`);
      // In real app, would fetch from separate cities endpoint
      setCities([
        { id: 1, name: 'Mumbai' },
        { id: 2, name: 'Delhi' },
        { id: 3, name: 'Bangalore' },
        { id: 4, name: 'Hyderabad' },
        { id: 5, name: 'Goa' },
      ]);
    } catch (error) {
      console.error('Error fetching cities:', error);
    }
  };

  // Fetch hotels based on filters
  const searchHotels = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const params = new URLSearchParams({
        page: page,
        page_size: 10,
        sort_by: sortBy,
        min_price: minPrice,
        max_price: maxPrice,
      });

      if (city) params.append('city_id', city);
      if (starRating) params.append('star_rating', starRating);
      
      Object.entries(amenities).forEach(([key, value]) => {
        if (value) params.append(`has_${key}`, 'true');
      });

      const response = await axios.get(
        `${API_BASE_URL}/hotels/api/search/?${params.toString()}`
      );

      setHotels(response.data.results || []);
    } catch (error) {
      console.error('Error fetching hotels:', error);
      setHotels([]);
    } finally {
      setLoading(false);
    }
  };

  // Get hotel details
  const viewHotelDetails = async (hotelId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/hotels/api/${hotelId}/`);
      setSelectedHotel(response.data);
      setShowHotelDetails(true);
    } catch (error) {
      console.error('Error fetching hotel details:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sticky Search Bar */}
      <SearchBar
        city={city}
        setCity={setCity}
        checkIn={checkIn}
        setCheckIn={setCheckIn}
        checkOut={checkOut}
        setCheckOut={setCheckOut}
        rooms={rooms}
        setRooms={setRooms}
        guests={guests}
        setGuests={setGuests}
        cities={cities}
        onSearch={searchHotels}
      />

      <div className="flex">
        {/* Left Sidebar - Filters */}
        <FilterSidebar
          minPrice={minPrice}
          setMinPrice={setMinPrice}
          maxPrice={maxPrice}
          setMaxPrice={setMaxPrice}
          starRating={starRating}
          setStarRating={setStarRating}
          amenities={amenities}
          setAmenities={setAmenities}
        />

        {/* Main Content */}
        <div className="flex-1 p-6">
          {/* Sorting Options */}
          <div className="mb-6 flex justify-between items-center">
            <h2 className="text-xl font-bold text-gray-800">
              Hotels in {city ? cities.find(c => c.id == city)?.name : 'Select City'}
            </h2>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="name">Sort by Name</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="rating_asc">Rating: Low to High</option>
              <option value="rating_desc">Rating: High to Low</option>
            </select>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          )}

          {/* Hotel Listings */}
          {!loading && hotels.length > 0 && (
            <div className="grid grid-cols-1 gap-6">
              {hotels.map((hotel) => (
                <HotelCard
                  key={hotel.id}
                  hotel={hotel}
                  checkIn={checkIn}
                  checkOut={checkOut}
                  rooms={rooms}
                  onViewDetails={() => viewHotelDetails(hotel.id)}
                />
              ))}
            </div>
          )}

          {/* No Results */}
          {!loading && hotels.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">
                No hotels found. Try adjusting your search filters.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Hotel Details Modal */}
      {showHotelDetails && selectedHotel && (
        <HotelDetailsModal
          hotel={selectedHotel}
          checkIn={checkIn}
          checkOut={checkOut}
          rooms={rooms}
          onClose={() => setShowHotelDetails(false)}
        />
      )}
    </div>
  );
}

/**
 * SearchBar - Sticky search bar component
 */
function SearchBar({
  city,
  setCity,
  checkIn,
  setCheckIn,
  checkOut,
  setCheckOut,
  rooms,
  setRooms,
  guests,
  setGuests,
  cities,
  onSearch,
}) {
  const minDate = format(new Date(), 'yyyy-MM-dd');

  return (
    <div className="sticky top-0 z-40 bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <form onSubmit={onSearch} className="flex gap-4 flex-wrap items-end">
          {/* City Select */}
          <div className="flex-1 min-w-[180px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              City
            </label>
            <select
              value={city}
              onChange={(e) => setCity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a city</option>
              {cities.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* Check-in Date */}
          <div className="flex-1 min-w-[140px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Check-in
            </label>
            <input
              type="date"
              value={checkIn}
              onChange={(e) => setCheckIn(e.target.value)}
              min={minDate}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Check-out Date */}
          <div className="flex-1 min-w-[140px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Check-out
            </label>
            <input
              type="date"
              value={checkOut}
              onChange={(e) => setCheckOut(e.target.value)}
              min={checkIn}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Rooms */}
          <div className="flex-1 min-w-[100px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rooms
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={rooms}
              onChange={(e) => setRooms(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Guests */}
          <div className="flex-1 min-w-[100px]">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Guests
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={guests}
              onChange={(e) => setGuests(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Search Button */}
          <button
            type="submit"
            className="px-8 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Search
          </button>
        </form>
      </div>
    </div>
  );
}

/**
 * FilterSidebar - Left sidebar with filters
 */
function FilterSidebar({
  minPrice,
  setMinPrice,
  maxPrice,
  setMaxPrice,
  starRating,
  setStarRating,
  amenities,
  setAmenities,
}) {
  const handleAmenityChange = (key) => {
    setAmenities({ ...amenities, [key]: !amenities[key] });
  };

  return (
    <div className="w-72 bg-white p-6 shadow-md h-screen overflow-y-auto">
      <h3 className="text-lg font-bold text-gray-800 mb-6">Filters</h3>

      {/* Price Range */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-700 mb-3">Price Range</h4>
        <div className="space-y-2">
          <div>
            <label className="text-sm text-gray-600">Min: ₹{minPrice}</label>
            <input
              type="range"
              min="0"
              max="100000"
              step="1000"
              value={minPrice}
              onChange={(e) => setMinPrice(parseInt(e.target.value))}
              className="w-full"
            />
          </div>
          <div>
            <label className="text-sm text-gray-600">Max: ₹{maxPrice}</label>
            <input
              type="range"
              min="0"
              max="100000"
              step="1000"
              value={maxPrice}
              onChange={(e) => setMaxPrice(parseInt(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      </div>

      {/* Star Rating */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-700 mb-3">Star Rating</h4>
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((rating) => (
            <label key={rating} className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="rating"
                value={rating}
                checked={starRating === String(rating)}
                onChange={(e) => setStarRating(e.target.value)}
                className="w-4 h-4"
              />
              <span className="text-sm text-gray-700">
                {'⭐'.repeat(rating)} {rating} Star
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Amenities */}
      <div>
        <h4 className="font-semibold text-gray-700 mb-3">Amenities</h4>
        <div className="space-y-2">
          {Object.entries(amenities).map(([key, value]) => (
            <label
              key={key}
              className="flex items-center gap-2 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={value}
                onChange={() => handleAmenityChange(key)}
                className="w-4 h-4 rounded"
              />
              <span className="text-sm text-gray-700 capitalize">{key}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * HotelCard - Individual hotel listing card
 */
function HotelCard({ hotel, checkIn, checkOut, rooms, onViewDetails }) {
  const nights = Math.ceil(
    (new Date(checkOut) - new Date(checkIn)) / (1000 * 60 * 60 * 24)
  );
  const totalPrice = (hotel.min_price * nights * rooms).toFixed(0);

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="flex gap-6 p-6">
        {/* Image Carousel */}
        <div className="w-64 h-48 bg-gray-300 rounded-lg overflow-hidden flex-shrink-0">
          {hotel.image ? (
            <img
              src={hotel.image}
              alt={hotel.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gray-400 flex items-center justify-center text-white">
              No Image
            </div>
          )}
        </div>

        {/* Hotel Details */}
        <div className="flex-1">
          <div className="mb-3">
            <h3 className="text-2xl font-bold text-gray-800">{hotel.name}</h3>
            <p className="text-gray-600 text-sm">{hotel.city_name}</p>
          </div>

          {/* Rating */}
          <div className="mb-3">
            <span className="text-yellow-500">{'⭐'.repeat(hotel.star_rating)}</span>
            <span className="ml-2 text-gray-700">
              {hotel.review_rating}/5 ({hotel.review_count} reviews)
            </span>
          </div>

          {/* Amenities */}
          <div className="mb-3 flex flex-wrap gap-2">
            {hotel.amenities?.wifi && (
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                WiFi
              </span>
            )}
            {hotel.amenities?.pool && (
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                Pool
              </span>
            )}
            {hotel.amenities?.parking && (
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                Parking
              </span>
            )}
            {hotel.amenities?.gym && (
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                Gym
              </span>
            )}
          </div>

          {/* Price Info */}
          <div className="bg-gray-50 p-3 rounded-lg mb-3">
            <div className="text-sm text-gray-600 mb-1">
              ₹{hotel.min_price?.toLocaleString()} per night
            </div>
            <div className="text-xl font-bold text-blue-600">
              ₹{totalPrice} for {nights} nights
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {checkIn} to {checkOut} • {rooms} room(s)
            </div>
          </div>

          {/* Action Button */}
          <button
            onClick={onViewDetails}
            className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            View Details & Book
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * HotelDetailsModal - Modal for viewing hotel details
 */
function HotelDetailsModal({ hotel, checkIn, checkOut, rooms, onClose }) {
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [availability, setAvailability] = useState(null);

  useEffect(() => {
    if (selectedRoom) {
      checkAvailability(selectedRoom.id);
      calculatePrice(selectedRoom.id);
    }
  }, [selectedRoom]);

  const checkAvailability = async (roomTypeId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/hotels/api/check-availability/`, {
        room_type_id: roomTypeId,
        check_in: checkIn,
        check_out: checkOut,
        num_rooms: rooms,
      });
      setAvailability(response.data.availability);
    } catch (error) {
      console.error('Error checking availability:', error);
    }
  };

  const calculatePrice = async (roomTypeId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/hotels/api/calculate-price/`, {
        room_type_id: roomTypeId,
        check_in: checkIn,
        check_out: checkOut,
        num_rooms: rooms,
      });
      setPricing(response.data.pricing);
    } catch (error) {
      console.error('Error calculating price:', error);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">{hotel.name}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ✕
          </button>
        </div>

        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Hotel Info */}
          <div>
            <img
              src={hotel.image}
              alt={hotel.name}
              className="w-full h-64 object-cover rounded-lg mb-4"
            />
            <p className="text-gray-600 mb-4">{hotel.description}</p>
            <div className="mb-4">
              <p className="text-gray-700">
                <strong>Address:</strong> {hotel.address}
              </p>
              <p className="text-gray-700">
                <strong>Check-in:</strong> {hotel.checkin_time}
              </p>
              <p className="text-gray-700">
                <strong>Check-out:</strong> {hotel.checkout_time}
              </p>
            </div>
          </div>

          {/* Room Selection & Pricing */}
          <div>
            <h3 className="text-xl font-bold text-gray-800 mb-4">Select Room Type</h3>
            <div className="space-y-3 mb-6">
              {hotel.room_types?.map((room) => (
                <div
                  key={room.id}
                  onClick={() => setSelectedRoom(room)}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedRoom?.id === room.id
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <h4 className="font-semibold text-gray-800">{room.name}</h4>
                  <p className="text-sm text-gray-600">{room.description}</p>
                  <p className="text-sm text-gray-600">
                    Max occupancy: {room.max_occupancy} • {room.number_of_beds} bed(s)
                  </p>
                  <p className="text-lg font-bold text-blue-600 mt-2">
                    ₹{room.base_price?.toLocaleString()}/night
                  </p>
                </div>
              ))}
            </div>

            {/* Pricing Breakdown */}
            {pricing && (
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <h4 className="font-bold text-gray-800 mb-3">Price Breakdown</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Base Price (per night):</span>
                    <span>₹{pricing.base_price?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Nights × Rooms:</span>
                    <span>{pricing.num_nights} × {pricing.num_rooms}</span>
                  </div>
                  <div className="flex justify-between font-semibold border-t pt-2">
                    <span>Subtotal:</span>
                    <span>₹{pricing.subtotal?.toLocaleString()}</span>
                  </div>
                  {pricing.discount_amount > 0 && (
                    <div className="flex justify-between text-green-600">
                      <span>Discount:</span>
                      <span>-₹{pricing.discount_amount?.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>GST ({pricing.gst_percentage}%):</span>
                    <span>₹{pricing.gst_amount?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-lg font-bold border-t pt-2 text-blue-600">
                    <span>Total Amount:</span>
                    <span>₹{pricing.total_amount?.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Availability Info */}
            {availability && (
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <h4 className="font-bold text-gray-800 mb-2">Availability</h4>
                {availability.is_available ? (
                  <p className="text-green-600 font-semibold">
                    ✓ Available for your dates
                  </p>
                ) : (
                  <p className="text-red-600 font-semibold">
                    ✗ Not available for selected dates
                  </p>
                )}
              </div>
            )}

            <button
              disabled={!selectedRoom || !availability?.is_available}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Book Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
