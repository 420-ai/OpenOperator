$pythonPath = [System.Environment]::GetEnvironmentVariable("PYTHON", "Process")
Start-Process -NoNewWindow -FilePath $pythonPath -ArgumentList "-u \\host.lan\Data\server2\main.py"
