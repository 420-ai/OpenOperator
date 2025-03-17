class M365a:
    def __init__(self):
        # 1: optional string enrolledTenantId
        self.enrolled_tenant_id: str = ""
        
    def to_json(self):
        return {
            "enrolledTenantId": self.enrolled_tenant_id
        }
