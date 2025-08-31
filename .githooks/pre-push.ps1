# PowerShell pre-push hook for Windows
# Prevents direct pushes to main/master when ALLOW_DIRECT_PUSH_TO_MAIN is false

param(
    [string]$remote,
    [string]$url
)

# Read stdin for push information
$input = [Console]::In.ReadToEnd()
if ($input) {
    $lines = $input -split "`n"
    
    foreach ($line in $lines) {
        if ($line.Trim() -eq "") { continue }
        
        $parts = $line -split " "
        if ($parts.Length -ge 3) {
            $remoteRef = $parts[2]
            $branch = $remoteRef -replace "refs/heads/", ""
            
            # Check if pushing to main or master
            if ($branch -eq "main" -or $branch -eq "master") {
                
                # Check for environment variable
                $allowPush = $env:ALLOW_DIRECT_PUSH_TO_MAIN
                
                # If not in environment, check .env file
                if (-not $allowPush -and (Test-Path ".env")) {
                    $envContent = Get-Content ".env" | Where-Object { $_ -match "^ALLOW_DIRECT_PUSH_TO_MAIN=" }
                    if ($envContent) {
                        $allowPush = ($envContent -split "=")[1].Trim()
                    }
                }
                
                # Default to false if not set
                if (-not $allowPush) {
                    $allowPush = "false"
                }
                
                # Check if push is allowed
                if ($allowPush -eq "false" -or $allowPush -eq "0" -or $allowPush -eq "no") {
                    Write-Host "❌ Direct push to $branch branch is disabled!" -ForegroundColor Red
                    Write-Host ""
                    Write-Host "Branch protection is enabled. Please:" -ForegroundColor Yellow
                    Write-Host "  1. Create a feature branch: git checkout -b feature/your-feature" -ForegroundColor Green
                    Write-Host "  2. Push your branch: git push origin feature/your-feature" -ForegroundColor Green
                    Write-Host "  3. Create a Pull Request on GitHub"
                    Write-Host ""
                    Write-Host "To temporarily allow direct pushes (NOT RECOMMENDED):" -ForegroundColor Yellow
                    Write-Host "  - Set ALLOW_DIRECT_PUSH_TO_MAIN=true in your .env file" -ForegroundColor Green
                    Write-Host "  - Or run: `$env:ALLOW_DIRECT_PUSH_TO_MAIN='true'; git push" -ForegroundColor Green
                    Write-Host ""
                    exit 1
                }
                else {
                    Write-Host "⚠️  Warning: Direct push to $branch branch!" -ForegroundColor Yellow
                    Write-Host "Branch protection is currently disabled (ALLOW_DIRECT_PUSH_TO_MAIN=$allowPush)" -ForegroundColor Yellow
                    Write-Host "Consider creating a pull request instead for code review." -ForegroundColor Yellow
                    Write-Host ""
                    Write-Host "Pushing directly to $branch in 3 seconds... Press Ctrl+C to cancel"
                    Start-Sleep -Seconds 3
                }
            }
        }
    }
}

exit 0