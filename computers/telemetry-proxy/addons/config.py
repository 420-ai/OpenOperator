from mitmproxy import addon

class MS_Teams_Filter:
    def __init__(self):
        self.domain_pattern = re.compile(r'data\.events\.microsoft\.com')

    def request(self, flow):
        if self.domain_pattern.search(flow.request.host):
            ctx.log.info(f"Intercepted traffic: {flow.request.method} {flow.request.path}")

addon.register(MS_Teams_Filter())
