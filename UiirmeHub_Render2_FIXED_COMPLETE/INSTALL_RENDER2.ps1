#Requires -Version 5.1
$ErrorActionPreference = 'Stop'
$repository = 'https://github.com/igorbakanov200505-create/Render2.git'
$actions = 'https://github.com/igorbakanov200505-create/Render2/actions'
$package = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoDir = Join-Path ([IO.Path]::GetTempPath()) ('Render2-install-' + [Guid]::NewGuid().ToString('N'))

function Fail($message) {
    Write-Host ''
    Write-Host ('ERROR: ' + $message) -ForegroundColor Red
    Write-Host 'If you have no Git, install Git for Windows: https://git-scm.com/downloads/win'
    Write-Host 'Alternative: GitHub > Add file > Create new file, name: .github/workflows/monitor.yml'
    Write-Host 'Copy the contents of WORKFLOW_COPY.txt from this package into it and Commit changes.'
    throw $message
}

try {
    Write-Host '===============================================' -ForegroundColor Cyan
    Write-Host ' UiirmeHub Pulse - GitHub Render2 installer' -ForegroundColor White
    Write-Host '===============================================' -ForegroundColor Cyan
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Fail 'Git for Windows is not installed.' }
    if (-not (Test-Path -LiteralPath (Join-Path $package '.github\workflows\monitor.yml'))) { Fail 'Workflow file was not extracted from the archive. Unzip the whole archive first.' }

    Write-Host '[1/4] Downloading current Render2 repository...' -ForegroundColor Yellow
    & git clone --depth 1 --branch main $repository $repoDir
    if ($LASTEXITCODE -ne 0) { Fail 'Cannot clone repository.' }

    Write-Host '[2/4] Installing website and workflow...' -ForegroundColor Yellow
    $paths = @('index.html', '.nojekyll', 'monitor/check.py', '.github/workflows/monitor.yml')
    foreach ($path in $paths) {
        $from = Join-Path $package $path
        $to = Join-Path $repoDir $path
        $directory = Split-Path -Parent $to
        if (-not (Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
        Copy-Item -LiteralPath $from -Destination $to -Force
    }
    # Keep user configuration and history already present on GitHub.
    foreach ($path in @('monitor/config.json','data/status.json')) {
        $from = Join-Path $package $path
        $to = Join-Path $repoDir $path
        $directory = Split-Path -Parent $to
        if (-not (Test-Path -LiteralPath $directory)) { New-Item -ItemType Directory -Path $directory -Force | Out-Null }
        if (-not (Test-Path -LiteralPath $to)) { Copy-Item -LiteralPath $from -Destination $to }
    }
    Copy-Item -LiteralPath (Join-Path $package 'README.md') -Destination (Join-Path $repoDir 'README.md') -Force

    Push-Location $repoDir
    try {
        Write-Host '[3/4] Creating Git commit...' -ForegroundColor Yellow
        & git add -- index.html .nojekyll README.md monitor/check.py monitor/config.json data/status.json .github/workflows/monitor.yml
        if ($LASTEXITCODE -ne 0) { Fail 'Cannot add files to Git.' }
        & git diff --cached --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host 'All required files are already committed.' -ForegroundColor Green
        } else {
            & git -c user.name='UiirmeHub Setup' -c user.email='uiirmehub-setup@users.noreply.github.com' commit -m 'fix: install Render2 Pulse monitoring workflow and site'
            if ($LASTEXITCODE -ne 0) { Fail 'Git commit failed.' }
            Write-Host '[4/4] Sending changes to your GitHub...' -ForegroundColor Yellow
            & git push origin main
            if ($LASTEXITCODE -ne 0) { Fail 'Git push failed. Sign in to GitHub when prompted or use GitHub Desktop.' }
        }
    } finally { Pop-Location }
    Write-Host ''
    Write-Host 'SUCCESS: Workflow is now in .github/workflows/monitor.yml' -ForegroundColor Green
    Write-Host 'Open Actions: ' $actions
    Write-Host 'If GitHub Pages is not active: Settings > Pages > Source > GitHub Actions.'
    Start-Process $actions
} catch {
    Write-Host ''
    Write-Host ('Installation stopped: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
} finally {
    # Remove temporary clone; originals and repository stay untouched.
    if (Test-Path -LiteralPath $repoDir) { Remove-Item -LiteralPath $repoDir -Recurse -Force -ErrorAction SilentlyContinue }
}
