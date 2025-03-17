# Endpoints

# Endpoints

## ✅ **List of Exposed Functionalities (Endpoints):**

| HTTP Method | Endpoint                             | Description                                                           |
| ----------- | ------------------------------------ | --------------------------------------------------------------------- |
| GET         | `/healthcheck`                       | Check service health status                                           |
| POST        | `/update_computer`                   | Updates computer state (window rect, clipboard, screenshot).          |
| POST        | `/execute_windows`                   | Executes Python commands using global `computer` and `human` objects. |
| POST        | `/execute`                           | Executes system shell commands.                                       |
| POST        | `/setup/execute`                     | Executes shell commands (alias of `/execute`).                        |
| POST        | `/shutdown`                          | Shuts down the machine.                                               |
| POST        | `/setup/launch`                      | Launches a specified application or command.                          |
| GET         | `/screenshot`                        | Captures screen including cursor (**deprecated**).                    |
| GET         | `/terminal`                          | Retrieves terminal window contents (Linux only).                      |
| GET         | `/obs_winagent`                      | Captures foreground window and additional info for OBS agent.         |
| GET         | `/accessibility`                     | Provides accessibility tree from UI (Linux/Windows).                  |
| POST        | `/screen_size`                       | Retrieves current screen resolution.                                  |
| POST        | `/window_size`                       | Retrieves dimensions of a specified window (Linux-specific).          |
| POST        | `/desktop_path`                      | Returns path to user's desktop.                                       |
| POST        | `/documents_path`                    | Returns path to user's documents.                                     |
| POST        | `/setup/create_folder`               | Creates a specified folder.                                           |
| POST        | `/setup/create_file`                 | Creates a file with specified content.                                |
| POST        | `/setup/recycle`                     | Moves specified file to recycle bin.                                  |
| POST        | `/folder_exists`                     | Checks if a specified folder exists.                                  |
| POST        | `/file_exists`                       | Checks if specified file exists.                                      |
| POST        | `/is_details_view`                   | Checks if Windows Explorer is in 'Details' view.                      |
| POST        | `/wallpaper`                         | Retrieves current wallpaper image.                                    |
| POST        | `/list_directory`                    | Lists directory contents recursively.                                 |
| POST        | `/file`                              | Sends specified file as download.                                     |
| POST        | `/setup/upload`                      | Uploads file to specified path.                                       |
| GET         | `/platform`                          | Retrieves OS platform information.                                    |
| GET         | `/cursor_position`                   | Returns current cursor position.                                      |
| POST        | `/setup/change_wallpaper`            | Changes the system wallpaper.                                         |
| POST        | `/setup/download_file`               | Downloads a file from provided URL.                                   |
| POST        | `/setup/open_file`                   | Opens the specified file with system default app.                     |
| POST        | `/setup/activate_window`             | Activates a specified window.                                         |
| POST        | `/setup/clear_task_files`            | Clears task-related files from Downloads folder.                      |
| POST        | `/setup/close_all`                   | Closes all open windows.                                              |
| POST        | `/setup/close_window`                | Closes a specific window.                                             |
| POST        | `/start_recording`                   | Starts screen recording.                                              |
| POST        | `/end_recording`                     | Stops recording and saves file.                                       |
| GET         | `/get_recording`                     | Retrieves recorded screen video file.                                 |
| POST        | `/save_state`                        | Creates a system snapshot (Windows only).                             |
| POST        | `/revert_to_snapshot`                | Restores system snapshot (**currently inactive**).                    |
| POST        | `/folder_exists`                     | Checks if a folder exists.                                            |
| POST        | `/list_directory`                    | Lists directory contents recursively.                                 |
| POST        | `/file`                              | Retrieves a specified file.                                           |
| POST        | `/setup/upload`                      | Uploads a file.                                                       |
| POST        | `/are_files_sorted_by_modified_time` | Checks if files in a directory are sorted by modification time.       |
| POST        | `/is_details_view`                   | Checks if File Explorer is in details view.                           |
| POST        | `/are_images_tagged`                 | Checks if all images have a specific tag.                             |
| POST        | `/library_folders`                   | Lists folders within a Windows library.                               |
| POST        | `/timer_exists`                      | Checks if a specified timer exists.                                   |
| POST        | `/check_world_clock`                 | Checks if specified world clock is active.                            |

---

## List of Code Functions Not Used at All (can be removed safely):

| Function Name                        | Remarks/Reason for Removal                                                              |
| ------------------------------------ | --------------------------------------------------------------------------------------- |
| `_has_active_terminal`               | Used only in `/terminal`, incomplete, Linux-specific. Remove if `/terminal` is removed. |
| `_create_pywinauto_node`             | Defined but not used at all, safe to remove entirely.                                   |
| `get_wallpaper_macos`                | Defined, but `get_wallpaper` endpoint currently does not call it.                       |
| `_create_atspi_node` (special cases) | Conditional logic (`calc`, `thunderbird`) unused; can simplify/remove these branches.   |
| `revert_to_snapshot`                 | Fully commented out, currently inactive. Can remove or complete.                        |

---

## List of Code Functions Not Used at All (can be removed safely):

| Function Name            | Reason                                                                 |
| ------------------------ | ---------------------------------------------------------------------- |
| `_create_pywinauto_node` | Not invoked in the script at all.                                      |
| `get_wallpaper_macos`    | Not invoked; macOS wallpaper retrieval unused.                         |
| `_has_active_terminal`   | Used conditionally; if `/terminal` is removed, this becomes redundant. |

---

**Recommendations:**

- Consider removing unused or incomplete functions mentioned above.
- Address deprecated endpoints (`/screenshot`) clearly if alternatives exist.
