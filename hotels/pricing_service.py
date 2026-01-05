"""
Hotel Pricing Service
Handles complex pricing calculations with taxes, discounts, and surcharges
"""

from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from .models import RoomAvailability, HotelDiscount, Hotel


class PricingCalculator:
    """Main pricing calculator for hotels"""
    
    def __init__(self, hotel: Hotel):
        self.hotel = hotel
        self.gst_rate = hotel.gst_percentage / Decimal('100')
    
    def get_room_price(self, room_type, check_in: date, check_out: date) -> Decimal:
        """
        Get base price for room for given dates
        Returns average price if multiple dates or base price
        """
        availability_records = RoomAvailability.objects.filter(
            room_type=room_type,
            date__gte=check_in,
            date__lt=check_out
        ).order_by('date')
        
        if not availability_records.exists():
            # If no availability records, use base price
            return room_type.base_price
        
        # Calculate average price for stay duration
        total_price = sum(rec.price for rec in availability_records)
        nights = (check_out - check_in).days
        
        return total_price / Decimal(str(nights)) if nights > 0 else room_type.base_price
    
    def calculate_total_price(
        self,
        room_type,
        check_in: date,
        check_out: date,
        num_rooms: int = 1,
        discount_code: Optional[str] = None
    ) -> Dict:
        """
        Calculate total price with all taxes, discounts and fees
        
        Returns:
            {
                'base_price': float,          # Per night base price
                'num_nights': int,
                'subtotal': float,            # Base price * nights * rooms
                'discount_amount': float,
                'subtotal_after_discount': float,
                'gst_amount': float,
                'total_amount': float,
                'tax_breakdown': {},
                'discount_details': {},
                'currency': 'INR'
            }
        """
        nights = (check_out - check_in).days
        if nights <= 0:
            raise ValueError("Check-out date must be after check-in date")
        
        # Get base price per night
        base_price = self.get_room_price(room_type, check_in, check_out)
        
        # Calculate subtotal
        subtotal = base_price * Decimal(str(num_rooms)) * Decimal(str(nights))
        
        # Apply discount
        discount_info = {}
        discount_amount = Decimal('0.00')
        
        if discount_code:
            discount_amount, discount_info = self._apply_discount(
                discount_code, subtotal
            )
        
        subtotal_after_discount = subtotal - discount_amount
        
        # Calculate GST (on final amount after discount)
        gst_amount = subtotal_after_discount * self.gst_rate
        
        # Total amount
        total_amount = subtotal_after_discount + gst_amount
        
        return {
            'base_price': float(base_price),
            'num_nights': nights,
            'num_rooms': num_rooms,
            'subtotal': float(subtotal),
            'discount_amount': float(discount_amount),
            'subtotal_after_discount': float(subtotal_after_discount),
            'gst_amount': float(gst_amount),
            'gst_percentage': float(self.hotel.gst_percentage),
            'total_amount': float(total_amount),
            'discount_details': discount_info,
            'currency': 'INR',
            'breakdown': {
                'base_price_per_night': float(base_price),
                'base_price_x_nights': float(base_price * Decimal(str(nights))),
                'base_price_x_nights_x_rooms': float(subtotal),
                'discount': float(discount_amount),
                'gst': float(gst_amount),
            }
        }
    
    def _apply_discount(self, code: str, amount: Decimal) -> Tuple[Decimal, Dict]:
        """Apply discount code and return discount amount and details"""
        try:
            discount = HotelDiscount.objects.get(
                code=code,
                hotel=self.hotel,
                is_active=True
            )
            
            if not discount.is_valid():
                return Decimal('0.00'), {'error': 'Discount code has expired'}
            
            discount_amount = discount.calculate_discount(amount)
            
            return discount_amount, {
                'code': code,
                'description': discount.description,
                'discount_type': discount.discount_type,
                'discount_value': float(discount.discount_value),
                'discount_amount': float(discount_amount),
                'is_valid': True
            }
        except HotelDiscount.DoesNotExist:
            return Decimal('0.00'), {'error': 'Invalid discount code', 'is_valid': False}
    
    def check_availability(
        self,
        room_type,
        check_in: date,
        check_out: date,
        num_rooms: int = 1
    ) -> Dict:
        """Check if room is available for dates"""
        availability_records = RoomAvailability.objects.filter(
            room_type=room_type,
            date__gte=check_in,
            date__lt=check_out
        ).order_by('date')
        
        if not availability_records.exists():
            return {
                'is_available': True,
                'reason': 'No specific availability records, room may be available',
                'min_available_rooms': None
            }
        
        min_available = min(rec.available_rooms for rec in availability_records)
        is_available = min_available >= num_rooms
        
        return {
            'is_available': is_available,
            'min_available_rooms': min_available,
            'required_rooms': num_rooms,
            'available_by_date': [
                {
                    'date': rec.date.isoformat(),
                    'available_rooms': rec.available_rooms,
                    'price': float(rec.price)
                }
                for rec in availability_records
            ]
        }
    
    def get_dynamic_price_multiplier(self, check_in: date) -> Decimal:
        """
        Get dynamic pricing multiplier based on check-in date
        Peak season, weekend, etc.
        """
        # Simple implementation: weekend multiplier
        day_of_week = check_in.weekday()
        
        if day_of_week >= 4:  # Friday, Saturday
            return Decimal('1.2')  # 20% peak price
        
        return Decimal('1.0')  # Normal price
    
    def get_price_history(self, room_type, start_date: date, end_date: date) -> List[Dict]:
        """Get price history for a room type for date range"""
        records = RoomAvailability.objects.filter(
            room_type=room_type,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        return [
            {
                'date': rec.date.isoformat(),
                'price': float(rec.price),
                'available_rooms': rec.available_rooms
            }
            for rec in records
        ]


class BulkPricingCalculator:
    """Calculate prices for multiple rooms/dates"""
    
    def __init__(self, hotel: Hotel):
        self.calculator = PricingCalculator(hotel)
        self.hotel = hotel
    
    def calculate_multi_room_prices(
        self,
        room_configs: List[Dict]
    ) -> Dict:
        """
        Calculate total price for multiple room configurations
        
        room_configs: [
            {
                'room_type_id': int,
                'check_in': '2024-01-10',
                'check_out': '2024-01-15',
                'num_rooms': 2
            }
        ]
        """
        total_breakdown = {
            'total_amount': 0,
            'total_gst': 0,
            'total_discount': 0,
            'rooms': []
        }
        
        for config in room_configs:
            from .models import RoomType
            room_type = RoomType.objects.get(id=config['room_type_id'])
            
            pricing = self.calculator.calculate_total_price(
                room_type,
                date.fromisoformat(config['check_in']),
                date.fromisoformat(config['check_out']),
                num_rooms=config.get('num_rooms', 1),
                discount_code=config.get('discount_code')
            )
            
            total_breakdown['rooms'].append(pricing)
            total_breakdown['total_amount'] += pricing['total_amount']
            total_breakdown['total_gst'] += pricing['gst_amount']
            total_breakdown['total_discount'] += pricing['discount_amount']
        
        return total_breakdown


class OccupancyCalculator:
    """Calculate occupancy rates for hotels"""
    
    @staticmethod
    def calculate_occupancy(
        room_type,
        check_in: date,
        check_out: date
    ) -> float:
        """Calculate occupancy percentage for room type"""
        availability_records = RoomAvailability.objects.filter(
            room_type=room_type,
            date__gte=check_in,
            date__lt=check_out
        )
        
        if not availability_records.exists():
            return 0.0
        
        total_rooms = availability_records.count() * room_type.total_rooms
        available_rooms = sum(rec.available_rooms for rec in availability_records)
        booked_rooms = total_rooms - available_rooms
        
        occupancy_pct = (booked_rooms / total_rooms * 100) if total_rooms > 0 else 0.0
        return occupancy_pct
    
    @staticmethod
    def get_hotel_occupancy_summary(hotel: Hotel, start_date: date, end_date: date) -> Dict:
        """Get occupancy summary for entire hotel"""
        room_types = hotel.room_types.all()
        
        total_rooms = sum(rt.total_rooms for rt in room_types)
        total_available = 0
        
        availability_records = RoomAvailability.objects.filter(
            room_type__hotel=hotel,
            date__gte=start_date,
            date__lte=end_date
        )
        
        for record in availability_records:
            total_available += record.available_rooms
        
        total_rooms_available = total_rooms * (end_date - start_date).days
        booked_rooms = total_rooms_available - total_available
        
        occupancy_pct = (booked_rooms / total_rooms_available * 100) if total_rooms_available > 0 else 0.0
        
        return {
            'hotel_id': hotel.id,
            'hotel_name': hotel.name,
            'occupancy_percentage': round(occupancy_pct, 2),
            'total_available_capacity': total_rooms_available,
            'booked_rooms': booked_rooms,
            'available_rooms': total_available,
            'period_start': start_date.isoformat(),
            'period_end': end_date.isoformat(),
        }
