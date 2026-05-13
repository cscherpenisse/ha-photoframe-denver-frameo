import asyncio

from adb_shell.adb_device_async import (
    AdbDeviceTcpAsync,
)
from adb_shell.exceptions import (
    AdbConnectionError,
)


class FrameoADB:
    def __init__(
        self,
        host: str,
        port: int,
    ):
        self.host = host
        self.port = port

        self.device = AdbDeviceTcpAsync(
            host,
            port,
        )

        self.connected = False

    # --------------------------------------------------
    # CONNECTION MANAGEMENT
    # --------------------------------------------------

    async def connect(self):
        """Connect to ADB."""

        try:
            await self.device.connect(
                rsa_keys=[],
                auth_timeout_s=3,
            )

            self.connected = True

        except asyncio.CancelledError:
            raise

        except Exception:
            self.connected = False
            raise

    async def ensure_connected(self):
        """Ensure ADB connection."""

        if self.connected:
            return

        for _ in range(3):
            try:
                await self.connect()
                return

            except asyncio.CancelledError:
                raise

            except Exception:
                await asyncio.sleep(1)

        self.connected = False

        raise AdbConnectionError(
            "Unable to connect to Frameo"
        )

    async def reconnect(self):
        """Reconnect completely."""

        self.connected = False

        self.device = AdbDeviceTcpAsync(
            self.host,
            self.port,
        )

        await self.ensure_connected()

    # --------------------------------------------------
    # SHELL COMMANDS
    # --------------------------------------------------

    async def shell(
        self,
        command: str,
    ):
        """Execute shell command safely."""

        try:
            await self.ensure_connected()

            return await self.device.shell(
                command
            )

        except asyncio.CancelledError:
            raise

        except Exception:
            # Connection probably died:
            # - reboot
            # - adb restart
            # - wifi reconnect
            # - socket reset

            await self.reconnect()

            return await self.device.shell(
                command
            )

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

        except asyncio.CancelledError:
            raise

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
        """Toggle display power."""

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
        """Get active foreground app."""

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
    # APP LAUNCHING
    # --------------------------------------------------

    async def start_fully_kiosk(self):
        """Launch Fully Kiosk."""

        await self.shell(
            "am start -n "
            "de.ozerov.fully/.MainActivity"
        )

    async def start_frameo(self):
        """Launch Frameo."""

        await self.shell(
            "am start -n "
            "com.frameo.app/.MainActivity"
        )

    # --------------------------------------------------
    # SCREENSHOTS
    # --------------------------------------------------

    async def create_screenshot(self):
        """Create screenshot on device."""

        await self.shell(
            "screencap -p "
            "/sdcard/frameo_screen.png"
        )
