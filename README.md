# ha-photoframe-denver PFF-1082

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
- ./adb connect 192.168.40.76:5555 (response: connected to 192.168.40.76:5555)
- Haal usb kabel uit pc of photoframe
- ./adb devices (response: List of devices attached 192.168.40.76:5555      device)

Aansturen ledrand photframe
- adb inschakelen via wifi (bovenstaande stappen)
- ./adb shell "echo '<95,255,255,48>' > /sdcard/frameo_light.txt" (<brightness,r,g,b>)
- ./adb shell "echo '<0,0,0,0>' > /sdcard/frameo_light.txt" (Uit)
- ./adb shell "echo '<95,255,0,0>' > /sdcard/frameo_light.txt" (Rood)

Commando's
- ./adb reboot (herstarten)
- ./adb shell am start -n de.ozerov.fully/.MainActivity (Fully Kiosk App opstarten)
- ./adb shell settings put system screen_brightness 255 (helderheid scherm, 255=maximaal 0=minimaal)
