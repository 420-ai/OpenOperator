# import os
# import subprocess
# import sys
# import time
# import asyncio
# from mitmproxy import options
# from mitmproxy.tools.dump import DumpMaster

# CERT_SUBJECT = "mitmproxy"
# CERT_PATH = os.path.expanduser("~/.mitmproxy/mitmproxy-ca-cert.cer")


# def ensure_cert_generated():
#     """
#     Starts mitmproxy's DumpMaster briefly to generate CA cert.
#     """
#     if os.path.exists(CERT_PATH):
#         print("mitmproxy certificate already exists.")
#         return

#     print("Generating mitmproxy certificate...")

#     async def start_and_shutdown():
#         opts = options.Options(listen_host="127.0.0.1", listen_port=8080, ssl_insecure=True)
#         m = DumpMaster(opts, with_termlog=False, with_dumper=False)
#         m.addons.clear()
#         await m.running()
#         await m.shutdown()

#     # Create and run event loop
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(start_and_shutdown())
#     loop.close()

#     print("Certificate generation complete.")


# def is_cert_installed():
#     """
#     Checks if the mitmproxy cert is already in the Windows Root cert store.
#     """
#     try:
#         result = subprocess.run(
#             ["certutil", "-verifystore", "Root"],
#             capture_output=True,
#             text=True,
#             check=True
#         )
#         return CERT_SUBJECT.lower() in result.stdout.lower()
#     except subprocess.CalledProcessError as e:
#         print("Error checking certificate store:", e)
#         return False


# def install_cert():
#     """
#     Installs the mitmproxy CA cert to the Windows Root cert store.
#     """
#     if not os.path.exists(CERT_PATH):
#         print(f"Certificate not found at: {CERT_PATH}")
#         return

#     print("Installing certificate...")
#     try:
#         subprocess.run(
#             ["certutil", "-addstore", "Root", CERT_PATH],
#             check=True
#         )
#         print("Certificate installed successfully.")
#     except subprocess.CalledProcessError as e:
#         print("Failed to install certificate:", e)


# def install_mitmproxy_certs():
#     """
#     Main function to ensure the mitmproxy cert is generated and installed.
#     """
#     ensure_cert_generated()

#     if is_cert_installed():
#         print("mitmproxy certificate is already installed.")
#     else:
#         install_cert()

