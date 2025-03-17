import os
import json
import logging
from mitmproxy.http import HTTPFlow
from mitmproxy.net.encoding import decode_gzip
from .kusto_decoder import decode_kusto_request


## TODO make the intercepted data to be a list of host_headers (check the oneds-collector-urls.json)

DATA_LOGS_PATH = "/data/logs/teams-telemetry/"

# ensure the directory exists
if not os.path.exists(DATA_LOGS_PATH):
    os.makedirs(DATA_LOGS_PATH)


class TeamsTelemetryAddon:
    def __init__(self):
        self.num = 0

    def request(self, flow: HTTPFlow):
        should_intercept = (
            flow.request.host_header.find("teams.events.data.microsoft.com") > -1
        )

        if should_intercept:
            ## this is for the JS portion
            if flow.request.headers.get("content-type") == "application/x-json-stream":
                flow.request.decode()
                body = flow.request.content.decode("utf-8")
                if body:
                    records = body.splitlines()
                    for record in records:
                        # for each record, append to a file in DATA_LOGS_PATH
                        # each record is a json object, we need to convert it to a single line of string
                        # and write it to the file
                        with open(
                            DATA_LOGS_PATH
                            + "teams-telemetry-"
                            + str(self.num)
                            + ".log",
                            "a",
                        ) as f:
                            f.write(record + "\n")
                else:
                    logging.info("No request body found.")

            ## this is for the Desktop client (shell)
            if (
                flow.request.headers.get("content-type")
                == "application/bond-compact-binary"
            ):
                logging.info("Intercepting Teams event data from maglev with bond.")

                ## decompresses the request body
                flow.request.decode()
                content = flow.request.content

                ## decode the Bond Compact Binary
                body = decode_kusto_request(content)

                if body:
                    for record in body:
                        # for each record, append to a file in DATA_LOGS_PATH
                        # each record is a json object, we need to convert it to a single line of string
                        # and write it to the file
                        with open(
                            DATA_LOGS_PATH
                            + "teams-telemetry-"
                            + str(self.num)
                            + ".log",
                            "a",
                        ) as f:
                            f.write(json.dumps(record.to_json(), indent=None) + "\n")

                else:
                    logging.info("No request body found.")

            ## this is for the Web client
            if flow.request.query.get("content-encoding"):
                encoding = flow.request.query["content-encoding"]

                if encoding == "gzip":
                    # manually decode this because the request uses a query param instead of a real content-encoding header
                    body = decode_gzip(flow.request.content).decode("utf-8")

                    if body:
                        lines = body.splitlines()
                        logging.info("Request body: %s" % lines)
                    else:
                        logging.info("No request body found.")
