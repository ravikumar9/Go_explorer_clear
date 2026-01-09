/**
 * Booking Utilities - City Autocomplete, Form Validation, Pricing
 * Provides shared utilities for hotel and bus booking pages
 */

// Indian cities database
const INDIAN_CITIES = [
    { name: 'Bangalore', code: 'BLR', state: 'Karnataka' },
    { name: 'Delhi', code: 'DEL', state: 'Delhi' },
    { name: 'Mumbai', code: 'MUM', state: 'Maharashtra' },
    { name: 'Hyderabad', code: 'HYD', state: 'Telangana' },
    { name: 'Chennai', code: 'MAA', state: 'Tamil Nadu' },
    { name: 'Kolkata', code: 'CCU', state: 'West Bengal' },
    { name: 'Pune', code: 'PNQ', state: 'Maharashtra' },
    { name: 'Ahmedabad', code: 'AMD', state: 'Gujarat' },
    { name: 'Jaipur', code: 'JAI', state: 'Rajasthan' },
    { name: 'Chandigarh', code: 'IXC', state: 'Chandigarh' },
    { name: 'Lucknow', code: 'LKO', state: 'Uttar Pradesh' },
    { name: 'Kochi', code: 'COK', state: 'Kerala' },
    { name: 'Indore', code: 'IDR', state: 'Madhya Pradesh' },
    { name: 'Surat', code: 'SUR', state: 'Gujarat' },
    { name: 'Bhopal', code: 'BHO', state: 'Madhya Pradesh' },
];

/**
 * CityAutocomplete - Auto-complete suggestions for city input
 */
class CityAutocomplete {
    constructor(inputElement, suggestionsContainer) {
        this.input = inputElement;
        this.suggestions = suggestionsContainer;
        this.cities = INDIAN_CITIES;

        // Event listeners
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('focus', () => {
            if (this.input.value.length > 0) this.showSuggestions();
        });
    }

    handleInput(e) {
        const value = e.target.value.trim().toLowerCase();
        if (value.length === 0) {
            this.suggestions.style.display = 'none';
            return;
        }

        // Filter cities by name or code
        const filtered = this.cities.filter(city =>
            city.name.toLowerCase().includes(value) ||
            city.code.toLowerCase().includes(value) ||
            city.state.toLowerCase().includes(value)
        );

        // Show top 5 suggestions
        if (filtered.length > 0) {
            this.displaySuggestions(filtered.slice(0, 5));
        } else {
            this.suggestions.innerHTML = '<div class="suggestion-item" style="padding: 10px; color: #999;">No cities found</div>';
            this.suggestions.style.display = 'block';
        }
    }

    displaySuggestions(cities) {
        this.suggestions.innerHTML = '';
        cities.forEach(city => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.innerHTML = `
                <strong>${city.name}</strong>
                <span style="color: #999; font-size: 0.85rem;"> (${city.state})</span>
            `;
            div.style.padding = '10px';
            div.style.cursor = 'pointer';
            div.style.borderBottom = '1px solid #eee';
            div.addEventListener('click', () => {
                this.input.value = city.name;
                this.suggestions.style.display = 'none';
                this.input.dispatchEvent(new Event('change'));
            });
            this.suggestions.appendChild(div);
        });
        this.suggestions.style.display = 'block';
    }

    showSuggestions() {
        if (this.suggestions.innerHTML.trim().length > 0) {
            this.suggestions.style.display = 'block';
        }
    }
}

/**
 * Form Validation Utilities
 */
class FormValidator {
    static validateCities(fromCity, toCity) {
        const errors = [];
        
        if (!fromCity || fromCity.trim() === '') {
            errors.push('Departure city is required');
        }
        if (!toCity || toCity.trim() === '') {
            errors.push('Arrival city is required');
        }
        
        if (fromCity && toCity && fromCity.toLowerCase().trim() === toCity.toLowerCase().trim()) {
            errors.push('Departure and arrival cities must be different');
        }
        
        return errors;
    }

    static validateDate(dateStr) {
        if (!dateStr) return ['Date is required'];
        
        const selectedDate = new Date(dateStr);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        if (selectedDate < today) {
            return ['Travel date cannot be in the past'];
        }
        
        return [];
    }

    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    static validatePhone(phone) {
        const phoneRegex = /^[0-9]{10,15}$/;
        return phoneRegex.test(phone);
    }
}

/**
 * Pricing Calculator
 */
class PricingCalculator {
    static calculate(basePrice, quantity, taxPercentage = 5, feePercentage = 2) {
        const base = basePrice * quantity;
        const fee = base * (feePercentage / 100);
        const tax = (base + fee) * (taxPercentage / 100);
        const total = base + fee + tax;

        return {
            base: Math.round(base),
            fee: Math.round(fee),
            tax: Math.round(tax),
            total: Math.round(total)
        };
    }

    static updateDisplay(basePriceEl, feeEl, taxEl, totalEl, basePrice, quantity, taxPct = 5, feePct = 2) {
        const pricing = this.calculate(basePrice, quantity, taxPct, feePct);
        if (basePriceEl) basePriceEl.textContent = pricing.base;
        if (feeEl) feeEl.textContent = pricing.fee;
        if (taxEl) taxEl.textContent = pricing.tax;
        if (totalEl) totalEl.textContent = pricing.total;
    }
}

/**
 * Date Picker Helper
 */
class DatePickerHelper {
    static setMinDate(inputElement, daysFromNow = 0) {
        const today = new Date();
        today.setDate(today.getDate() + daysFromNow);
        const minDate = today.toISOString().split('T')[0];
        inputElement.setAttribute('min', minDate);
        return minDate;
    }

    static openPicker(inputElement) {
        // Just focus - showPicker() requires user gesture and causes errors
        if (inputElement) {
            inputElement.focus();
        }
    }
}

/**
 * Local Storage Manager (for cart/session data)
 */
class StorageManager {
    static set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('localStorage not available:', e);
        }
    }

    static get(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.warn('Error reading from localStorage:', e);
            return null;
        }
    }

    static clear(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('Error clearing localStorage:', e);
        }
    }
}

/**
 * Modal Helper
 */
class ModalHelper {
    static show(modalElement) {
        if (window.bootstrap && window.bootstrap.Modal) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        } else if (modalElement) {
            modalElement.style.display = 'block';
        }
    }

    static hide(modalElement) {
        if (window.bootstrap && window.bootstrap.Modal) {
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
        } else if (modalElement) {
            modalElement.style.display = 'none';
        }
    }
}

// Export for use in modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        INDIAN_CITIES,
        CityAutocomplete,
        FormValidator,
        PricingCalculator,
        DatePickerHelper,
        StorageManager,
        ModalHelper
    };
}
