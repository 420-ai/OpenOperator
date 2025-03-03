# Running as a separate server on VM

This server can be running in classic Windows 11 VM (ex. Parallels for Mac). Follow the steps below.

## Prerequisites

Since this server will run directly on the VM and not in the VM inside Docker, we need to adjust logging path.

In the `main.py` file, change line defining path to the logs

Replace
```
log_file = os.path.join("\\\\host.lan\\Data", "logs", "server_2.log")
```

For
```
log_file = os.path.join(".", "logs", "server_2.log")
```

and create a folder `logs` manually.


## Run

In this folder open `Anaconda Prompt` and run commands below

In case the environment is not already created run
```
conda create --name server2
```

Continue with activating the environment, install dependencies and run it.
```
conda activate server2
pip install -r requirements.txt
python main.py
```

## Port forwarding

If you want to use port forwarding to access the server via `127.0.0.1:5050` on the host (server is running on VM on port `:5000`), you need to make sure steps below are done.

### 1.1 Windows Firewall

Windows Defender Firewall may be blocking external connections. To allow traffic:
1. Open **Windows Defender Firewall with Advanced Security**.
2. Go to **Inbound Rules** > **New Rule**.
3. Select **Port** > Choose **TCP** and enter `5000`.
4. Allow the connection for **all networks** (private, public, domain).
5. Name the rule and save it.


### 1.2 VM software - Parallels Desktop

In order to access the server via port `5050`, you need to setup a port forwarding in paralells desktop as follows.

1. Open **Parallels Desktop** > **Configuration** for your Windows VM.
2. Go to **Hardware** > **Network** > **Advanced Settings**.
3. Ensure you've added a **port forwarding rule**:
   - **Protocol**: TCP
   - **Source port**: `5050`
   - **Forward to**: `Windows 11` (or Name of your VM)
   - **Destination port**: `5000`

### 1.3 Test it

**Step 1** is to ensure the server is running correctly from the Windows VM. Open url (`http://127.0.0.1:5000/probe`) in browser on your Windows 11 machine. You should see response:
```
{
  "message": "Service is operational",
  "status": "Probe successful"
}
```

**Step 2** is to ensure that your server is also accessible from the host (ex. MacOS). Run in your terminal following command:
```sh
curl -v http://127.0.0.1:5050/probe
```

You should see response:
```
{
  "message": "Service is operational",
  "status": "Probe successful"
}
```
