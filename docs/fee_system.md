# NeedARide Fee System Documentation

## Overview

NeedARide uses a transparent fee structure that ensures fair compensation for drivers while maintaining sustainable platform operations. This document outlines how fees are calculated and distributed.

## Base Price Components

### Operational Costs (per mile)

- **Fuel Cost**: Based on current gas prices and vehicle efficiency

  - Default gas price: $3.50/gallon
  - Average vehicle efficiency: 25 MPG
  - Cost per mile: $0.14

- **Insurance**: $0.15 per mile
- **Maintenance**: $0.10 per mile (oil, tires, etc.)
- **Vehicle Depreciation**: $0.08 per mile

### Additional Fees

- **Stop Fee**: $2.00 per additional stop
- **Time Fee**: $0.25 per minute after 1 hour
- **Recurring Ride Discount**: 10% off for recurring rides

## Fee Distribution

### Driver Earnings

- **Profit Margin**: 20% of the subtotal (before platform fees)
- **Earnings Calculation**: `driver_earnings = subtotal - platform_profit`

### Platform Fees

- **Platform Profit Margin**: 5% of the subtotal
- **Stripe Processing Fees**:
  - Percentage: 2.9% of transaction amount
  - Fixed fee: $0.30 per transaction
- **Total Platform Revenue**: `platform_profit = subtotal * 0.05`

### Payment Processing

- **Stripe Fees**: Calculated on the total transaction amount
  - `stripe_fees = (subtotal * 0.029) + 0.30`

## Price Calculation Example

Let's break down a 10-mile, 30-minute ride with 2 stops:

1. **Base Price Calculation**:

   - Distance: 10 miles
   - Base price per mile: $0.25 (minimum)
   - Base price: $2.50

2. **Additional Fees**:

   - Stop fee: 2 stops × $2.00 = $4.00
   - Time fee: 0 (under 1 hour)
   - Subtotal: $6.50

3. **Fee Distribution**:

   - Platform profit (5%): $0.33
   - Driver earnings: $6.17
   - Stripe fees: ($6.50 × 0.029) + $0.30 = $0.49

4. **Final Price**:
   - Total price: $6.99 (rounded to 2 decimal places)

## Price Limits

- **Minimum Price per Mile**: $0.25
- **Maximum Price per Mile**: $0.45

## Rider Price Splitting

When multiple riders share a ride:

1. Driver contributes 20% of the total price
2. Remaining amount is split equally among riders
3. All amounts are rounded to 2 decimal places

## Future Considerations

The fee structure may be adjusted based on:

- Market conditions
- Platform growth
- Operational costs
- Competitive landscape

## Fee Transparency

All fees are clearly displayed in the price breakdown:

- Base price
- Stop fees
- Time fees
- Platform fees
- Stripe processing fees
- Driver earnings
- Price per mile
- Price per rider (when applicable)

## Technical Implementation

The fee system is implemented in `app/services/price_service.py` and uses the following models:

- `PriceCalculationRequest`
- `PriceCalculationResponse`
- `PriceBreakdown`
- `RiderPriceRequest`
- `RiderPriceResponse`

For detailed implementation, refer to the source code.
