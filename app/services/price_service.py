import os
from datetime import datetime
from typing import Optional
from decimal import Decimal, ROUND_DOWN
import httpx
from app.schemas.price import (
    PriceCalculationRequest,
    PriceCalculationResponse,
    PriceBreakdown,
    RiderPriceRequest,
    RiderPriceResponse
)

# Constants for price calculation
# These values should be updated regularly based on market conditions
GAS_PRICE_PER_GALLON = 3.50  # Current US average gas price
AVERAGE_CAR_MPG = 25  # Average miles per gallon
INSURANCE_COST_PER_MILE = 0.15  # Insurance cost per mile
MAINTENANCE_COST_PER_MILE = 0.10  # Maintenance cost per mile (oil, tires, etc.)
DEPRECIATION_COST_PER_MILE = 0.08  # Vehicle depreciation per mile
DRIVER_PROFIT_MARGIN = 0.20  # 20% profit margin for drivers
PLATFORM_PROFIT_MARGIN = 0.05  # 5% platform profit margin
STRIPE_PROCESSING_FEE = 0.029  # 2.9% Stripe processing fee
STRIPE_FIXED_FEE = 0.30  # $0.30 fixed fee per transaction

# Minimum and maximum prices
MIN_PRICE_PER_MILE = 0.25  # Minimum price per mile
MAX_PRICE_PER_MILE = 0.45  # Maximum price per mile

async def get_current_gas_price() -> float:
    """
    Get current gas price from an API
    You can use APIs like GasBuddy, AAA, or other fuel price APIs
    """
    # TODO: Implement actual gas price API integration
    # For now, return the default value
    return GAS_PRICE_PER_GALLON

async def calculate_base_price_per_mile() -> float:
    """
    Calculate the base price per mile based on current costs
    """
    # Calculate fuel cost per mile
    fuel_cost_per_mile = GAS_PRICE_PER_GALLON / AVERAGE_CAR_MPG
    
    # Calculate total cost per mile
    total_cost_per_mile = (
        fuel_cost_per_mile +
        INSURANCE_COST_PER_MILE +
        MAINTENANCE_COST_PER_MILE +
        DEPRECIATION_COST_PER_MILE
    )
    
    # Add driver profit margin
    price_with_profit = total_cost_per_mile * (1 + DRIVER_PROFIT_MARGIN)
    
    # Add platform profit margin
    final_price = price_with_profit * (1 + PLATFORM_PROFIT_MARGIN)
    
    # Ensure price is within bounds
    final_price = max(MIN_PRICE_PER_MILE, min(MAX_PRICE_PER_MILE, final_price))
    
    return round(final_price, 2)

async def calculate_ride_price(
    request: PriceCalculationRequest
) -> PriceCalculationResponse:
    """
    Calculate the total price for a ride based on various factors
    """
    try:
        # Get current gas price if not provided
        current_gas_price = request.current_gas_price or await get_current_gas_price()
        
        # Calculate base price per mile
        base_price_per_mile = await calculate_base_price_per_mile()
        
        # Calculate base price
        base_price = request.distance_miles * base_price_per_mile
        
        # Add additional costs for stops
        stop_fee = request.number_of_stops * 2.00  # $2 per additional stop
        
        # Add time-based fee for longer trips
        time_fee = max(0, (request.duration_minutes - 60) * 0.25)  # $0.25 per minute after 1 hour
        
        # Calculate subtotal before fees
        subtotal = base_price + stop_fee + time_fee
        
        # Apply discount for recurring rides
        if request.is_recurring:
            subtotal *= 0.90  # 10% discount for recurring rides
        
        # Calculate Stripe processing fees
        stripe_percentage_fee = subtotal * STRIPE_PROCESSING_FEE
        stripe_fixed_fee = STRIPE_FIXED_FEE
        total_stripe_fees = stripe_percentage_fee + stripe_fixed_fee
        
        # Calculate total price including all fees
        total_price = subtotal + total_stripe_fees
        
        # Round to 2 decimal places
        total_price = float(Decimal(str(total_price)).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
        
        # Calculate platform profit (separate from Stripe fees)
        platform_profit = subtotal * PLATFORM_PROFIT_MARGIN
        
        # Calculate driver earnings (before platform profit)
        driver_earnings = subtotal - platform_profit
        
        price_breakdown = PriceBreakdown(
            total_price=total_price,
            base_price=base_price,
            stop_fee=stop_fee,
            time_fee=time_fee,
            platform_fee=platform_profit,  # This is now our actual profit
            driver_earnings=driver_earnings,
            price_per_mile=total_price / request.distance_miles,
            stripe_fees=total_stripe_fees  # Added stripe fees to breakdown
        )
        
        return PriceCalculationResponse(
            status="OK",
            price_breakdown=price_breakdown
        )
        
    except Exception as e:
        return PriceCalculationResponse(
            status="ERROR",
            price_breakdown=PriceBreakdown(
                total_price=0,
                base_price=0,
                stop_fee=0,
                time_fee=0,
                platform_fee=0,
                driver_earnings=0,
                price_per_mile=0,
                stripe_fees=0
            ),
            error_message=str(e)
        )

async def calculate_price_per_rider(
    request: RiderPriceRequest
) -> RiderPriceResponse:
    """
    Calculate the price per rider when splitting the cost
    """
    try:
        if request.number_of_riders <= 0:
            return RiderPriceResponse(
                price_per_rider=request.total_price
            )
        
        # Driver pays 20% of the total price
        driver_contribution = request.total_price * 0.20
        remaining_amount = request.total_price - driver_contribution
        
        # Split remaining amount among riders
        price_per_rider = remaining_amount / request.number_of_riders
        
        # Round to 2 decimal places
        price_per_rider = float(Decimal(str(price_per_rider)).quantize(Decimal('0.01'), rounding=ROUND_DOWN))
        
        return RiderPriceResponse(
            price_per_rider=price_per_rider
        )
        
    except Exception as e:
        return RiderPriceResponse(
            price_per_rider=0,
            error_message=str(e)
        ) 
