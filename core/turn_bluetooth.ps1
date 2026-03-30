param([string]$action)

$bt = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*Bluetooth*" }

if ($action -eq "off") {
    foreach ($device in $bt) {
        Disable-PnpDevice -InstanceId $device.InstanceId -Confirm:$false
    }
    Write-Output "Bluetooth turned off"
}
elseif ($action -eq "on") {
    foreach ($device in $bt) {
        Enable-PnpDevice -InstanceId $device.InstanceId -Confirm:$false
    }
    Write-Output "Bluetooth turned on"
}