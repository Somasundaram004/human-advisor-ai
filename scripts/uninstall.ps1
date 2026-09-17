$ErrorActionPreference = 'Stop'
Unregister-ScheduledTask -TaskName 'HumanAdvisorAI' -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName 'HumanAdvisorAI-Window' -Confirm:$false -ErrorAction SilentlyContinue
Write-Output 'Human Advisor AI auto-start task removed. Data and virtual environment were left intact.'