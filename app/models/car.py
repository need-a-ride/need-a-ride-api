from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.session import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    color = Column(String, nullable=False)
    license_plate = Column(String, nullable=False, unique=True)
    capacity = Column(Integer, nullable=False, default=4)
    is_active = Column(Boolean, default=True)
    
    # Additional car details
    air_conditioned = Column(Boolean, default=False)
    has_wheelchair_access = Column(Boolean, default=False)
    
    # Relationships
    driver = relationship("Driver", back_populates="cars")
    rides = relationship("Ride", back_populates="car") 
