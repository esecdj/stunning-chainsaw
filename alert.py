import datetime
from typing import List, Optional
from pydantic import BaseModel
from models.alert import AlertModel


class TimeRange(BaseModel):
    startDate : datetime.datetime
    endDate : datetime.datetime

class Filter(BaseModel):
    name : str
    value : str

class AlertRequestModel(BaseModel):
    pageToken: Optional[str] = None
    timeRange: Optional[TimeRange] = None
    limit: Optional[int] = None
    filters: Optional[List[Filter]] = None

class AlertListRequestModel(BaseModel):
    alerts : List[AlertModel]