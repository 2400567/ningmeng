# Create Desktop Shortcut Script
$WshShell = New-Object -comObject WScript.Shell
$desktopPath = [System.Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path -Path $desktopPath -ChildPath 'AI Data Analysis System.lnk'
$targetPath = 'd:\AI\AI数据分析系统_桌面启动.bat'

# Create shortcut
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.WorkingDirectory = 'd:\AI'
$Shortcut.IconLocation = 'shell32.dll,4'
$Shortcut.Description = 'AI Data Analysis System'
$Shortcut.Save()

Write-Host "✅ Desktop shortcut created successfully: $shortcutPath"