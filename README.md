# Denver / Frameo Photoframe Home Assistant Integration (Under construction, not yet bug-free)

Features:

- LED control
- RGB support
- Brightness
- Screen power
- ADB over TCP
- Denver PFF support
- Frameo support

Tested devices: Denver PFF-1082

# Installation
HACS 
1. Open HACS in Home Assistant
2. Click on the three dots in the top right corner
3. Select Custom repositories
4. Add the repository URL: https://github.com/cscherpenisse/ha-photoframe-denver-frameo
5. Select Integration as the category
6. Click Add
7. Search for "Denver Frameo Photoframe" in HACS and install it
8. Restart Home Assistant
9. Add the integration via Settings → Devices & Services → Add Integration

======================================================================================
Stappenplan installeren Kiosk App

- Installeren van adb tool op windows PC C:\platform-tools
https://developer.android.com/tools/releases/platform-tools
Downloaden, file uitpakken en de map platform-tools verplaatsen naar de C-schijf

- Installeren van Nova Launcher v6-2-19
Photoframe verbinden via usb met PC
Start windows powershell op en ga in de map platform-tools
./adb install "bestandsnaam.apk"
- Installeren van Kiosk v1.60.1
./adb install "bestandsnaam.apk"


Algemene uitleg links:
https://gist.github.com/cjlawson02/cdda949d9ce107040bebbc9a8ef3853f

Inschakelen adb via wifi
- Verbind photoframe via usb kabel met pc
- ./adb devices (response: 59734398        device)
- ./adb tcpip 5555 (response: restarting in TCP mode port: 5555)
- ./adb connect 192.168.xx.xx:5555 (response: connected to 192.168.xx.xx:5555)
- Haal usb kabel uit pc of photoframe
- ./adb devices (response: List of devices attached 192.168.xx.xx:5555      device)

Standaard opstarten adb via wifi instellen
- ./adb shell setprop persist.adb.tcp.port 5555
- ./adb reboot
- ./adb connect 192.168.xx.xx:5555

Aansturen ledrand photoframe
- adb inschakelen via wifi (bovenstaande stappen)
- ./adb shell "echo '<95,255,255,48>' > /sdcard/frameo_light.txt" (<brightness,r,g,b>)
- ./adb shell "echo '<0,0,0,0>' > /sdcard/frameo_light.txt" (Uit)
- ./adb shell "echo '<95,255,0,0>' > /sdcard/frameo_light.txt" (Rood)

Commando's
- ./adb reboot (herstarten)
- ./adb shell am start -n de.ozerov.fully/.MainActivity (Fully Kiosk App opstarten)
- ./adb shell settings put system screen_brightness 255 (helderheid scherm, 255=maximaal 0=minimaal)

Via Home Assistant, Actie (Ontwikkelaarshulpmiddelen)
action: androidtv.adb_command
data:
  command: echo '<255,255,0,0>' > /sdcard/frameo_light.txt
target:
  entity_id: media_player.android_tv_192_168_xx_xx
