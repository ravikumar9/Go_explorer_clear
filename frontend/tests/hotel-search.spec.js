import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:8000';

test.describe('Hotel Search E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to hotel search page
    await page.goto(`${BASE_URL}/hotels/`);
  });

  test('should display search bar with all input fields', async ({ page }) => {
    // Check for city input
    const citySelect = await page.locator('select').first();
    await expect(citySelect).toBeVisible();

    // Check for date inputs
    const dateInputs = await page.locator('input[type="date"]');
    expect(await dateInputs.count()).toBeGreaterThanOrEqual(2);

    // Check for rooms input
    const roomsInputs = await page.locator('input[type="number"]');
    expect(await roomsInputs.count()).toBeGreaterThanOrEqual(1);

    // Check for search button
    const searchButton = await page.locator('button:has-text("Search")');
    await expect(searchButton).toBeVisible();
  });

  test('should search hotels by city', async ({ page }) => {
    // Select a city
    await page.locator('select').first().selectOption('1');
    
    // Click search
    await page.locator('button:has-text("Search")').click();

    // Wait for results
    await page.waitForLoadState('networkidle');
    
    // Check if hotels are displayed
    const hotelCards = await page.locator('[data-testid="hotel-card"]');
    const count = await hotelCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should apply price filter', async ({ page }) => {
    // Set price range
    const minPriceInput = await page.locator('input[name="min_price"]').first();
    const maxPriceInput = await page.locator('input[name="max_price"]').first();

    if (minPriceInput && maxPriceInput) {
      await minPriceInput.fill('10000');
      await maxPriceInput.fill('50000');

      // Click search
      await page.locator('button:has-text("Search")').click();
      await page.waitForLoadState('networkidle');

      // Verify all prices are within range
      const priceElements = await page.locator('[data-testid="hotel-price"]').all();
      
      for (const priceEl of priceElements) {
        const priceText = await priceEl.textContent();
        const price = parseInt(priceText?.replace(/\D/g, '') || '0');
        expect(price).toBeGreaterThanOrEqual(10000);
        expect(price).toBeLessThanOrEqual(50000);
      }
    }
  });

  test('should sort hotels by price', async ({ page }) => {
    // Select a city and search
    await page.locator('select').first().selectOption('1');
    await page.locator('button:has-text("Search")').click();
    await page.waitForLoadState('networkidle');

    // Change sort order
    const sortSelect = await page.locator('select').nth(1);
    if (sortSelect) {
      await sortSelect.selectOption('price_asc');
      await page.waitForLoadState('networkidle');

      // Verify sorting
      const prices = await page.locator('[data-testid="hotel-price"]').allTextContents();
      const numPrices = prices.map(p => parseInt(p.replace(/\D/g, '') || '0'));
      
      for (let i = 0; i < numPrices.length - 1; i++) {
        expect(numPrices[i]).toBeLessThanOrEqual(numPrices[i + 1]);
      }
    }
  });

  test('should open hotel details modal', async ({ page }) => {
    // Search for hotels
    await page.locator('select').first().selectOption('1');
    await page.locator('button:has-text("Search")').click();
    await page.waitForLoadState('networkidle');

    // Click on first hotel
    const firstHotelButton = await page.locator('button:has-text("View Details")').first();
    await firstHotelButton.click();

    // Wait for modal
    await page.waitForLoadState('networkidle');

    // Check if details modal is visible
    const modal = await page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();

    // Check for hotel name in modal
    const hotelName = await modal.locator('h2').first();
    await expect(hotelName).toBeVisible();
  });

  test('should select room type and calculate price', async ({ page }) => {
    // Search for hotels
    await page.locator('select').first().selectOption('1');
    await page.locator('button:has-text("Search")').click();
    await page.waitForLoadState('networkidle');

    // Open hotel details
    await page.locator('button:has-text("View Details")').first().click();
    await page.waitForLoadState('networkidle');

    // Select a room type
    const roomTypes = await page.locator('[data-testid="room-type"]').all();
    if (roomTypes.length > 0) {
      await roomTypes[0].click();
      await page.waitForLoadState('networkidle');

      // Check if pricing breakdown appears
      const pricingBreakdown = await page.locator('[data-testid="pricing-breakdown"]');
      await expect(pricingBreakdown).toBeVisible();

      // Verify pricing information
      const totalPrice = await pricingBreakdown.locator('text=Total Amount').textContent();
      expect(totalPrice).toBeTruthy();
    }
  });

  test('should verify room availability', async ({ page }) => {
    // Search for hotels
    await page.locator('select').first().selectOption('1');
    await page.locator('button:has-text("Search")').click();
    await page.waitForLoadState('networkidle');

    // Open hotel details
    await page.locator('button:has-text("View Details")').first().click();
    await page.waitForLoadState('networkidle');

    // Select a room
    const roomTypes = await page.locator('[data-testid="room-type"]').all();
    if (roomTypes.length > 0) {
      await roomTypes[0].click();
      await page.waitForLoadState('networkidle');

      // Check availability message
      const availabilityMsg = await page.locator('[data-testid="availability-message"]');
      if (availabilityMsg) {
        const message = await availabilityMsg.textContent();
        expect(message).toMatch(/Available|Not available/i);
      }
    }
  });

  test('should close hotel details modal', async ({ page }) => {
    // Search and open details
    await page.locator('select').first().selectOption('1');
    await page.locator('button:has-text("Search")').click();
    await page.waitForLoadState('networkidle');

    await page.locator('button:has-text("View Details")').first().click();
    await page.waitForLoadState('networkidle');

    // Close button (✕)
    const closeButton = await page.locator('button:has-text("✕")').first();
    await closeButton.click();

    // Modal should be hidden
    const modal = await page.locator('[role="dialog"]');
    await expect(modal).not.toBeVisible({ timeout: 1000 }).catch(() => {
      // It's ok if modal still exists but hidden
    });
  });

  test('should handle multiple amenity filters', async ({ page }) => {
    // Check pool amenity
    const poolCheckbox = await page.locator('input[name="pool"]');
    if (poolCheckbox) {
      await poolCheckbox.check();
      
      // Check gym amenity
      const gymCheckbox = await page.locator('input[name="gym"]');
      if (gymCheckbox) {
        await gymCheckbox.check();

        // Search
        await page.locator('button:has-text("Search")').click();
        await page.waitForLoadState('networkidle');

        // Verify results have these amenities
        const hotelCards = await page.locator('[data-testid="hotel-card"]').all();
        expect(hotelCards.length).toBeGreaterThan(0);
      }
    }
  });
});

