import enum

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    refunded = "refunded"

class PaymentType(str, enum.Enum):
    base_payout = "base_payout"
    gmv_commission = "gmv_commission"
    bonus = "bonus"
    leaderboard_bonus = "leaderboard_bonus"
    referral_bonus = "referral_bonus"
    manual_adjustment = "manual_adjustment"

class PayoutMethod(str, enum.Enum):
    stripe = "stripe"
    fanbasis = "fanbasis"
    manual = "manual"
    bank_transfer = "bank_transfer"
