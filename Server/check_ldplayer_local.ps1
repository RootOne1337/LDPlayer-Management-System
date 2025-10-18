# Simple LDPlayer Check - Direct

Write-Host "`n==============================" -ForegroundColor Cyan
Write-Host "  LDPlayer Check - LOCAL" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# Check LDPlayer9
Write-Host "`nChecking LDPlayer 9..." -ForegroundColor Yellow

$ldpath = "C:\LDPlayer\LDPlayer9"
if (Test-Path $ldpath) {
    Write-Host "✅ LDPlayer9 found at: $ldpath" -ForegroundColor Green
    
    $dnconsole = "$ldpath\dnconsole.exe"
    if (Test-Path $dnconsole) {
        Write-Host "✅ dnconsole.exe found!" -ForegroundColor Green
        
        Write-Host "`nListing emulators..." -ForegroundColor Yellow
        & "$dnconsole" list
        
        Write-Host "`n✅ SUCCESS!" -ForegroundColor Green
    } else {
        Write-Host "❌ dnconsole.exe NOT found!" -ForegroundColor Red
    }
} else {
    Write-Host "❌ LDPlayer9 NOT found at: $ldpath" -ForegroundColor Red
}

Write-Host "`n==============================" -ForegroundColor Cyan
