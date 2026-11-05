# Optional PowerShell entry; use the existing execution policy as provided.
$ErrorActionPreference = 'Stop'
Write-Output "cwd=$((Get-Location).Path)"
Write-Output "harness=$PSScriptRoot"
foreach ($name in @('bash', 'sh', 'python3', 'python', 'codex')) {
    $found = Get-Command $name -ErrorAction SilentlyContinue
    Write-Output "$name=$($found.Source)"
}
foreach ($runtime in @('python3', 'python')) {
    $found = Get-Command $runtime -CommandType Application -ErrorAction SilentlyContinue
    if ($found) {
        try {
            & $found.Source -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>$null
        } catch {
            Write-Output "$runtime failed to execute; trying next runtime."
            continue
        }
        if ($LASTEXITCODE -eq 0) {
            & $found.Source "$PSScriptRoot/tools/start.py" @args
            exit $LASTEXITCODE
        }
        Write-Output "$runtime version check failed; trying next runtime."
    }
}
Write-Output 'Python 3.10+ unavailable; no installation/launch. Automatic recovery: no.'
Write-Output 'Next: in the provided Codex chat, enter:'
Write-Output "Read the task README and existing AGENTS.md first, then '$PSScriptRoot/AGENTS.md' and '$PSScriptRoot/templates/START.md' as auxiliary instructions; start P1 analysis and continue through P7."
exit 2
