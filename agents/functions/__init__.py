from functions.default.close_all_windows import close_all_windows
from functions.default.open_application import open_application
from functions.default.start_network_proxy import start_network_proxy
from functions.default.stop_network_proxy import stop_network_proxy
from functions.default.get_evaluation_results import get_evaluation_results
from functions.default.delete_files import delete_files

FUNCTIONS = {
    "close_all_windows": close_all_windows,
    "open_application": open_application,
    "start_network_proxy": start_network_proxy,
    "stop_network_proxy": stop_network_proxy,
    "get_evaluation_results": get_evaluation_results,
    "delete_files": delete_files,
}
