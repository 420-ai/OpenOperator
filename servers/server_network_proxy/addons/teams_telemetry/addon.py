import os
import json
import logging
from mitmproxy.http import HTTPFlow
from mitmproxy.net.encoding import decode_gzip
from .kusto_decoder import decode_kusto_request
from elasticsearch import Elasticsearch

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger("teams_addon")


# Setup logging
TELEMETRY_PATH = os.getenv("TELEMETRY_PATH", "/telemetry2")
print("TELEMETRY_PATH", TELEMETRY_PATH)
if not os.path.exists(TELEMETRY_PATH):
    os.makedirs(TELEMETRY_PATH)
    logger.info(f"Created telemetry logs directory: {TELEMETRY_PATH}")
else:
    logger.info(f"Telemetry logs directory already exists: {TELEMETRY_PATH}")


class TeamsTelemetryAddon:
    def __init__(self, filename: str = "teams-telemetry", storeurl: str = "http://localhost:9200"):
        self.filename = f"{filename}.log"
        self.store_url = storeurl

        logger.info(f"Initializing TeamsTelemetryAddon with filename: {self.filename} and store URL: {self.store_url}")

        self.es = Elasticsearch(self.store_url)

    def request(self, flow: HTTPFlow):

        # --------------------
        # Filter for telemetry requests
        # --------------------
        should_intercept = "teams.events.data.microsoft.com" in flow.request.host_header
        if not should_intercept:
            logger.debug("Request does not match telemetry host, skipping.")
            return

        # --------------------
        # Valid telemetry requests
        # --------------------

        # Log the request details
        logger.debug(f"Incoming request to {flow.request.pretty_url}")
        logger.debug(f"Request headers: {flow.request.headers}")
        logger.debug(f"Query params: {flow.request.query}")

        try:
            # --- JSON stream (browser JS telemetry) ---
            if flow.request.headers.get("content-type") == "application/x-json-stream":
                logger.info("Intercepted JS telemetry: application/x-json-stream")

                query_encoding = flow.request.query.get("content-encoding")
                encoding = flow.request.headers.get("content-encoding") or query_encoding
                logger.debug(f"Detected encoding: {encoding}")

                if encoding == "gzip":
                    body = decode_gzip(flow.request.content).decode("utf-8")
                else:
                    flow.request.decode()
                    body = flow.request.content.decode("utf-8")

                if body:
                    records = body.splitlines()
                    logger.info(f"Decoded {len(records)} records from JSON stream")
                    for record in records:

                        # Save into file
                        with open(f"{TELEMETRY_PATH}\\{self.filename}", "a") as f:
                            f.write(record + "\n")
                        logger.debug(f"Wrote records to file {self.filename}")

                        # Save into Elasticsearch
                        try:
                            doc = json.loads(record)
                            if isinstance(doc, dict):
                                self.es.index(index="teams-telemetry", document=doc)
                                logger.debug(f"Indexed record into Elasticsearch")
                            else:
                                logger.warning("Decoded record is not a valid JSON object")
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode JSON record: {e}")
                            logger.error(f"Record content: {record}")
                        except Exception as e:
                            logger.error(f"Failed to index record into Elasticsearch: {e}")
                            logger.error(f"Record content: {record}")

                    logger.info(f"Wrote {len(records)} records to file {self.filename}")

                else:
                    logger.warning("Empty body in application/x-json-stream request")

            # --- Bond Compact Binary (Desktop client) ---
            elif flow.request.headers.get("content-type") == "application/bond-compact-binary":
                logger.info("Intercepted Desktop telemetry: application/bond-compact-binary")

                flow.request.decode()
                content = flow.request.content

                body = decode_kusto_request(content)
                if body:
                    logger.info(f"Decoded {len(body)} Bond records")
                    for record in body:

                        # Save into file
                        with open(f"{TELEMETRY_PATH}\\{self.filename}", "a") as f:
                            f.write(json.dumps(record.to_json(), indent=None) + "\n")
                        logger.debug(f"Wrote Bond records to file {self.filename}")

                        # Save into Elasticsearch
                        try:
                            doc = record.to_json()
                            if isinstance(doc, dict):
                                self.es.index(index="teams-telemetry", document=doc)
                                logger.debug(f"Indexed record into Elasticsearch")
                            else:
                                logger.warning("Decoded record is not a valid JSON object")
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to decode JSON record: {e}")
                            logger.error(f"Record content: {record}")
                        except Exception as e:
                            logger.error(f"Failed to index record into Elasticsearch: {e}")
                            logger.error(f"Record content: {record}")

                    logger.info(f"Wrote {len(records)} records to file {self.filename}")

                else:
                    logger.warning("No Bond records decoded")

            # --- Web telemetry with gzip via query param ---
            elif flow.request.query.get("content-encoding") == "gzip":
                logger.info("Intercepted Web telemetry via query param: content-encoding=gzip")

                try:
                    body = decode_gzip(flow.request.content).decode("utf-8")
                    if body:
                        lines = body.splitlines()
                        logger.info(f"Decoded {len(lines)} lines from Web telemetry")
                        for line in lines:

                            # Save into file
                            with open(f"{TELEMETRY_PATH}\\{self.filename}", "a") as f:
                                f.write(line + "\n")
                            logger.debug(f"Wrote Web telemetry lines to file {self.filename}")

                            # Save into Elasticsearch
                            try:
                                doc = json.loads(record)
                                if isinstance(doc, dict):
                                    self.es.index(index="teams-telemetry", document=doc)
                                    logger.debug(f"Indexed record into Elasticsearch")
                                else:
                                    logger.warning("Decoded record is not a valid JSON object")
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to decode JSON record: {e}")
                                logger.error(f"Record content: {record}")
                            except Exception as e:
                                logger.error(f"Failed to index record into Elasticsearch: {e}")
                                logger.error(f"Record content: {record}")

                        logger.info(f"Wrote {len(records)} records to file {self.filename}")
                    else:
                        logger.warning("Empty body in gzip via query param request")
                except Exception as e:
                    logger.error(f"Failed to decode gzip via query param: {e}")

            else:
                logger.debug("Request did not match known telemetry formats")

        except Exception as e:
            logger.error(f"Unhandled error processing telemetry request: {e}")
            logger.error("Full traceback:\n" + str(e), exc_info=True)
