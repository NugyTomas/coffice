from datetime import time, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Time, Float, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy import Enum as SQLAlchemyEnum

from app.enums import CafePrice, CoffeeQuality, WifiQuality, PowerOutlets, NoiseLevel, Seating, AirConditioning, \
    TypicalOccupancy, FoodOptions, VegetarianOptions, CardPayment, OpeningDayStatus, WeekDay, Rating
from app.extensions import db


class Cafe(db.Model):
    __tablename__ = "cafes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_place_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(6), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(16), nullable=True)
    email: Mapped[str | None] = mapped_column(String(250), nullable=True)
    website: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(31), nullable=True)
    coffee_quality: Mapped[CoffeeQuality] = mapped_column(SQLAlchemyEnum(CoffeeQuality), nullable=True)
    price_level: Mapped[CafePrice] = mapped_column(SQLAlchemyEnum(CafePrice), nullable=True)

    opening_hours: Mapped[list["OpeningHours"]] = relationship(back_populates="cafe")
    cafe_photos: Mapped[list["CafePhoto"]] = relationship(back_populates="cafe")
    features: Mapped["CafeFeature"] = relationship(back_populates="cafe", uselist=False)
    reviews: Mapped[list["Review"]] = relationship(back_populates="cafe")


class OpeningHours(db.Model):
    __tablename__ = "opening_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False)
    day_of_week: Mapped[WeekDay] = mapped_column(SQLAlchemyEnum(WeekDay), nullable=False)
    status: Mapped[OpeningDayStatus] = mapped_column(SQLAlchemyEnum(OpeningDayStatus), nullable=False)
    open_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    close_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    cafe: Mapped["Cafe"] = relationship(back_populates="opening_hours")


class CafePhoto(db.Model):
    __tablename__ = "cafe_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cafe: Mapped["Cafe"] = relationship(back_populates="cafe_photos")


class CafeFeature(db.Model):
    __tablename__ = "cafe_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False, unique=True)
    wifi_quality: Mapped[WifiQuality] = mapped_column(SQLAlchemyEnum(WifiQuality), nullable=False)
    power_outlets: Mapped[PowerOutlets] = mapped_column(SQLAlchemyEnum(PowerOutlets), nullable=False)
    noise_level: Mapped[NoiseLevel] = mapped_column(SQLAlchemyEnum(NoiseLevel), nullable=False)
    seating_type: Mapped[Seating] = mapped_column(SQLAlchemyEnum(Seating), nullable=False)
    air_conditioning: Mapped[AirConditioning] = mapped_column(SQLAlchemyEnum(AirConditioning), nullable=True)
    typical_occupancy: Mapped[TypicalOccupancy | None] = mapped_column(SQLAlchemyEnum(TypicalOccupancy), nullable=True)
    food_options: Mapped[FoodOptions] = mapped_column(SQLAlchemyEnum(FoodOptions), nullable=False)
    vegetarian_options: Mapped[VegetarianOptions] = mapped_column(SQLAlchemyEnum(VegetarianOptions), nullable=False)
    card_payment: Mapped[CardPayment] = mapped_column(SQLAlchemyEnum(CardPayment), nullable=True)

    cafe: Mapped["Cafe"] = relationship(back_populates="features")


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    suggestions: Mapped[list["CafeSuggestion"]] = relationship(back_populates="user")
    suggestion_reviews: Mapped[list["CafeSuggestionReview"]] = relationship(back_populates="user")


class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[Rating] = mapped_column(SQLAlchemyEnum(Rating), nullable=False)
    text: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    cafe: Mapped["Cafe"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")

    __table_args__ = (UniqueConstraint("user_id", "cafe_id", name="unique_user_cafe_review"),)


class CafeSuggestion(db.Model):
    __tablename__ = "cafe_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_place_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(6), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(16), nullable=True)
    email: Mapped[str | None] = mapped_column(String(250), nullable=True)
    website: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(31), nullable=True)
    coffee_quality: Mapped[CoffeeQuality] = mapped_column(SQLAlchemyEnum(CoffeeQuality), nullable=True)
    price_level: Mapped[CafePrice] = mapped_column(SQLAlchemyEnum(CafePrice), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    suggestion_opening_hours: Mapped[list["CafeSuggestionOpeningHours"]] = relationship(back_populates="suggestion")
    suggestion_photos: Mapped[list["CafeSuggestionPhoto"]] = relationship(back_populates="suggestion")
    suggestion_features: Mapped["CafeSuggestionFeature"] = relationship(back_populates="suggestion", uselist=False)
    suggestion_reviews: Mapped["CafeSuggestionReview"] = relationship(back_populates="suggestion", uselist=False)

    user: Mapped["User"] = relationship(back_populates="suggestions")


class CafeSuggestionFeature(db.Model):
    __tablename__ = "cafe_suggestion_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("cafe_suggestions.id"), nullable=False, unique=True)
    wifi_quality: Mapped[WifiQuality] = mapped_column(SQLAlchemyEnum(WifiQuality), nullable=False)
    power_outlets: Mapped[PowerOutlets] = mapped_column(SQLAlchemyEnum(PowerOutlets), nullable=False)
    noise_level: Mapped[NoiseLevel] = mapped_column(SQLAlchemyEnum(NoiseLevel), nullable=False)
    seating_type: Mapped[Seating] = mapped_column(SQLAlchemyEnum(Seating), nullable=False)
    air_conditioning: Mapped[AirConditioning] = mapped_column(SQLAlchemyEnum(AirConditioning), nullable=True)
    typical_occupancy: Mapped[TypicalOccupancy | None] = mapped_column(SQLAlchemyEnum(TypicalOccupancy), nullable=True)
    food_options: Mapped[FoodOptions] = mapped_column(SQLAlchemyEnum(FoodOptions), nullable=False)
    vegetarian_options: Mapped[VegetarianOptions] = mapped_column(SQLAlchemyEnum(VegetarianOptions), nullable=False)
    card_payment: Mapped[CardPayment] = mapped_column(SQLAlchemyEnum(CardPayment), nullable=True)

    suggestion: Mapped["CafeSuggestion"] = relationship(back_populates="suggestion_features")


class CafeSuggestionOpeningHours(db.Model):
    __tablename__ = "cafe_suggestion_opening_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("cafe_suggestions.id"), nullable=False)
    day_of_week: Mapped[WeekDay] = mapped_column(SQLAlchemyEnum(WeekDay), nullable=False)
    status: Mapped[OpeningDayStatus] = mapped_column(SQLAlchemyEnum(OpeningDayStatus), nullable=False)
    open_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    close_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    suggestion: Mapped["CafeSuggestion"] = relationship(back_populates="suggestion_opening_hours")


class CafeSuggestionPhoto(db.Model):
    __tablename__ = "cafe_suggestion_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("cafe_suggestions.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    suggestion: Mapped["CafeSuggestion"] = relationship(back_populates="suggestion_photos")


class CafeSuggestionReview(db.Model):
    __tablename__ = "cafe_suggestion_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("cafe_suggestions.id"), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[Rating] = mapped_column(SQLAlchemyEnum(Rating), nullable=False)
    text: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    suggestion: Mapped["CafeSuggestion"] = relationship(back_populates="suggestion_reviews")
    user: Mapped["User"] = relationship(back_populates="suggestion_reviews")
