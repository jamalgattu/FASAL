import enum


class UserRole(str, enum.Enum):
    FARMER = "farmer"
    BUYER = "buyer"
    ADMIN = "admin"


class Unit(str, enum.Enum):
    KG = "kg"
    QUINTAL = "quintal"
    TONNE = "tonne"


class QualityGrade(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


QUALITY_RANK = {QualityGrade.C: 1, QualityGrade.B: 2, QualityGrade.A: 3}


class BuyerType(str, enum.Enum):
    INSTITUTIONAL = "institutional"
    WHOLESALER = "wholesaler"
    RETAIL_CHAIN = "retail_chain"
    PROCESSOR = "processor"


class ListingStatus(str, enum.Enum):
    AVAILABLE = "available"
    MATCHED = "matched"
    IN_ORDER = "in_order"
    SOLD_OUT = "sold_out"
    EXPIRED = "expired"


class RequirementStatus(str, enum.Enum):
    OPEN = "open"
    MATCHED = "matched"
    FULFILLED = "fulfilled"
    CLOSED = "closed"


class MatchStatus(str, enum.Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CONVERTED = "converted"  # turned into an Order


class OrderStatus(str, enum.Enum):
    MATCHED = "matched"
    ACCEPTED = "accepted"
    RESERVED = "reserved"
    CONFIRMED = "confirmed"
    PICKUP_ASSIGNED = "pickup_assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    DISPUTED = "disputed"


# Statuses at/after which inventory has been reserved against the listing.
INVENTORY_RESERVED_STATUSES = {
    OrderStatus.RESERVED,
    OrderStatus.CONFIRMED,
    OrderStatus.PICKUP_ASSIGNED,
    OrderStatus.PICKED_UP,
    OrderStatus.IN_TRANSIT,
    OrderStatus.DELIVERED,
    OrderStatus.DISPUTED,
}

# Terminal statuses — no further transitions are allowed out of these.
TERMINAL_ORDER_STATUSES = {
    OrderStatus.COMPLETED,
    OrderStatus.CANCELLED,
    OrderStatus.REJECTED,
}


class VehicleType(str, enum.Enum):
    MINI_TRUCK = "mini_truck"
    TRUCK = "truck"
    REFRIGERATED_VAN = "refrigerated_van"
    TEMPO = "tempo"


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
