# PowerShell script to start all Distributed Systems Backend Services
# For Windows users

# Get the directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Array to track process objects
$Processes = @()

# Cleanup function
function Cleanup {
    Write-Host "`nShutting down all services..." -ForegroundColor Yellow
    
    # Kill processes by port
    Write-Host "Stopping services on ports..." -ForegroundColor Cyan
    Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort 3002 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort 1099 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    
    # Kill Java processes
    Get-Process -Name java -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*RMIServer*" -or $_.CommandLine -like "*HttpRmiGateway*" -or $_.CommandLine -like "*rmiregistry*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Kill Python processes
    Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" -or $_.CommandLine -like "*gunicorn*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Close tracked PowerShell windows
    foreach ($proc in $Processes) {
        if (-not $proc.HasExited) {
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Host "All services stopped and ports released." -ForegroundColor Green
    exit
}

# Register cleanup on Ctrl+C
Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Cleanup } | Out-Null
$null = [Console]::TreatControlCAsInput = $false

Write-Host "`nStarting Distributed Systems Backend Services...`n" -ForegroundColor Green

# Module 1: Complaint Management System (Socket Server)
Write-Host "Starting Module 1: Complaint Management System..." -ForegroundColor Yellow
$Processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\Module 1'; python main.py" -PassThru
Start-Sleep -Seconds 2

# Module 2: Hostel Room Management (RMI + HTTP Gateway)
Write-Host "Starting Module 2: Hostel Room Management..." -ForegroundColor Yellow

# Compile Java files
Write-Host "Compiling Java files..." -ForegroundColor Cyan
Set-Location "Module 2"
javac *.java
if ($LASTEXITCODE -ne 0) {
    Write-Host "Java compilation failed!" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Start RMI Registry
$Processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\Module 2'; rmiregistry 1099" -PassThru
Start-Sleep -Seconds 2

# Start RMI Server
$Processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\Module 2'; java RMIServer" -PassThru
Start-Sleep -Seconds 2

# Start HTTP Gateway
$Processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\Module 2'; java HttpRmiGateway" -PassThru
Start-Sleep -Seconds 2

# Module 4: WebRTC Signaling Server (WebSocket)
Write-Host "Starting Module 4: WebRTC Signaling Server..." -ForegroundColor Yellow
$Processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir\Module 4'; python main.py" -PassThru
Start-Sleep -Seconds 2

# Wrapper: Main API Gateway (Flask + SocketIO)
Write-Host "Starting Wrapper: Main API Gateway..." -ForegroundColor Yellow
$Processes += Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ScriptDir'; gunicorn -k eventlet -w 1 wrapper:app --bind 0.0.0.0:3001" -PassThru

Write-Host "`nAll services started!" -ForegroundColor Green
Write-Host "Check the opened PowerShell windows for each service." -ForegroundColor Green
Write-Host "`nService URLs:" -ForegroundColor Yellow
Write-Host "  - Module 1 (Complaints):     tcp://localhost:3000" -ForegroundColor White
Write-Host "  - Module 2 (HTTP Gateway):   http://localhost:3002" -ForegroundColor White
Write-Host "  - Module 2 (RMI Registry):   rmi://localhost:1099" -ForegroundColor White
Write-Host "  - Module 4 (WebRTC):         ws://localhost:8765" -ForegroundColor White
Write-Host "  - Wrapper (Main API):        http://localhost:3001" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop all services" -ForegroundColor Yellow

# Wait for user interrupt
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Cleanup
}
