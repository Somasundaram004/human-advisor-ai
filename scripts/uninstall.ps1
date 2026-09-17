$ErrorActionPreference = 'Stop'
Unregister-ScheduledTask -TaskName 'HumanAdvisorAI' -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName 'HumanAdvisorAI-Window' -Confirm:$false -ErrorAction SilentlyContinue
$Startup = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'
Remove-Item (Join-Path $Startup 'HumanAdvisorAI.lnk') -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $Startup 'HumanAdvisorAI-Window.lnk') -Force -ErrorAction SilentlyContinue
Write-Output 'Human Advisor AI auto-start task removed. Data and virtual environment were left intact.'