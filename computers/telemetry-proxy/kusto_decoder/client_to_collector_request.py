from .deserializers.deserialize_record import deserialize_record
from .deserializers.deserialize_data import deserialize_data
from .deserializers.deserialize_value import deserialize_value
from .deserializers.deserialize_attribute import deserialize_attribute
from .deserializers.deserialize_customer_content import deserialize_customer_content
from .deserializers.deserialize_pii import deserialize_pii
from .deserializers.deserialize_m365a import deserialize_m365a
from .deserializers.deserialize_loc import deserialize_loc
from .deserializers.deserialize_protocol import deserialize_protocol
from .deserializers.deserialize_sdk import deserialize_sdk
from .deserializers.deserialize_net import deserialize_net
from .deserializers.deserialize_utc import deserialize_utc
from .deserializers.deserialize_app import deserialize_app
from .deserializers.deserialize_os import deserialize_os
from .deserializers.deserialize_device import deserialize_device
from .deserializers.deserialize_user import deserialize_user

class ClientToCollectorRequest:
    """
    Main class for deserializing collector request data
    """
    
    deserialize_record = staticmethod(deserialize_record)
    deserialize_data = staticmethod(deserialize_data)
    deserialize_value = staticmethod(deserialize_value)
    deserialize_attribute = staticmethod(deserialize_attribute)
    deserialize_customer_content = staticmethod(deserialize_customer_content)
    deserialize_pii = staticmethod(deserialize_pii)
    deserialize_m365a = staticmethod(deserialize_m365a)
    deserialize_loc = staticmethod(deserialize_loc)
    deserialize_sdk = staticmethod(deserialize_sdk)
    deserialize_net = staticmethod(deserialize_net)
    deserialize_utc = staticmethod(deserialize_utc)
    deserialize_app = staticmethod(deserialize_app)
    deserialize_os = staticmethod(deserialize_os)
    deserialize_device = staticmethod(deserialize_device)
    deserialize_user = staticmethod(deserialize_user)
    deserialize_protocol = staticmethod(deserialize_protocol)
