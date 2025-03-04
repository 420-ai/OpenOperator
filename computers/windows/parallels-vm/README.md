# Computers

This folder contains setup for computers that are operated via OpenOperator.

# 1. Windows

In folder `parallels-vm` is setup for a VM in [Paralells](https://parallels.com/).

## 1.1 Download Windows 11 Evaluation .iso file:

1. Visit [Microsoft Evaluation Center](https://info.microsoft.com/ww-landing-windows-11-enterprise.html), accept the Terms of Service, and download a **Windows 11 Enterprise Evaluation (90-day trial, English, United States)** ISO file [~6GB]

> ARM64 edition !!

2. After downloading, rename the file to `win.iso` and copy it to the directory `iso` (if does not exist, create one in this directory)

## 1.2 Install VM

Install Windows manually. Create user `Docker` with empty password.

> TURN OFF automatical pausing of VM after 30 seconds.

TODO: Prepare `unattend.xml` installation

## 1.3 Setup VM

1. Create a folder `C:\INSTALL`
2. Create a folder `C:\INSTALL\logs`
3. Create a folder `C:\TEMP`
4. Copy the content of this folder into path `C:\INSTALL`

5. Open Command Prompt as Administrator
6. Run the `install.bat` file with your username in the command prompt. Ex. `C:\INSTALL>install.bat lukaskellerstein`
