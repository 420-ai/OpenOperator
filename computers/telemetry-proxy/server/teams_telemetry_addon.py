import logging
from mitmproxy.http import HTTPFlow
from mitmproxy.net.encoding import decode_gzip
from kusto_decoder import decode_kusto_request

# Use this for Maglev
# mitmproxy -k -s teams-telemetry.py --mode local:ms-teams --view-filter="teams.events.data.microsoft.com" --showhost

## TODO just have this script to run the proxy server for us

class TeamsTelemetryAddon:
    def __init__(self):
        self.num = 0

    def request(self, flow: HTTPFlow):       
        should_intercept = (
            flow.request.host_header.find("teams.events.data.microsoft.com") > -1
        )

        if should_intercept:
            if flow.request.headers.get("content-type") == "application/bond-compact-binary":
                logging.info("Intercepting Teams event data from maglev with bond.")
                
                ## decompresses the request body
                flow.request.decode()
                content = flow.request.content

                ## decode the Bond Compact Binary
                body = decode_kusto_request(content)
                
                if body:
                    for record in body:
                        logging.info("Record: %s" % record.to_json())
                else:
                    logging.info("No request body found.")
            
            if flow.request.query.get("content-encoding"):
                encoding = flow.request.query["content-encoding"]
                
                if encoding == "gzip":
                    body = decode_gzip(flow.request.content).decode("utf-8")

                    if body:
                        lines = body.splitlines()
                        logging.info("Request body: %s" % lines)
                    else:
                        logging.info("No request body found.")
