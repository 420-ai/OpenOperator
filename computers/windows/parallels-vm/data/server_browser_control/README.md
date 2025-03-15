# Endpoints

## ✅ **List of Exposed Functionalities (Endpoints):**

| Method | Endpoint                     | Description                                 |
| ------ | ---------------------------- | ------------------------------------------- |
| GET    | `/healthcheck`               | Check service health status                 |
| POST   | `/browser/launch`            | Launch browser instance                     |
| POST   | `/browser/open`              | Open a URL in a new page                    |
| POST   | `/browser/close`             | Close browser instance                      |
| POST   | `/browser/cdp`               | Send Chrome DevTools Protocol (CDP) command |
| POST   | `/browser/screenshot`        | Take a screenshot of the specified page     |
| POST   | `/browser/get_cookies`       | Retrieve cookies for the specified page     |
| POST   | `/browser/start_tracing`     | Start browser tracing                       |
| POST   | `/browser/stop_tracing`      | Stop browser tracing                        |
| GET    | `/browser/download_trace`    | Download trace file                         |
| POST   | `/browser/get_local_storage` | Get local storage from specified page       |
| POST   | `/browser/execute_js`        | Execute JavaScript on specified page        |
| GET    | `/platform`                  | Get system platform info                    |
| GET    | `/cursor_position`           | Get current cursor position (x, y)          |
| POST   | `/setup/create_file`         | Create a file with specified content        |
| POST   | `/setup/open_file`           | Open file on system                         |
| POST   | `/shutdown`                  | Initiate system shutdown (**Careful!**)     |
