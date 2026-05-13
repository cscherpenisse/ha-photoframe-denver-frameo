import asyncio
from adb_shell.adb_device_async import AdbDeviceTcpAsync
from adb_shell.exceptions import AdbConnectionError


class FrameoADB:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.device = AdbDeviceTcpAsync(host, port)
        self.connected = False

    async def connect(self):
        """Establish ADB connection."""
        try:
            await self.device.connect(rsa_keys=[])
            self.connected = True
        except Exception:
            self.connected = False
            raise

    async def ensure_connected(self):
        """Ensure ADB connection with retries."""
        if self.connected:
            return

        for _ in range(3):
            try:
                await self.connect()
                return
            except Exception:
                await asyncio.sleep(1)

        self.connected = False
        raise AdbConnectionError("Unable to connect to ADB device")

    async def shell(self, command: str):
        """Execute ADB shell command safely."""
        await self.ensure_connected()
        return await self.device.shell(command)

    # -------------------------
    # LED CONTROL
    # -------------------------

    async def read_led_state(self) -> str:
        """Read LED state from file on device."""
        try:
            raw = await self.shell("cat /sdcard/frameo_light.txt")
            return raw.strip()
        except Exception:
            # fallback if file missing or ADB fails
            return "<0,0,0,0>"

    async def set_led_state(self, brightness: int, r: int, g: int, b: int):
        """Write LED state to device."""
        cmd = (
            f"echo '<{brightness},{r},{g},{b}>' "
            f"> /sdcard/frameo_light.txt"
        )
        await self.shell(cmd)

    # -------------------------
    # SCREEN CONTROL
    # -------------------------

    async def toggle_screen(self):
        """Toggle screen power."""
        await self.shell("input keyevent 26")

    async def set_screen_brightness(self, brightness: int):
        """Set Android system brightness."""
        await self.shell(
            f"settings put system screen_brightness {brightness}"
        )
    # -------------------------
    # SCREEN BRIGHTNESS
    # -------------------------

async def get_screen_brightness(self):
    """Read Android screen brightness."""
    result = await self.shell(
        "settings get system screen_brightness"
    )

    try:
        return int(result.strip())
    except Exception:
        return 127


async def set_screen_brightness(self, brightness: int):
    """Set Android screen brightness."""
    await self.shell(
        f"settings put system screen_brightness {brightness}"
    )
