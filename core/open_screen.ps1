Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class MonitorHelper {
    [DllImport("user32.dll")]
    public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam);
}
"@
# SendMessage to turn on monitor
[MonitorHelper]::SendMessage(-1, 0x0112, 0xF170, -1)