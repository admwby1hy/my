chcp 65001
[system.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null
 
#创建 NotifyIcon 对象
$balloon = New-Object System.Windows.Forms.NotifyIcon
$path = Get-Process -id $pid | Select-Object -ExpandProperty Path
$icon = [System.Drawing.Icon]::ExtractAssociatedIcon($path)
$balloon.Icon = $icon
$balloon.BalloonTipIcon = 'Info'
$balloon.BalloonTipText = $args[0]
$balloon.BalloonTipTitle = 'info'
$balloon.Visible = $true
 
#显示气球提示框
$balloon.ShowBalloonTip(10000)

#$balloon

#exit