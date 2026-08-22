from datetime import time, datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Time, Float, ForeignKey, Boolean, DateTime, UniqueConstraint

from extensions import db

class Cafe(db.Model):
    __tablename__ = "cafes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_place_id : Mapped[str] = mapped_column(String(255), unique= True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    email : Mapped[str] = mapped_column(String(250), nullable=True)
    website : Mapped[str] = mapped_column(String(2048), nullable=True)
    instagram : Mapped[str] = mapped_column(String(100), nullable=True)
    price_level: Mapped[str] = mapped_column(String(20), nullable=True)

    opening_hours: Mapped[list["OpeningHours"]] = relationship(back_populates="cafe")
    cafe_photos: Mapped[list["CafePhoto"]] = relationship(back_populates="cafe")
    features: Mapped["CafeFeature"] = relationship(back_populates="cafe", uselist=False)
    reviews: Mapped[list["Review"]] = relationship(back_populates="cafe")


class OpeningHours(db.Model):
    __tablename__ = "opening_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id : Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False)
    day_of_week : Mapped[str] = mapped_column(String(20), nullable=False)
    open_time: Mapped[time] = mapped_column(Time, nullable=True)
    close_time: Mapped[time] = mapped_column(Time, nullable=True)

    cafe: Mapped["Cafe"] = relationship(back_populates="opening_hours")

class CafePhoto(db.Model):
    __tablename__ = "cafe_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id : Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    cafe: Mapped["Cafe"] = relationship(back_populates="cafe_photos")

class CafeFeature(db.Model):
    __tablename__ = "cafe_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False, unique=True)
    wifi_quality: Mapped[str] = mapped_column(String(20), nullable=True)
    socket_availability: Mapped[str] = mapped_column(String(20), nullable=True)
    noise_level : Mapped[str] = mapped_column(String(20), nullable=True)
    seating_type: Mapped[str] = mapped_column(String(20), nullable=True)
    air_conditioning: Mapped[bool] = mapped_column(Boolean, nullable=True)
    typical_occupancy: Mapped[str] = mapped_column(String(20), nullable=True)
    card_payment: Mapped[bool] = mapped_column(Boolean, nullable=True)
    food_available: Mapped[str] = mapped_column(String(20), nullable=True)
    vegetarian_options: Mapped[bool] = mapped_column(Boolean, nullable=True)

    cafe: Mapped["Cafe"] = relationship(back_populates="features")

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user")
    suggestions: Mapped[list["CafeSuggestion"]] = relationship(back_populates="user")
    suggestion_reviews: Mapped[list["CafeSuggestionReview"]] = relationship(back_populates="user")

class Review(db.Model):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafes.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    cafe: Mapped["Cafe"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")

    __table_args__ = (UniqueConstraint("user_id", "cafe_id", name="unique_user_cafe_review"),)

class CafeSuggestion(db.Model):
    __tablename__ = "cafe_suggestions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_place_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[str] = mapped_column(String(250), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    email: Mapped[str] = mapped_column(String(250), nullable=True)
    website: Mapped[str] = mapped_column(String(2048), nullable=True)
    instagram: Mapped[str] = mapped_column(String(100), nullable=True)
    price_level: Mapped[str] = mapped_column(String(20), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    suggestion_opening_hours: Mapped[list["CafeSuggestionOpeningHours"]] = relationship(back_populates="suggestion")
    suggestion_photos: Mapped[list["CafeSuggestionPhoto"]] = relationship(back_populates="suggestion")
    suggestion_features : Mapped["CafeSuggestionFeature"] = relationship(back_populates="suggestion", uselist=False)
    suggestion_reviews: Mapped["CafeSuggestionReview"] = relationship(back_populates="suggestion", uselist=False)

    user: Mapped["User"] = relationship(back_populates="suggestions")


class CafeSuggestionOpeningHours(db.Model):
    __tablename__ = "cafe_suggestion_opening_hours"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("cafe_suggestions.id"), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    open_time: Mapped[time] = mapped_column(Time, nullable=True)
    close_time: Mapped[time] = mapped_column(Time, nullable=True)

    suggestion: Mapped["CafeSuggestion"] = relationship(back_populates="suggestion_opening_hours")

class CafeSuggestionPhoto(db.Model):
    __tablename__ = "cafe_suggestion_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("cafe_suggestions.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    suggestion: Mapped["CafeSuggestion"] = relationship(back_populates="suggestion_photos")

class CafeSuggestionFeature(db.Model):
    __tablename__ = "cafe_suggestion_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("cafe_suggestions.id"), nullable=False, unique=True)
    wifi_quality: Mapped[str] = mapped_column(String(20), nullable=True)
    socket_availability: Mapped[str] = mapped_column(String(20), nullable=True)
    noise_level: Mapped[str] = mapped_column(String(20), nullable=True)
    seating_type: Mapped[str] = mapped_column(String(20), nullable=True)
    air_conditioning: Mapped[bool] = mapped_column(Boolean, nullable=True)
    typical_occupancy: Mapped[str] = mapped_column(String(20), nullable=True)
    card_payment: Mapped[bool] = mapped_column(Boolean, nullable=True)
    food_available: Mapped[str] = mapped_column(String(20), nullable=True)
    vegetarian_options: Mapped[bool] = mapped_column(Boolean, nullable=True)

    suggestion: Mapped["CafeSuggestion"] = relationship(back_populates="suggestion_features")

class CafeSuggestionReview(db.Model):
    __tablename__ = "cafe_suggestion_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    suggestion_id: Mapped[int] = mapped_column(ForeignKey("cafe_suggestions.id"), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    text: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    suggestion: Mapped["CafeSuggestion"] = relationship(back_populates="suggestion_reviews")
    user: Mapped["User"] = relationship(back_populates="suggestion_reviews")