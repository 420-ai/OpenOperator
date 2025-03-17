from typing import List
from .enums import PIIKind, CustomerContentKind

class Attribute:
    def __init__(self):
        # 1: optional vector<PII> pii
        self.pii: List[PIIKind] = []
        # 2: optional vector<CustomerContent> customer_content
        self.customer_content: List[CustomerContentKind] = []

    def __str__(self) -> str:
        pii_as_string = ",".join(str(value_pii) for value_pii in self.pii)
        customer_content_string = ",".join(str(value_cc) for value_cc in self.customer_content)
        return f"Attribute (pii: [{pii_as_string}], customer_content: [{customer_content_string}])"
