import asyncio
import os
import tempfile
import logging

from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from adb_shell.auth.keygen import keygen

_LOGGER = logging.getLogger(__name__)


class FrameoADB:
    """ADB handler for Denver Frameo."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.device = None
        self.signer = None
        self._connected = False

    # --------------------------------------------------
    # KEY HANDLING
    # --------------------------------------------------

    def load_signer(self):
        """Load or generate ADB key."""

        key_path = "/config/.storage/adbkey"
        pub_path = f"{key_path}.pub"

        if not os.path.exists(key_path):
            _LOGGER.warning("ADB key not found, generating new key...")
            keygen(key_path)

        with open(key_path, "r") as f:
            priv = f.read()

        with open(pub_path, "r") as f:
            pub = f.read()

        return PythonRSASigner(pub, priv)

    # --------------------------------------------------
    # CONNECT
    # --------------------------------------------------

    async def connect(self):
        """Connect to device."""

        if self._connected and self.device:
            return

        self.signer = self.load_signer()
        self.device = AdbDeviceTcp(self.host, self.port)

        await self.device.connect(
            rsa_keys=[self.signer],
            auth_timeout_s=5,
        )

        self._connected = True

    async def ensure_connected(self):
        """Ensure active connection."""

        try:
            await self.connect()
        except Exception as err:
            _LOGGER.warning("ADB reconnect failed: %s", err)
            self._connected = False
            raise

    # --------------------------------------------------
    # SHELL
    # --------------------------------------------------

    async def shell(self, cmd: str):
        """Run shell command."""

        await self.ensure_connected()

        try:
            return await self.device.shell(cmd)
        except Exception as err:
            _LOGGER.warning("ADB shell failed: %s", err)
            self._connected = False
            raise

    # --------------------------------------------------
    # SCREEN STATE
    # --------------------------------------------------

    async def is_screen_on(self) -> bool:
        """Check if screen is on."""

        output = await self.shell("dumpsys power | grep mWakefulness")

        return "Awake" in output or "Awake" in str(output)

    # --------------------------------------------------
    # SCREENSHOT (IMPORTANT FIX)
    # --------------------------------------------------

    async def get_screenshot(self) -> bytes | None:
        """Take screenshot via screencap + pull."""

        await self.ensure_connected()

        remote_path = "/sdcard/frameo_screen.png"

        try:
            await self.device.shell(
                f"screencap -p {remote_path}"
            )

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                local_path = tmp.name

            await self.device.pull(
                remote_path,
                local_path,
            )

            with open(local_path, "rb") as f:
                data = f.read()

            os.remove(local_path)

            return data

        except Exception as err:
            _LOGGER.warning("Screenshot failed: %s", err)
            self._connected = False
            return None

    # --------------------------------------------------
    # SIMPLE COMMANDS
    # --------------------------------------------------

    async def read_led_state(self):
        return await self.shell("cat /sys/.../led")  # pas aan indien nodig

    async def get_screen_brightness(self):
        return await self.shell("settings get system screen_brightness")

    async def get_foreground_app(self):
        return await self.shell("dumpsys window | grep mCurrentFocus")

    # --------------------------------------------------
    # OPTIONAL
    # --------------------------------------------------

    async def toggle_screen(self):
        """Toggle screen via power key."""

        await self.shell("input keyevent 26")
