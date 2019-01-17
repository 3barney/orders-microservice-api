from enum import Enum, auto

# auto() means that items in the enumeration will get a numeric sequential number
class Status(Enum):
  Received = auto()
  Processing = auto()
  Payment_Complete = auto()
  Shipping = auto()
  Completed = auto()
  Cancelled = auto()