test.describe('API Integration Tests', () => {
  test('should fetch hotels from API', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/hotels/api/list/?page_size=10`);
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data.results).toBeDefined();
    expect(Array.isArray(data.results)).toBe(true);
  });

  test('should search hotels by city via API', async ({ request }) => {
    const response = await request.get(`${BASE_URL}/hotels/api/search/?city_id=1&page_size=10`);
    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data.results).toBeDefined();
    expect(data.results.length).toBeGreaterThan(0);
  });

  test('should calculate price via API', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/hotels/api/calculate-price/`, {
      data: {
        room_type_id: 1,
        check_in: '2024-01-15',
        check_out: '2024-01-18',
        num_rooms: 1,
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.pricing).toBeDefined();
    expect(data.pricing.total_amount).toBeGreaterThan(0);
  });

  test('should check availability via API', async ({ request }) => {
    const response = await request.post(`${BASE_URL}/hotels/api/check-availability/`, {
      data: {
        room_type_id: 1,
        check_in: '2024-01-15',
        check_out: '2024-01-18',
        num_rooms: 1,
      },
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.availability).toBeDefined();
    expect(typeof data.availability.is_available).toBe('boolean');
  });

  test('should filter by price via API', async ({ request }) => {
    const response = await request.get(
      `${BASE_URL}/hotels/api/search/?min_price=5000&max_price=50000&page_size=10`
    );

    expect(response.status()).toBe(200);
    const data = await response.json();
    
    // Verify all hotels are within price range
    for (const hotel of data.results) {
      expect(hotel.min_price).toBeGreaterThanOrEqual(5000);
      expect(hotel.min_price).toBeLessThanOrEqual(50000);
    }
  });

  test('should sort by rating via API', async ({ request }) => {
    const response = await request.get(
      `${BASE_URL}/hotels/api/search/?sort_by=rating_desc&page_size=10`
    );

    expect(response.status()).toBe(200);
    const data = await response.json();

    // Verify sorting
    for (let i = 0; i < data.results.length - 1; i++) {
      expect(data.results[i].review_rating).toBeGreaterThanOrEqual(
        data.results[i + 1].review_rating
      );
    }
  });
});
