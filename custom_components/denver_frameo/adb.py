import asyncio

from adb_shell.adb_device_async import (
    AdbDeviceTcpAsync,
)


class FrameoADB:
    def __init__(
        self,
        host: str,
        port: int,
    ):
        self.host = host
        self.port = port

    # --------------------------------------------------
    # LOW LEVEL SHELL
    # --------------------------------------------------

    async def shell(
        self,
        command: str,
    ):
        """Execute one-off ADB command."""

        device = AdbDeviceTcpAsync(
            self.host,
            self.port,
        )

        try:
            await asyncio.wait_for(
                device.connect(
                    rsa_keys=[],
                    auth_timeout_s=3,
                ),
                timeout=5,
            )

            result = await asyncio.wait_for(
                device.shell(command),
                timeout=10,
            )

            return result

        finally:
            try:
                await device.close()

            except Exception:
                pass

    # --------------------------------------------------
    # LED CONTROL
    # --------------------------------------------------

    async def read_led_state(self):
        """Read LED state."""

        try:
            raw = await self.shell(
                "cat /sdcard/frameo_light.txt"
            )

            return raw.strip()

        except Exception:
            return "<0,0,0,0>"

    async def set_led_state(
        self,
        brightness: int,
        r: int,
        g: int,
        b: int,
    ):
        """Set LED state."""

        cmd = (
            f"echo '<{brightness},{r},{g},{b}>' "
            f"> /sdcard/frameo_light.txt"
        )

        await self.shell(cmd)

    # --------------------------------------------------
    # SCREEN CONTROL
    # --------------------------------------------------

    async def toggle_screen(self):
        """Toggle screen power."""

        await self.shell(
            "input keyevent 26"
        )

    async def get_screen_brightness(self):
        """Get Android brightness."""

        result = await self.shell(
            "settings get system "
            "screen_brightness"
        )

        try:
            return int(result.strip())

        except Exception:
            return 127

    async def set_screen_brightness(
        self,
        brightness: int,
    ):
        """Set Android brightness."""

        await self.shell(
            f"settings put system "
            f"screen_brightness {brightness}"
        )

    # --------------------------------------------------
    # FOREGROUND APP
    # --------------------------------------------------

    async def get_foreground_app(self):
        """Get foreground app."""

        result = await self.shell(
            "dumpsys window windows "
            "| grep mCurrentFocus"
        )

        try:
            line = result.strip()

            if "/" in line:
                activity = (
                    line.split("/")[0]
                    .split()[-1]
                )

                return activity

        except Exception:
            pass

        return "unknown"

    # --------------------------------------------------
    # APP CONTROL
    # --------------------------------------------------

    async def start_fully_kiosk(self):
        """Start Fully Kiosk."""

        await self.shell(
            "am start -n "
            "de.ozerov.fully/.MainActivity"
        )

    async def start_frameo(self):
        """Start Frameo."""

        await self.shell(
            "am start -n "
            "com.frameo.app/.MainActivity"
        )

    # --------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------

    async def create_screenshot(self):
        """Create screenshot."""

        await self.shell(
            "screencap -p "
            "/sdcard/frameo_screen.png"
        )
