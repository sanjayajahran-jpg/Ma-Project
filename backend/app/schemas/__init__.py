from app.schemas.auth import Token, TokenPayload, UserLogin, UserCreate, UserResponse
from app.schemas.brand import BrandBase, BrandCreate, BrandUpdate, BrandResponse
from app.schemas.car import (
    EngineTypeResponse, BodyTypeResponse,
    CarSpecBase, CarSpecCreate, CarSpecResponse,
    CarVariantBase, CarVariantCreate, CarVariantResponse,
    CarBase, CarCreate, CarUpdate, CarListResponse, CarDetailResponse, CarPaginatedResponse
)
from app.schemas.compare import CompareRequest, CompareResponse
from app.schemas.calculator import (
    FuelPriceResponse, FuelPriceUpdate, FuelComparisonItem,
    FuelCostRequest, FuelCostResultItem, FuelCostSummary, FuelCostResponse
)

__all__ = [
    "Token", "TokenPayload", "UserLogin", "UserCreate", "UserResponse",
    "BrandBase", "BrandCreate", "BrandUpdate", "BrandResponse",
    "EngineTypeResponse", "BodyTypeResponse",
    "CarSpecBase", "CarSpecCreate", "CarSpecResponse",
    "CarVariantBase", "CarVariantCreate", "CarVariantResponse",
    "CarBase", "CarCreate", "CarUpdate", "CarListResponse", "CarDetailResponse", "CarPaginatedResponse",
    "CompareRequest", "CompareResponse",
    "FuelPriceResponse", "FuelPriceUpdate", "FuelComparisonItem",
    "FuelCostRequest", "FuelCostResultItem", "FuelCostSummary", "FuelCostResponse"
]
