# Create log directory if it doesn't exist
$logDir = "C:\Logs"
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir
}

# Define log file path
$logFile = "$logDir\startup-log.txt"

# Get current timestamp (when the script was triggered)
$triggeredAt = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Get system boot time
$bootTime = (Get-CimInstance -ClassName Win32_OperatingSystem).LastBootUpTime

# Get current user
$currentUser = $env:USERNAME

# Get user logon time (best-effort: last successful interactive logon)
$logonEvent = Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624} -MaxEvents 50 |
    Where-Object {
        $_.Properties[5].Value -eq $currentUser -and
        ($_.Properties[8].Value -eq "2" -or $_.Properties[8].Value -eq "10") # 2 = Interactive, 10 = RemoteInteractive
    } |
    Sort-Object TimeCreated -Descending |
    Select-Object -First 1

$logonTime = if ($logonEvent) { $logonEvent.TimeCreated } else { "N/A" }

# Format log entry
$entry = @"
----------------------------------------
[Script Triggered]: $triggeredAt
User              : $currentUser
System Boot Time  : $bootTime
User Logon Time   : $logonTime
----------------------------------------
"@

# Write to log
Add-Content -Path $logFile -Value $entry
