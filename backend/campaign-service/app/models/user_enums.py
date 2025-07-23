# app/models/user_enums.py - Missing shared enums
import enum

class GenderType(str, enum.Enum):
    male = "MALE"
    female = "FEMALE"
    non_binary = "NON_BINARY"
    prefer_not_to_say = "PERFER_NOT_TO_SAY"


