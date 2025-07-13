# Computers

This folder contains setup for computers that are operated via OpenOperator.

# 1. Windows

In folder `parallels_vm` is setup for a VM in [Paralells](https://parallels.com/).

## 1.1 Download Windows 11 Evaluation .iso file:

1. Visit [Microsoft Software Download](https://www.microsoft.com/en-us/software-download/windows11arm64), select language, and download ISO file
2. Select edition `Windows 11 (multi-edition ISO for Arm64)`
3. Select language `English (United States)`
4. The downloaded file looks like `Win11_24H2_English_Arm64.iso` [~5GB]

## 1.2 Install VM

Install Windows manually from the `iso` file you've downloaded. Choose `Windows 11 Pro` as version.

### Installation notes

Device name: `oo-comp-1`

When reaching the "Sign in" screen with Microsoft account
Shift + F10 => opens command prompt
Write `start ms-cxh:localonly` and hit Enter

Create a local user:
username: Lukas1234
password: 1234

## 1.3 Setup VM

0. Edit a power plan on Windows
   Turn off the display: never
   Put the computer to sleep: never

1. Create a folder `C:\OEM`
2. Copy `computers/windows/docker/scripts/*` into `C:\OEM\*`

3. Create a folder `C:\TEMP`

4. Create a folder `C:\Data`
5. Copy `computers/windows/docker/data/init` into `C:\Data\init`
6. Copy a folders below into the `C:\Data\*`

- `../../servers/mcp_server_computer_control`
- `../../servers/server_browser_control`
- `../../servers/server_computer_control`
- `../../servers/server_evaluator`
- `../../servers/server_network_proxy`
- `../../servers/server_teams_control`
- `../../servers/server_appium`
- `../../servers/mcp_computer_control`
- `../../servers/mcp_playwright_wrapper`

6. Open Command Prompt as Administrator
7. Run the `install.bat` file with your username in the command prompt. Ex. `C:\OEM>install.bat Lukas1234 wmware`
8. When you see `Press any key to continue ...` in the command prompt, CLOSE IT!

> All logs are collected in the folder `C:\Logs` for troubleshooting

## 1.4 Port forwarding
