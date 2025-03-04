# Computers

This folder contains setup for computers that are operated via OpenOperator.

# 1. Windows

In folder `parallels-vm` is setup for a VM in [Paralells](https://parallels.com/).

## 1.1 Download Windows 11 Evaluation .iso file:

1. Visit [Microsoft Software Download](https://www.microsoft.com/en-us/software-download/windows11arm64), select language, and download ISO file
2. The downloaded file looks like `Win11_24H2_English_Arm64.iso` [~5GB]

## 1.2 Install VM

Install Windows manually from the `iso` file you downloaded. Choose `Windows 11 Pro` as version.

> TURN OFF automatical pausing of VM after 30 seconds.
> Disable sharing applications between Mac > Windows
> Disable sharing applications between Windows > Mac

## 1.3 Setup VM

1. Create a folder `C:\INSTALL`
2. Create a folder `C:\INSTALL\logs`
3. Create a folder `C:\TEMP`
4. Copy the content of this folder into path `C:\INSTALL`

5. Open Command Prompt as Administrator
6. Run the `install.bat` file with your username in the command prompt. Ex. `C:\INSTALL>install.bat lukaskellerstein`

## 1.4 Port forwarding

On the `VM` is running an `open-operator server` on port `5050`. You can test that it is running correctly by opening browser with url `http://localhost:5000/probe`, you should see response as

```
{
  "message": "Service is operational",
  "status": "Probe successful"
}
```

In order to access the `open-operator server` running on `VM` from the `host`, we need to setup port forwarding on the parallels.

- Protocol: `TCP`
- Source port: `5050`
- Forward To: VM - `<Name of the VM>`
- Destination port: `5000`

Now you can test that you can access the server from host by running command `curl -v http://127.0.0.1:5050/probe`, you should see response such as

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
  "message": "Service is operational",
  "status": "Probe successful"
}
* Closing connection
```
