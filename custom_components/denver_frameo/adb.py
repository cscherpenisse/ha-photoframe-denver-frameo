from adb_shell.adb_device_async import AdbDeviceTcpAsync
from adb_shell.auth.sign_pythonrsa import PythonRSASigner


class FrameoADB:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.device = AdbDeviceTcpAsync(host, port)

    async def connect(self):
        await self.device.connect(rsa_keys=[])

    async def shell(self, command: str):
        return await self.device.shell(command)

    async def read_led_state(self):
        raw = await self.shell("cat /sdcard/frameo_light.txt")
        return raw.strip()

    async def set_led_state(self, brightness, r, g, b):
        cmd = f"echo '<{brightness},{r},{g},{b}>' > /sdcard/frameo_light.txt"
        await self.shell(cmd)

    async def set_screen_brightness(self, brightness):
        await self.shell(
            f"settings put system screen_brightness {brightness}"
        )

    async def toggle_screen(self):
        await self.shell("input keyevent 26")
