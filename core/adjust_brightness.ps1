param([int]$level)
$monitors = Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods
foreach ($m in $monitors) {
    $m.WmiSetBrightness(1, $level)
}