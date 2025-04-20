import os
import time
import subprocess
from mitmproxy import certs, options
# from mitmproxy.certs import SSLCert
from cryptography.hazmat.primitives import serialization
import logging

logger = logging.getLogger("certs")

def ensure_mitmproxy_cert_installed():
    custom_confdir = os.path.join(os.environ["USERPROFILE"], ".mitmproxy")  # Or any path you like
    opts = options.Options(confdir=custom_confdir)

    # Check if already created
    key_size = 2048

    # ca = certs.CertStore.from_store(opts.confdir, "mitmproxy", key_size)
    certs.CertStore.from_store(opts.confdir, "mitmproxy", key_size)

    # ca_path = os.path.join(opts.confdir, "mitmproxy-ca.pem")
    cer_path = os.path.join(opts.confdir, "mitmproxy-ca-cert.cer")

    if not os.path.exists(cer_path):
        logger.error("Creating mitmproxy CA certificate failed...")
    else:
        logger.info("mitmproxy CA certificate already exists.")


    # Check if already installed
    try:
        logger.debug("Checking if mitmproxy cert is already trusted in Root store...")
        result = subprocess.run(
            ["certutil", "-verifystore", "Root"],
            capture_output=True, text=True, check=True
        )
        if "mitmproxy" in result.stdout.lower():
            logger.info("mitmproxy cert is already trusted.")
            return
    except subprocess.CalledProcessError as e:
        logger.warning(f"certutil check failed: {e}")

    # Install into Windows Root store
    try:
        logger.info("Installing mitmproxy cert into Windows Root store...")
        subprocess.run(
            ["certutil", "-addstore", "Root", cer_path],
            check=True
        )
        logger.info("mitmproxy cert installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install mitmproxy cert: {e}")
