from datetime import time, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Time, Float, ForeignKey, Boolean, DateTime, UniqueConstraint, CheckConstraint
from sqlalchemy import Enum as SQLAlchemyEnum

from app.enums import CafePrice, CoffeeQuality, WifiQuality, PowerOutlets, NoiseLevel, Seating, AirConditioning, \
    TypicalOccupancy, FoodOptions, VegetarianOptions, CardPayment, OpeningDayStatus, WeekDay, CafeStatus
from app.extensions import db


class Cafe(db.Model):
    __tablename__ = "cafes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_place_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(50))
    postal_code: Mapped[str] = mapped_column(String(6))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    phone: Mapped[str | None] = mapped_column(String(16))
    email: Mapped[str | None] = mapped_column(String(250))
    website: Mapped[str | None] = mapped_column(String(2048))
    instagram: Mapped[str | None] = mapped_column(String(31))
    coffee_quality: Mapped[CoffeeQuality] = mapped_column(SQLAlchemyEnum(CoffeeQuality))
    price_level: Mapped[CafePrice] = mapped_column(SQLAlchemyEnum(CafePrice))
    status: Mapped[CafeStatus] = mapped_column(SQLAlchemyEnum(CafeStatus), default=CafeStatus.PENDING, nullable=False, index=True)
    submitted_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    opening_hours: Mapped[list["OpeningHours"]] = relationship(back_populates="cafe", cascade="all, delete-orphan")
    photos: Mapped[list["CafePhoto"]] = relationship(back_populates="cafe", cascade="all, delete-orphan")
    features: Mapped["CafeFeature"] = relationship(back_populates="cafe", uselist=False, cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="cafe", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship(back_populates="submitted_cafes")

class CafeFeature(db.Model):
    __tablename__ = "cafe_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), unique=True)
    wifi_quality: Mapped[WifiQuality] = mapped_column(SQLAlchemyEnum(WifiQuality))
    power_outlets: Mapped[PowerOutlets] = mapped_column(SQLAlchemyEnum(PowerOutlets))
    noise_level: Mapped[NoiseLevel] = mapped_column(SQLAlchemyEnum(NoiseLevel))
    seating_type: Mapped[Seating] = mapped_column(SQLAlchemyEnum(Seating))
    air_conditioning: Mapped[AirConditioning] = mapped_column(SQLAlchemyEnum(AirConditioning))
    typical_occupancy: Mapped[TypicalOccupancy] = mapped_column(SQLAlchemyEnum(TypicalOccupancy))
    food_options: Mapped[FoodOptions] = mapped_column(SQLAlchemyEnum(FoodOptions))
    vegetarian_options: Mapped[VegetarianOptions] = mapped_column(SQLAlchemyEnum(VegetarianOptions))
    card_payment: Mapped[CardPayment] = mapped_column(SQLAlchemyEnum(CardPayment))

    cafe: Mapped["Cafe"] = relationship(back_populates="features")


class OpeningHours(db.Model):
    __tablename__ = "opening_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"))
    day_of_week: Mapped[WeekDay] = mapped_column(SQLAlchemyEnum(WeekDay))
    status: Mapped[OpeningDayStatus] = mapped_column(SQLAlchemyEnum(OpeningDayStatus))
    open_time: Mapped[time | None] = mapped_column(Time)
    close_time: Mapped[time | None] = mapped_column(Time)

    cafe: Mapped["Cafe"] = relationship(back_populates="opening_hours")


class CafePhoto(db.Model):
    __tablename__ = "cafe_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"))
    image_url: Mapped[str] = mapped_column(String(2048))
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)

    cafe: Mapped["Cafe"] = relationship(back_populates="photos")

class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str | None] = mapped_column(String(2048))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    cafe: Mapped["Cafe"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")

    __table_args__ = (UniqueConstraint("user_id", "cafe_id", name="unique_user_cafe_review"),
                      CheckConstraint("rating BETWEEN 1 AND 5", name="rating_between_1_and_5"),)

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    submitted_cafes: Mapped[list["Cafe"]] = relationship(back_populates="user")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
