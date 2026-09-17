$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Python = Get-Command py -ErrorAction SilentlyContinue
if ($null -eq $Python) { $Python = Get-Command python -ErrorAction SilentlyContinue }
if ($null -eq $Python) { throw 'Python 3.11+ is required. Install it from https://www.python.org/downloads/.' }

$Venv = Join-Path $Root '.venv'
if (-not (Test-Path $Venv)) { & $Python.Source -3 -m venv $Venv }
$VenvPython = Join-Path $Venv 'Scripts\python.exe'
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $Root 'requirements.txt')

$EnvFile = Join-Path $Root '.env'
if (-not (Test-Path $EnvFile)) { Copy-Item (Join-Path $Root '.env.example') $EnvFile }

$TaskName = 'HumanAdvisorAI'
$Action = New-ScheduledTaskAction -Execute $VenvPython -Argument '-m uvicorn app.main:app --host 127.0.0.1 --port 8000' -WorkingDirectory $Root
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
try {
	Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Force -ErrorAction Stop | Out-Null
	Start-ScheduledTask -TaskName $TaskName
} catch {
	$Startup = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'
	New-Item -ItemType Directory -Force $Startup | Out-Null
	$Shell = New-Object -ComObject WScript.Shell
	$Shortcut = $Shell.CreateShortcut((Join-Path $Startup 'HumanAdvisorAI.lnk'))
	$Shortcut.TargetPath = $VenvPython
	$Shortcut.Arguments = '-m uvicorn app.main:app --host 127.0.0.1 --port 8000'
	$Shortcut.WorkingDirectory = $Root
	$Shortcut.Save()
	Start-Process -FilePath $VenvPython -ArgumentList '-m uvicorn app.main:app --host 127.0.0.1 --port 8000' -WorkingDirectory $Root
}
$BrowserTask = 'HumanAdvisorAI-Window'
$Browser = (Get-Command msedge -ErrorAction SilentlyContinue).Source
if (-not $Browser) { $Browser = (Get-Command chrome -ErrorAction SilentlyContinue).Source }
if ($Browser) {
	$BrowserAction = New-ScheduledTaskAction -Execute $Browser -Argument '--new-window http://127.0.0.1:8000/'
	try {
		Register-ScheduledTask -TaskName $BrowserTask -Action $BrowserAction -Trigger $Trigger -Principal $Principal -Force -ErrorAction Stop | Out-Null
		Start-ScheduledTask -TaskName $BrowserTask
	} catch {
		$Startup = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'
		New-Item -ItemType Directory -Force $Startup | Out-Null
		$Shell = New-Object -ComObject WScript.Shell
		$Shortcut = $Shell.CreateShortcut((Join-Path $Startup 'HumanAdvisorAI-Window.lnk'))
		$Shortcut.TargetPath = $Browser
		$Shortcut.Arguments = '--new-window http://127.0.0.1:8000/'
		$Shortcut.Save()
		Start-Process -FilePath $Browser -ArgumentList '--new-window http://127.0.0.1:8000/'
	}
}
Write-Output 'Human Advisor AI installed and started at login on http://127.0.0.1:8000/docs'
Write-Output 'Microphone access remains opt-in and must be started by the user.'