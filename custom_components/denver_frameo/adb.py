import asyncio
import logging
import os
import tempfile

from adb_shell.adb_device_async import (
    AdbDeviceTcpAsync,
)

_LOGGER = logging.getLogger(__name__)


class FrameoADB:
    def __init__(
        self,
        host: str,
        port: int,
    ):
        self.host = host
        self.port = port

        self.lock = asyncio.Lock()

        self._connected = False

    # --------------------------------------------------
    # CONNECTION
    # --------------------------------------------------

    async def ensure_connected(self):
        """Compatibility helper."""

        return True

    # --------------------------------------------------
    # LOW LEVEL SHELL
    # --------------------------------------------------

    async def shell(
        self,
        command: str,
    ):
        """Execute ADB shell command."""

        async with self.lock:

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

                self._connected = True

                result = await asyncio.wait_for(
                    device.shell(command),
                    timeout=15,
                )

                return result

            except Exception as err:
                self._connected = False

                raise Exception(
                    f"ADB command failed: {err}"
                )

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
    # SCREEN STATUS
    # --------------------------------------------------

    async def is_screen_on(self) -> bool:
        """Check if display is ON."""

        try:
            output = await self.shell(
                "dumpsys power | grep 'Display Power'"
            )

            output = str(output).strip()

            _LOGGER.warning(
                "DISPLAY POWER: %s",
                output,
            )

            return "state=ON" in output

        except Exception as err:
            _LOGGER.warning(
                "Display state check failed: %s",
                err,
            )

            return False

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
            "settings get system screen_brightness"
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
            f"settings put system screen_brightness {brightness}"
        )

    # --------------------------------------------------
    # FOREGROUND APP
    # --------------------------------------------------

    async def get_foreground_app(self):
        """Get foreground app."""

        try:
            result = await self.shell(
                "dumpsys window windows | grep mCurrentFocus"
            )

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
            "net.frameo.frame/.MainActivity"
        )

    # --------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------

    async def create_screenshot(self):
        """Create screenshot on device."""

        await self.shell(
            "screencap -p "
            "/sdcard/frameo_screen.png"
        )

    async def read_screenshot(self):
        """Read screenshot file safely."""

        async with self.lock:

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

                temp_file = tempfile.NamedTemporaryFile(
                    suffix=".png",
                    delete=False,
                )

                temp_path = temp_file.name

                temp_file.close()

                await device.pull(
                    "/sdcard/frameo_screen.png",
                    temp_path,
                )

                with open(temp_path, "rb") as file:
                    data = file.read()

                os.remove(temp_path)

                return data

            except Exception as err:
                _LOGGER.warning(
                    "Screenshot read failed: %s",
                    err,
                )

                return None

            finally:
                try:
                    await device.close()

                except Exception:
                    pass
