import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * HotelSearchTest - Component for E2E and integration testing
 */
export default function HotelSearchTest() {
  const [testResults, setTestResults] = useState([]);
  const [isRunning, setIsRunning] = useState(false);

  const runTests = async () => {
    setIsRunning(true);
    const results = [];

    try {
      // Test 1: Search hotels by city
      const test1 = await testSearchHotelsByCity();
      results.push(test1);

      // Test 2: Apply price filter
      const test2 = await testPriceFilter();
      results.push(test2);

      // Test 3: Sort by price
      const test3 = await testSortByPrice();
      results.push(test3);

      // Test 4: Check pricing calculation
      const test4 = await testPricingCalculation();
      results.push(test4);

      // Test 5: Check availability
      const test5 = await testAvailabilityCheck();
      results.push(test5);

      // Test 6: Get hotel details
      const test6 = await testHotelDetails();
      results.push(test6);

      setTestResults(results);
    } catch (error) {
      console.error('Test error:', error);
    }

    setIsRunning(false);
  };

  // Test Cases
  const testSearchHotelsByCity = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/hotels/api/search/?city_id=1&page_size=5`
      );

      const passed =
        response.status === 200 &&
        Array.isArray(response.data.results) &&
        response.data.results.length > 0;

      return {
        name: 'Search Hotels by City',
        passed,
        message: passed
          ? `✓ Found ${response.data.results.length} hotels`
          : '✗ No hotels found',
      };
    } catch (error) {
      return {
        name: 'Search Hotels by City',
        passed: false,
        message: `✗ Error: ${error.message}`,
      };
    }
  };

  const testPriceFilter = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/hotels/api/search/?min_price=10000&max_price=50000&page_size=5`
      );

      const allInRange = response.data.results.every(
        (h) => h.min_price >= 10000 && h.min_price <= 50000
      );

      const passed = response.status === 200 && allInRange;

      return {
        name: 'Price Filter',
        passed,
        message: passed
          ? '✓ All hotels within price range'
          : '✗ Price filter not working',
      };
    } catch (error) {
      return {
        name: 'Price Filter',
        passed: false,
        message: `✗ Error: ${error.message}`,
      };
    }
  };

  const testSortByPrice = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/hotels/api/search/?sort_by=price_asc&page_size=10`
      );

      const hotels = response.data.results;
      let isSorted = true;

      for (let i = 0; i < hotels.length - 1; i++) {
        if (hotels[i].min_price > hotels[i + 1].min_price) {
          isSorted = false;
          break;
        }
      }

      return {
        name: 'Sort by Price',
        passed: response.status === 200 && isSorted,
        message: isSorted
          ? '✓ Hotels correctly sorted by price'
          : '✗ Sorting not working',
      };
    } catch (error) {
      return {
        name: 'Sort by Price',
        passed: false,
        message: `✗ Error: ${error.message}`,
      };
    }
  };

  const testPricingCalculation = async () => {
    try {
      // First, get a hotel to get a room type ID
      const hotelResponse = await axios.get(
        `${API_BASE_URL}/hotels/api/search/?page_size=1`
      );

      if (hotelResponse.data.results.length === 0) {
        return {
          name: 'Pricing Calculation',
          passed: false,
          message: '✗ No hotels found for testing',
        };
      }

      const hotelId = hotelResponse.data.results[0].id;
      const hotelDetail = await axios.get(
        `${API_BASE_URL}/hotels/api/${hotelId}/`
      );

      if (!hotelDetail.data.room_types?.length) {
        return {
          name: 'Pricing Calculation',
          passed: false,
          message: '✗ No room types found',
        };
      }

      const roomTypeId = hotelDetail.data.room_types[0].id;

      // Calculate price
      const pricingResponse = await axios.post(
        `${API_BASE_URL}/hotels/api/calculate-price/`,
        {
          room_type_id: roomTypeId,
          check_in: '2024-01-15',
          check_out: '2024-01-18',
          num_rooms: 2,
        }
      );

      const pricing = pricingResponse.data.pricing;
      const passed =
        pricingResponse.status === 200 &&
        pricing.num_nights === 3 &&
        pricing.num_rooms === 2 &&
        pricing.total_amount > 0;

      return {
        name: 'Pricing Calculation',
        passed,
        message: passed
          ? `✓ Price calculated: ₹${pricing.total_amount?.toLocaleString()}`
          : '✗ Pricing calculation failed',
      };
    } catch (error) {
      return {
        name: 'Pricing Calculation',
        passed: false,
        message: `✗ Error: ${error.message}`,
      };
    }
  };

  const testAvailabilityCheck = async () => {
    try {
      const hotelResponse = await axios.get(
        `${API_BASE_URL}/hotels/api/search/?page_size=1`
      );

      if (hotelResponse.data.results.length === 0) {
        return {
          name: 'Availability Check',
          passed: false,
          message: '✗ No hotels found for testing',
        };
      }

      const hotelId = hotelResponse.data.results[0].id;
      const hotelDetail = await axios.get(
        `${API_BASE_URL}/hotels/api/${hotelId}/`
      );

      if (!hotelDetail.data.room_types?.length) {
        return {
          name: 'Availability Check',
          passed: false,
          message: '✗ No room types found',
        };
      }

      const roomTypeId = hotelDetail.data.room_types[0].id;

      const availabilityResponse = await axios.post(
        `${API_BASE_URL}/hotels/api/check-availability/`,
        {
          room_type_id: roomTypeId,
          check_in: '2024-01-15',
          check_out: '2024-01-18',
          num_rooms: 1,
        }
      );

      const passed =
        availabilityResponse.status === 200 &&
        availabilityResponse.data.availability;

      return {
        name: 'Availability Check',
        passed,
        message: passed
          ? '✓ Availability check working'
          : '✗ Availability check failed',
      };
    } catch (error) {
      return {
        name: 'Availability Check',
        passed: false,
        message: `✗ Error: ${error.message}`,
      };
    }
  };

  const testHotelDetails = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/hotels/api/search/?page_size=1`
      );

      if (response.data.results.length === 0) {
        return {
          name: 'Hotel Details',
          passed: false,
          message: '✗ No hotels found',
        };
      }

      const hotelId = response.data.results[0].id;
      const detailResponse = await axios.get(
        `${API_BASE_URL}/hotels/api/${hotelId}/`
      );

      const passed =
        detailResponse.status === 200 &&
        detailResponse.data.name &&
        Array.isArray(detailResponse.data.room_types);

      return {
        name: 'Hotel Details',
        passed,
        message: passed
          ? `✓ Hotel details loaded: ${detailResponse.data.name}`
          : '✗ Hotel details not loading',
      };
    } catch (error) {
      return {
        name: 'Hotel Details',
        passed: false,
        message: `✗ Error: ${error.message}`,
      };
    }
  };

  const passedCount = testResults.filter((r) => r.passed).length;
  const totalCount = testResults.length;

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Hotel Search - E2E Tests
        </h1>

        <button
          onClick={runTests}
          disabled={isRunning}
          className="mb-8 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
        >
          {isRunning ? 'Running Tests...' : 'Run Tests'}
        </button>

        {testResults.length > 0 && (
          <>
            <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-lg font-semibold text-blue-800">
                {passedCount} of {totalCount} tests passed
                {passedCount === totalCount && ' ✓ All tests passed!'}
              </p>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all"
                  style={{ width: `${(passedCount / totalCount) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="space-y-3">
              {testResults.map((result, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${
                    result.passed
                      ? 'bg-green-50 border-green-500'
                      : 'bg-red-50 border-red-500'
                  }`}
                >
                  <h3 className="font-semibold text-gray-800">
                    {result.passed ? '✓' : '✗'} {result.name}
                  </h3>
                  <p className="text-gray-600 mt-1">{result.message}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
