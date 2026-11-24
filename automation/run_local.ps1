param([string]$PythonExe = 'python')
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path $PSScriptRoot -Parent
& $PythonExe (Join-Path $ProjectRoot 'src/pipeline.py')
if ($LASTEXITCODE -ne 0) { throw 'Data pipeline failed; summary verification not run.' }
& $PythonExe (Join-Path $ProjectRoot 'src/verify_summary.py')
if ($LASTEXITCODE -ne 0) { throw 'AI summary failed verification. Draft a new summary from the current evidence packet.' }
# Does not regenerate source data, call an AI service, create a schedule, or send reports.
