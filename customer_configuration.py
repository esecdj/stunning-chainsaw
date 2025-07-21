from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from models.customer_configuration import ConfigurationCredential, ConfigurationModel, ConfigurationSetting


class ConfigutrationRequestModel(BaseModel):
    configuration: Optional[List[ConfigurationModel]] = None
    credential: Optional[ConfigurationCredential] = None
    settings: Optional[ConfigurationSetting] = None

