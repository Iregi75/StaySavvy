from datetime import datetime
from pydantic import BaseModel, validator

class BookingCreate(BaseModel):
    user_id: str
    hotel_id: str
    room_type: str
    check_in: str
    check_out: str
    guest_count: int
    payment_method: str
    
    @validator('check_in', 'check_out')
    def validate_dates(cls, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Date format must be YYYY-MM-DD")

class BookingResponse(BookingCreate):
    id: str
    status: str
    created_at: str
    total_amount: float