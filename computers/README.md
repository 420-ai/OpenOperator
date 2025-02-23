# Computers

This folder contains setup for computers that are operated via OpenOperator. Based on: https://github.com/dockur/windows

# 1. Windows

In folder `windows` is setup for a VM in docker.

## 1.1 Download Windows 11 Evaluation .iso file:

1. Visit [Microsoft Evaluation Center](https://info.microsoft.com/ww-landing-windows-11-enterprise.html), accept the Terms of Service, and download a **Windows 11 Enterprise Evaluation (90-day trial, English, United States)** ISO file [~6GB]
2. After downloading, rename the file to `setup.iso` and copy it to the directory `WindowsAgentArena/src/win-arena-container/vm/image`

## 1.2 Configure

You can configurate softwar that will be installed into the Windows via file `software.json`.

In case of any software, you can provide array of `mirrors` that will be used for installation.
In case of MS Teams application fill the `username` and `password` in order to pre-login for a particular user.

```JSON
{
  "Microsoft Teams": {
    "mirrors": ["https://aka.ms/teams64bitmsi"],
    "alias": "teams",
    "user": {
      "name": "INSERT HERE USERNAME",
      "password": "INSERT HERE PASSWORD"
    }
  }
}
```

## 1.3 Run

Navigate yourself into folder `windows` and open terminal. Run command `docker-compose up`. The command will use your .iso file, create a new `storage` folder that will represent your installation of W11.

- In case our removed the content of `storage` folder => The installation of W11 happens again
- In case you keep the `storage` folder after initial installation => W11 will start without initial installation

# TODO

Fix not working ffmpeg after first installation => workaround restart Docker container

- reason probably being that adding FFMPEG to the PATH happens on the same terminal as running the server2, resulting in server2 does not know that the PATH was updated and still using the old PATHs (without ffmpeg)
