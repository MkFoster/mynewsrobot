# MyNewsRobot - Quick Start Script
# Run this after cloning to set up your development environment

Write-Host "🤖 MyNewsRobot - Phase 1 Setup" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python 3\.1[3-9]") {
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python 3.13+ required. Found: $pythonVersion" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create .env if it doesn't exist
Write-Host "`nSetting up environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env already exists" -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env from template" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env with your actual credentials" -ForegroundColor Yellow
}

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
$adkCheck = python -c "import google.adk; print('OK')" 2>&1
if ($adkCheck -eq "OK") {
    Write-Host "✅ Google ADK installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Google ADK not found" -ForegroundColor Red
    exit 1
}

# Check configuration files
Write-Host "`nChecking configuration files..." -ForegroundColor Yellow
$configFiles = @(
    "config/news_sources.yaml",
    "config/topic_priorities.yaml",
    "config/weekly_bookmarks.yaml",
    "config/wordpress.yaml",
    "config/writing_style.yaml"
)

$allConfigsExist = $true
foreach ($file in $configFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file missing" -ForegroundColor Red
        $allConfigsExist = $false
    }
}

if ($allConfigsExist) {
    Write-Host "✅ All configuration files present" -ForegroundColor Green
} else {
    Write-Host "❌ Some configuration files are missing" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "✅ Phase 1 Setup Complete!" -ForegroundColor Green
Write-Host "================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Edit .env with your credentials" -ForegroundColor White
Write-Host "  2. Update config/news_sources.yaml with your news sources" -ForegroundColor White
Write-Host "  3. Update config/wordpress.yaml with your WordPress URL" -ForegroundColor White
Write-Host "  4. Run: python src/main.py" -ForegroundColor White
Write-Host "  5. Test: curl http://localhost:8080/health`n" -ForegroundColor White

Write-Host "For detailed setup instructions, see: docs/setup.md`n" -ForegroundColor Cyan

# Offer to run tests
$runTests = Read-Host "Would you like to run tests now? (y/n)"
if ($runTests -eq "y") {
    Write-Host "`nRunning tests..." -ForegroundColor Yellow
    pytest tests/ -v
}

Write-Host "`n🚀 Ready to build! See PROJECT_PLAN.md for next phases.`n" -ForegroundColor Green
