# Computers

This folder contains setup for computers that are operated via OpenOperator. Based on: https://github.com/dockur/windows

# 1. Windows

In folder `windows/docker` is setup for a VM in docker.

## 1.1 Download Windows 11 .iso file:

1a. Visit [Microsoft Evaluation Center](https://info.microsoft.com/ww-landing-windows-11-enterprise.html), accept the Terms of Service, and download a **Windows 11 Enterprise Evaluation (90-day trial, English, United States)** ISO file [~6GB] 64-bit edition !!

1b. Visit [Windows Software Download center](https://www.microsoft.com/en-us/software-download/windows11), download **Windows 11 (multi-edition ISO for x64 devices)** - Win11_24H2_English_x64.iso [~6GB]

2. After downloading, rename the file to `win.iso` and copy it to the directory `iso` (if does not exist, create one in this directory)

## 1.2 Configure

You can configurate software that will be installed on the Windows via file `windows/docker/data/init/software.json`.

In case of any software, you can provide array of `mirrors` that will be used for installation.

```JSON
{
  "Microsoft Teams": {
    "mirrors": ["https://aka.ms/teams64bitmsi"],
    "alias": "teams"
  }
}
```

## 1.3 Run (prebuilt)

Navigate yourself into folder `windows/docker` and open terminal. Run command `docker-compose up`. The command will use your .iso file, create a new `storage` folder that will represent your installation of W11.

- In case our removed the content of `storage` folder => The installation of W11 happens again
- In case you keep the `storage` folder after initial installation => W11 will start without initial installation

### 1.4 Run (local)

We can run version with pre-builded docker container `lukaskellerstein/windows-computer:<VERSION>` or we can build locally new docker container. Navigate to `windows/docker` and run command `docker compose -f compose-local.yml up`

### 1.5 VNC

You can open the VM via VNC => `http://localhost:8006`

### 1.6 RDP

1. Change a default `Docker` user password from "" to "1234" via VNC

```bash
net user Docker 1234
```

2. Set an `admin` connection in Microsoft Remote Desktop software

**On Windows**

Run mstsc via command

```bash
mstsc /admin
```

### 1.6 Test in Docker

On the `Windows 11` are running a open-operator servers:

- server computer control on port `5050`
- server browser control on port `5051`

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

### 1.7 Test on host

You can test the openoperator servers from host by running command `curl -v http://127.0.0.1:5050/healthcheck`, you should see response such as

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

# 2. Post-installation procedure

## 2.1 Show hidden files

Control Panel > File Explorer Options > View > Show hidden files

## 2.2 Check mitmproxy certs

Check that mitmproxy certs are installed.

Search > Manage computer certificates > Truster Root Certification Authorities > Certificates > mitmproxy

## 2.3 Check Teams has installed configuration

Check that `configuration.json` exist on path `C:\Users\Docker\AppData\Local\Packages\MSTeams_8wekyb3d8bbwe\LocalCache\Microsoft\MSTeams\configuration.json`.

If not, call the `teams_control_server` on the computer.

A) via test script - `openoperator/servers/test/test_teams_control_server.py`

B) via curl

## 2.4 Prepare Teams

1. Open Teams > Finish the "Last Step" dialog
2. Login into Teams

## 2.9 Notepad

Notepad - set open alway in new window
