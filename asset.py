from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
import datetime


class MethodIntegrationModel(BaseModel):
    uri: str
    type: str
    httpMethod: str
    timeoutInMillis: int
    cacheKeyParameters: List[str]
    passthroughBehavior: str


class AlertsCountModel(BaseModel):
    count: int
    severity: str


class AssetDataModel(BaseModel):
    rest_api: Optional[str] = Field(None, alias="restApi")
    http_method: Optional[str] = Field(None, alias="httpMethod")
    api_key_required: Optional[bool] = Field(None, alias="apiKeyRequired")
    authorization_type: Optional[str] = Field(None, alias="authorizationType")
    method_integration: Optional[MethodIntegrationModel] = Field(None, alias="methodIntegration")


class AssetModel(BaseModel):
    id: str = Field(alias="id")
    external_asset_id: str = Field(..., alias="externalAssetId")
    cloud_type: str = Field(..., alias="cloudType")
    created_ts: datetime.datetime = Field(..., alias="createdTs")
    insert_ts: datetime.datetime = Field(..., alias="insertTs")
    dynamic_data: Optional[Any] = Field(None, alias="dynamicData")
    data: AssetDataModel
    name: str
    region_id: str = Field(..., alias="regionId")
    region_name: str = Field(..., alias="regionName")
    risk_grade: str = Field(..., alias="riskGrade")
    state_id: Optional[str] = Field(None, alias="stateId")
    url: str
    vpc_id: Optional[str] = Field(None, alias="vpcId")
    vpc_name: str = Field(..., alias="vpcName")
    relationship_counts: int = Field(..., alias="relationshipCounts")
    vulnerability_counts: Optional[Any] = Field(None, alias="vulnerabilityCounts")
    vpc_external_asset_id: str = Field(..., alias="vpcExternalAssetId")
    tags: Dict[str, str]
    asset_type: str = Field(..., alias="assetType")
    service_name: str = Field(..., alias="serviceName")
    resource_type: str = Field(..., alias="resourceType")
    account_group: str = Field(..., alias="accountGroup")
    account_name: str = Field(..., alias="accountName")
    asset_class_id: str = Field(..., alias="assetClassId")
    asset_class: str = Field(..., alias="assetClass")
    deleted: bool
    problem: List[Any]
    alerts_count: List[AlertsCountModel] = Field(..., alias="alertsCount")
    alert_count_by_severity: List[AlertsCountModel] = Field(..., alias="alertCountBySeverity")
    ip_addresses: List[str] = Field(..., alias="ipAddresses")
    true_internet_exposure: Optional[Any] = Field(None, alias="trueInternetExposure")

    # Auto-convert timestamps (milliseconds -> datetime)
    @field_validator("created_ts", "insert_ts", mode="before")
    @classmethod
    def convert_timestamp(cls, value):
        if isinstance(value, (int, float)):  
            return datetime.datetime.fromtimestamp(value / 1000, tz=datetime.timezone.utc)  # Convert to UTC
        return value  # If already datetime, keep it
    
    model_config = {"populate_by_name": True, "alias_generator": None}
