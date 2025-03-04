# Computers

This folder contains setup for computers that are operated via OpenOperator. Based on: https://github.com/dockur/windows

# 1. Windows

In folder `windows` is setup for a VM in docker.

## 1.1 Download Windows 11 Evaluation .iso file:

1. Visit [Microsoft Evaluation Center](https://info.microsoft.com/ww-landing-windows-11-enterprise.html), accept the Terms of Service, and download a **Windows 11 Enterprise Evaluation (90-day trial, English, United States)** ISO file [~6GB]

> 64-bit edition !!

2. After downloading, rename the file to `win.iso` and copy it to the directory `iso` (if does not exist, create one in this directory)

## 1.2 Configure

You can configurate software that will be installed on the Windows via file `windows/data/init/software.json`.

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

Navigate yourself into folder `windows` and open terminal. Run command `docker-compose up`. The command will use your .iso file, create a new `storage` folder that will represent your installation of W11.

- In case our removed the content of `storage` folder => The installation of W11 happens again
- In case you keep the `storage` folder after initial installation => W11 will start without initial installation

### 1.4 Run (local)

We can run version with pre-builded docker container `lukaskellerstein/windows-computer:<VERSION>` or we can build locally new docker container. Navigate to `windows` and run command `docker compose -f compose-local.yml up`

### 1.5 RDP

You can open the VM via `http://localhost:8006`
