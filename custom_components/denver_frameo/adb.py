import os
import asyncio
import logging
import tempfile
from pathlib import Path
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.adb_device_async import AdbDeviceAsync
from adb_shell.transport.tcp_transport_async import TcpTransportAsync

from adb_shell.auth.sign_pythonrsa import PythonRSASigner

LOGGER = logging.getLogger(__name__)


class FrameoADB:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.transport = TcpTransportAsync(
            host,
            port,
        )

        self.device = AdbDeviceAsync(
            self.transport
        )

        self.signer = None

        self.connected = False
        
    # --------------------------------------------------
    # CREATE ADB KEY
    # --------------------------------------------------

    def load_signer(self):
        """Load or create ADB key."""

        key_path = "/config/.storage/adbkey"

        pub_path = f"{key_path}.pub"

        # ---------------------------------
        # CREATE KEY IF MISSING
        # ---------------------------------

        if not os.path.exists(key_path):

            from adb_shell.auth.keygen import keygen

            keygen(key_path)

        with open(key_path) as private_key:
            priv = private_key.read()

        with open(pub_path) as public_key:
            pub = public_key.read()

        return PythonRSASigner(pub, priv)
    
    # --------------------------------------------------
    # CONNECT
    # --------------------------------------------------

    async def connect(self):
        """Connect to device."""

        if self._connected:
            return

        self.signer = self.load_signer()

        await self.device.connect(
            rsa_keys=[self.signer],
            auth_timeout_s=5,
        )

        self._connected = True

    async def disconnect(self):
        """Disconnect."""

        try:
            await self.device.close()
        except Exception:
            pass

        self.connected = False

    async def ensure_connected(self):
        """Reconnect automatically."""

        try:
            if not self.connected:
                await self.connect()
                return

            await asyncio.wait_for(
                self.device.shell("echo ok"),
                timeout=5,
            )

        except Exception:
            LOGGER.debug(
                "ADB reconnect triggered"
            )

            self.connected = False

            try:
                await self.disconnect()
            except Exception:
                pass

            await self.connect()

    # --------------------------------------------------
    # SHELL
    # --------------------------------------------------

    async def shell(self, command):
        """Run adb shell command."""

        await self.ensure_connected()

        try:
            return await asyncio.wait_for(
                self.device.shell(command),
                timeout=10,
            )

        except Exception:
            self.connected = False
            raise

    # --------------------------------------------------
    # SCREEN STATE
    # --------------------------------------------------

    async def is_screen_on(self):
        """Check if display is ON."""

        result = await self.shell(
            "dumpsys power"
        )

        result = result.lower()

        return (
            "display power: state=on" in result
        )

    # --------------------------------------------------
    # SCREENSHOT
    # --------------------------------------------------

    async def create_screenshot(self):
        """Create screenshot on device."""

        await self.shell(
            "screencap -p /sdcard/frameo_screen.png"
        )

    async def read_screenshot(self):
        """Read screenshot binary."""

        await self.ensure_connected()

        temp_file = (
            Path(tempfile.gettempdir())
            / "frameo_screen.png"
        )

        loop = asyncio.get_running_loop()

        await loop.run_in_executor(
            None,
            lambda: self.device.pull(
                "/sdcard/frameo_screen.png",
                str(temp_file),
            ),
        )

        if not temp_file.exists():
            return None

        return temp_file.read_bytes()

    # --------------------------------------------------
    # BRIGHTNESS
    # --------------------------------------------------

    async def get_screen_brightness(self):
        """Get brightness."""

        result = await self.shell(
            "settings get system screen_brightness"
        )

        return int(result.strip())

    async def set_screen_brightness(self, value):
        """Set brightness."""

        await self.shell(
            f"settings put system screen_brightness {value}"
        )

    # --------------------------------------------------
    # FOREGROUND APP
    # --------------------------------------------------

    async def get_foreground_app(self):
        """Get foreground app."""

        result = await self.shell(
            "dumpsys window windows | grep mCurrentFocus"
        )

        return result.strip()

    # --------------------------------------------------
    # POWER
    # --------------------------------------------------

    async def toggle_screen(self):
        """Toggle screen power."""

        await self.shell(
            "input keyevent 26"
        )

    # --------------------------------------------------
    # LED
    # --------------------------------------------------

    async def read_led_state(self):
        return await self.shell(
            "cat /sdcard/frameo_light.txt"
        )

    async def set_led_state(
        self,
        brightness,
        r,
        g,
        b,
    ):
        await self.shell(
            f'echo "<{brightness},{r},{g},{b}>" > /sdcard/frameo_light.txt'
        )
