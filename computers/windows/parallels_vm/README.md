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

> TURN OFF automatical pausing of VM after 30 seconds.
> Disable sharing applications between Mac > Windows (Optional)
> Disable sharing applications between Windows > Mac (Optional)

## 1.3 Share folder to VM

Share folder `computers/windows/parallels_vm` into VM. Then you will see new network disk in Windows 11 VM named `parallels_vm on Mac (Y:)`.

## 1.4 Setup VM

1. Create a folder `C:\INSTALL`
2. Create a folder `C:\TEMP`

3. Copy a folders below into the `data` folder in this directory

- `../../servers/server_browser_control`
- `../../servers/server_computer_control`
- `../../servers/evaluator`
- `../../servers/network_proxy`

4. Adjust the `.env` files in each server => Uncomment the section for `# Parallels - Windows` and comment out the other variants
5. Copy the content of this folder into path `C:\INSTALL`

6. Open Command Prompt as Administrator
7. Run the `install.bat` file with your username in the command prompt. Ex. `C:\INSTALL>install.bat lukaskellerstein`

8. When you see `Press any key to continue ...` in the command prompt, CLOSE IT!

> All logs are collected in the folder `C:\INSTALL\data\logs` for troubleshooting

## 1.4 Port forwarding

On the `VM` are running a open-operator servers:

- server computer control on port `5050`
- server browser control on port `5051`
- server network proxy on port `5052`
- server evaluator on port `5053`

You can test them if they are running correctly by opening browser with urls:

- `http://localhost:5050/healthcheck`
- `http://localhost:5051/healthcheck`

and you should see responses as

```
{
  "status": "Successful"
  "message": "Service is operational!",
}
```

In order to access the open-operator servers running on `VM` from the `host`, we need to setup port forwarding on the parallels. The steps below describes exposing only port `5050`, you need do the same steps for other ports as well (`5051`).

- Protocol: `TCP`
- Source port: `5050`
- Forward To: VM - `<Name of the VM>`
- Destination port: `5050`

Now you can test that you can access the server from host by running command `curl -v http://127.0.0.1:5050/healthcheck`, you should see response such as

```
*   Trying 127.0.0.1:5050...
* Connected to 127.0.0.1 (127.0.0.1) port 5050
> GET /probe HTTP/1.1
> Host: 127.0.0.1:5050
> User-Agent: curl/8.7.1
> Accept: */*
>
* Request completely sent off
< HTTP/1.1 200 OK
< Server: Werkzeug/3.1.3 Python/3.10.0
< Date: Tue, 04 Mar 2025 12:16:10 GMT
< Content-Type: application/json
< Content-Length: 74
< Connection: close
<
{
  "status": "Successful",
  "message": "Service is operational!"
}
* Closing connection
```
