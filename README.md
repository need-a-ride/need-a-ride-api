# NeedARide 🚗

A modern, efficient, and user-friendly ride-sharing platform built with FastAPI and Python. NeedARide connects drivers with riders, offering a seamless experience for both parties.

## 🌟 Features

### For Riders

- **Smart Route Planning**: Optimized routes with multiple stops
- **Real-time Price Estimation**: Transparent pricing based on distance, time, and stops
- **Ride Sharing**: Split costs with other riders
- **Recurring Rides**: Save 10% on regular commutes
- **Multiple Payment Options**: Secure digital payments through Stripe
- **Real-time Tracking**: Live location updates during rides
- **Driver Ratings**: Rate and review your experience
- **Scheduled Rides**: Book rides in advance

### For Drivers

- **Flexible Earnings**: 20% profit margin on rides
- **Route Optimization**: Smart navigation with Google Maps integration
- **Multiple Stops**: Efficient handling of multi-stop routes
- **Recurring Rides**: Build a regular customer base
- **Real-time Updates**: Live traffic and route information
- **Earnings Dashboard**: Track your income and performance

### Platform Features

- **Transparent Fee Structure**: Clear breakdown of all costs
- **Safety First**: Real-time tracking and driver verification
- **Scalable Architecture**: Built for growth
- **API-First Design**: Easy integration with other services
- **Comprehensive Documentation**: Detailed API and system documentation

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT with OAuth2
- **Maps**: Google Maps API
- **Payments**: Stripe
- **Testing**: Pytest
- **Documentation**: OpenAPI (Swagger)

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Google Maps API Key
- Stripe API Keys
- Redis (for caching)

## 🚀 Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/needaride-api.git
   cd needaride-api
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**

   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📝 Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/needaride

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Maps
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Redis
REDIS_URL=redis://localhost:6379
```

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running the server
- **Fee System**: [Fee System Documentation](docs/fee_system.md)
- **Architecture**: [Architecture Overview](docs/architecture.md)

## 🧪 Testing

Run tests with:

```bash
pytest
```

## 📦 Project Structure

```
needaride-api/
├── alembic/              # Database migrations
├── app/
│   ├── core/            # Core functionality
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── schemas/         # Pydantic models
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
├── docs/                # Documentation
├── tests/               # Test files
├── .env.example         # Example environment variables
├── alembic.ini          # Alembic configuration
├── main.py              # Application entry point
└── requirements.txt     # Project dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software owned by NeedARide. All rights reserved.

### What this means for you:

#### If you're a user:

- You can use NeedARide's services by paying the platform fees
- The service is not free to use
- You cannot run your own instance
- You cannot modify or distribute the code

#### If you're a developer:

- You can view the code for learning purposes
- You cannot use the code to create competing services
- You cannot modify or distribute the code
- You can contribute through pull requests

#### If you're a business:

- You cannot use this code to create any ride-sharing service
- You cannot modify or distribute the code
- You cannot run your own instance
- You must use the official NeedARide service

#### Commercial Use:

- NeedARide charges platform fees for all rides
- Platform fees are transparent and clearly displayed
- Fees are used to maintain and improve the service
- The service is not free to use

For commercial licensing inquiries, please contact us at [boharasirshak101@gmail.com]

## 👥 Authors

- Your Name - Sirshak Bohara

## 🙏 Acknowledgments

- FastAPI team for the amazing framework
- Google Maps Platform for mapping services
- Stripe for payment processing
- All contributors and users of NeedARide
