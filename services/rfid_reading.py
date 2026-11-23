
import ctypes
import threading
import queue
from ctypes import wintypes


# Windows message identifiers.
WM_INPUT = 0x00FF
WM_QUIT = 0x0012

# Raw Input data and device information constants.
RID_INPUT = 0x10000003
RIDI_DEVICENAME = 0x20000007

# Raw Input registration flags.
RIDEV_INPUTSINK = 0x00000100
RIDEV_REMOVE = 0x00000001

# Keyboard event flag indicating a key release.
RI_KEY_BREAK = 0x0001

# Virtual key code for the Enter key.
VK_RETURN = 0x0D

# Vendor and product identifiers of the RFID reader.
DEVICE_VID = "VID_1A86"
DEVICE_PID = "PID_2366"


# Windows API structures.

class RAWINPUTDEVICE(ctypes.Structure):
    """Describe a device registered for raw input."""

    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND)
    ]


class RAWINPUTHEADER(ctypes.Structure):
    """Store metadata about a raw input event."""

    _fields_ = [
        ("dwType", wintypes.DWORD),
        ("dwSize", wintypes.DWORD),
        ("hDevice", wintypes.HANDLE),
        ("wParam", wintypes.WPARAM)
    ]


class RAWKEYBOARD(ctypes.Structure):
    """Represent raw keyboard input data."""

    _fields_ = [
        ("MakeCode", wintypes.USHORT),
        ("Flags", wintypes.USHORT),
        ("Reserved", wintypes.USHORT),
        ("VKey", wintypes.USHORT),
        ("Message", wintypes.UINT),
        ("ExtraInformation", wintypes.ULONG)
    ]


class RAWINPUTUNION(ctypes.Union):
    """Store the data associated with a raw input event."""

    _fields_ = [
        ("keyboard", RAWKEYBOARD),
        ("padding", ctypes.c_byte * 32)
    ]


class RAWINPUT(ctypes.Structure):
    """Represent a complete raw input event."""

    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("data", RAWINPUTUNION)
    ]


class WNDCLASS(ctypes.Structure):
    """Define the properties of a Windows window class."""

    pass


# Define the callback type used by the Windows window procedure.
WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM
)

WNDCLASS._fields_ = [
    ("style", wintypes.UINT),
    ("lpfnWndProc", WNDPROC),
    ("cbClsExtra", ctypes.c_int),
    ("cbWndExtra", ctypes.c_int),
    ("hInstance", wintypes.HINSTANCE),
    ("hIcon", wintypes.HANDLE),
    ("hCursor", wintypes.HANDLE),
    ("hbrBackground", wintypes.HANDLE),
    ("lpszMenuName", wintypes.LPCWSTR),
    ("lpszClassName", wintypes.LPCWSTR)
]


class MSG(ctypes.Structure):
    """Represent a Windows message."""

    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
        ("lPrivate", wintypes.DWORD)
    ]


class RFIDReading:
    """Read RFID card UIDs using the Windows Raw Input API."""

    def __init__(self) -> None:
        """Initialize the RFID reader and Windows API libraries."""
        self.cards = queue.Queue()
        self.buffer = ""

        self.thread = None
        self.thread_id = None
        self.hwnd = None

        self.running = False
        self.ready = threading.Event()

        self.device_cache = {}
        self.error = None

        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

        self._configure_api()

    def _configure_api(self) -> None:
        """Configure argument and return types for Windows API functions."""

        self.user32.RegisterRawInputDevices.argtypes = [
            ctypes.POINTER(RAWINPUTDEVICE),
            wintypes.UINT,
            wintypes.UINT
        ]
        self.user32.RegisterRawInputDevices.restype = wintypes.BOOL

        self.user32.GetRawInputData.argtypes = [
            wintypes.HANDLE,
            wintypes.UINT,
            ctypes.c_void_p,
            ctypes.POINTER(wintypes.UINT),
            wintypes.UINT
        ]
        self.user32.GetRawInputData.restype = wintypes.UINT

        self.user32.GetRawInputDeviceInfoW.argtypes = [
            wintypes.HANDLE,
            wintypes.UINT,
            ctypes.c_void_p,
            ctypes.POINTER(wintypes.UINT)
        ]
        self.user32.GetRawInputDeviceInfoW.restype = wintypes.UINT

        self.kernel32.GetModuleHandleW.argtypes = [
            wintypes.LPCWSTR
        ]
        self.kernel32.GetModuleHandleW.restype = wintypes.HMODULE

        self.user32.CreateWindowExW.argtypes = [
            wintypes.DWORD,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HWND,
            wintypes.HMENU,
            wintypes.HINSTANCE,
            ctypes.c_void_p
        ]
        self.user32.CreateWindowExW.restype = wintypes.HWND

        self.user32.RegisterClassW.argtypes = [
            ctypes.POINTER(WNDCLASS)
        ]
        self.user32.RegisterClassW.restype = wintypes.ATOM

        self.user32.GetMessageW.argtypes = [
            ctypes.POINTER(MSG),
            wintypes.HWND,
            wintypes.UINT,
            wintypes.UINT
        ]
        self.user32.GetMessageW.restype = ctypes.c_int

        self.user32.TranslateMessage.argtypes = [
            ctypes.POINTER(MSG)
        ]
        self.user32.TranslateMessage.restype = wintypes.BOOL

        self.user32.DispatchMessageW.argtypes = [
            ctypes.POINTER(MSG)
        ]
        self.user32.DispatchMessageW.restype = wintypes.LPARAM

        self.user32.DefWindowProcW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            ctypes.c_size_t,
            ctypes.c_ssize_t
        ]
        self.user32.DefWindowProcW.restype = ctypes.c_ssize_t

        self.kernel32.GetCurrentThreadId.restype = wintypes.DWORD

        self.user32.PostThreadMessageW.argtypes = [
            wintypes.DWORD,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM
        ]
        self.user32.PostThreadMessageW.restype = wintypes.BOOL

        self.user32.DestroyWindow.argtypes = [
            wintypes.HWND
        ]
        self.user32.DestroyWindow.restype = wintypes.BOOL

        self.user32.UnregisterClassW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.HINSTANCE
        ]
        self.user32.UnregisterClassW.restype = wintypes.BOOL

    def start(self) -> None:
        """Start the RFID reader in a separate thread.

        Raises:
            RuntimeError: If the reader fails to initialize or times out.
        """
        if self.thread and self.thread.is_alive():
            return

        self.running = True
        self.ready.clear()
        self.error = None

        # Clear previously collected data before restarting.
        self.buffer = ""
        self.device_cache.clear()

        while not self.cards.empty():
            self.cards.get_nowait()

        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        self.thread.start()

        if not self.ready.wait(timeout=5):
            self.running = False

            if self.thread_id:
                self.user32.PostThreadMessageW(
                    self.thread_id,
                    WM_QUIT,
                    0,
                    0
                )

            self.thread.join(timeout=3)
            raise RuntimeError("CardReader initialization timed out")

        if self.error:
            self.thread.join(timeout=3)
            raise RuntimeError(
                "CardReader initialization failed"
            ) from self.error

    def stop(self) -> None:
        """Stop the RFID reader and release its Windows resources.

        Raises:
            RuntimeError: If the reader thread does not stop in time.
        """
        self.running = False

        if self.thread and self.thread.is_alive():

            if self.thread_id:
                self.user32.PostThreadMessageW(
                    self.thread_id,
                    WM_QUIT,
                    0,
                    0
                )

            self.thread.join(timeout=3)

            if self.thread.is_alive():
                raise RuntimeError("CardReader failed to stop")

        self.thread = None
        self.thread_id = None
        self.hwnd = None

    def get_card(self, timeout: float | None = None) -> str | None:
        """Retrieve a scanned card UID from the queue.

        Args:
            timeout: Maximum time to wait for a card, in seconds.
                None means wait indefinitely.

        Returns:
            str | None: The card UID, or None if no card is available
            before the timeout expires.
        """
        try:
            return self.cards.get(timeout=timeout)
        except queue.Empty:
            return None

    def _run(self) -> None:
        """Create a hidden window and process Windows raw input messages.

        This method runs in a separate thread. It registers the keyboard
        input device, processes incoming messages, and releases resources
        when the reader stops.
        """
        instance = None
        class_name = f"TimeTagCardReader_{id(self)}"

        class_registered = False
        input_registered = False

        try:
            self.thread_id = self.kernel32.GetCurrentThreadId()
            instance = self.kernel32.GetModuleHandleW(None)

            # Create the Windows message handler callback.
            self._wndproc = WNDPROC(self._window_proc)

            wc = WNDCLASS()
            wc.lpfnWndProc = self._wndproc
            wc.hInstance = instance
            wc.lpszClassName = class_name

            atom = self.user32.RegisterClassW(ctypes.byref(wc))

            if not atom:
                raise ctypes.WinError(ctypes.get_last_error())

            class_registered = True

            # Create a hidden window to receive raw input messages.
            self.hwnd = self.user32.CreateWindowExW(
                0,
                class_name,
                "TimeTag Card Reader",
                0,
                0, 0, 0, 0,
                None,
                None,
                instance,
                None
            )

            if not self.hwnd:
                raise ctypes.WinError(ctypes.get_last_error())

            # Register keyboard input for the hidden window.
            device = RAWINPUTDEVICE(
                0x01,
                0x06,
                RIDEV_INPUTSINK,
                self.hwnd
            )

            result = self.user32.RegisterRawInputDevices(
                ctypes.byref(device),
                1,
                ctypes.sizeof(RAWINPUTDEVICE)
            )

            if not result:
                raise ctypes.WinError(ctypes.get_last_error())

            input_registered = True

            self.ready.set()

            msg = MSG()

            # Process Windows messages while the reader is running.
            while self.running:
                result = self.user32.GetMessageW(
                    ctypes.byref(msg),
                    None,
                    0,
                    0
                )

                if result <= 0:
                    break

                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))

        except Exception as error:
            self.error = error
            self.ready.set()

        finally:
            # Unregister the raw input device.
            if input_registered:
                device = RAWINPUTDEVICE(
                    0x01,
                    0x06,
                    RIDEV_REMOVE,
                    None
                )

                self.user32.RegisterRawInputDevices(
                    ctypes.byref(device),
                    1,
                    ctypes.sizeof(RAWINPUTDEVICE)
                )

            # Destroy the hidden window.
            if self.hwnd:
                self.user32.DestroyWindow(self.hwnd)

            # Unregister the Windows window class.
            if class_registered:
                self.user32.UnregisterClassW(
                    class_name,
                    instance
                )

            self.hwnd = None
            self.thread_id = None
            self.running = False

    def _window_proc(
        self,
        hwnd: int,
        message: int,
        wparam: int,
        lparam: int
    ) -> int:
        """Handle messages received by the hidden Windows window.

        Args:
            hwnd: Handle to the window receiving the message.
            message: Windows message identifier.
            wparam: Additional message information.
            lparam: Additional message information.

        Returns:
            int: Result returned by the Windows default window procedure.
        """
        if message == WM_INPUT:
            self._process_input(lparam)

        return self.user32.DefWindowProcW(
            hwnd,
            message,
            wparam,
            lparam
        )

    def _is_card_reader(self, device_handle: int) -> bool:
        """Check whether an input device is the configured RFID reader.

        Args:
            device_handle: Handle identifying the input device.

        Returns:
            bool: True if the device VID and PID match the RFID reader.
        """
        if device_handle in self.device_cache:
            return self.device_cache[device_handle]

        size = wintypes.UINT(0)

        self.user32.GetRawInputDeviceInfoW(
            device_handle,
            RIDI_DEVICENAME,
            None,
            ctypes.byref(size)
        )

        if not size.value:
            return False

        device_name = ctypes.create_unicode_buffer(size.value)

        result = self.user32.GetRawInputDeviceInfoW(
            device_handle,
            RIDI_DEVICENAME,
            device_name,
            ctypes.byref(size)
        )

        if result == 0xFFFFFFFF:
            return False

        name = device_name.value.upper()

        is_reader = (
            DEVICE_VID in name and
            DEVICE_PID in name
        )

        self.device_cache[device_handle] = is_reader

        return is_reader

    def _process_input(self, raw_handle: int) -> None:
        """Process raw keyboard input received from the RFID reader.

        The method filters input events by device, ignores key releases,
        collects hexadecimal UID characters, and adds the completed UID
        to the card queue when Enter is received.

        Args:
            raw_handle: Handle to the raw input data.
        """
        size = wintypes.UINT(0)

        header_size = ctypes.sizeof(RAWINPUTHEADER)

        result = self.user32.GetRawInputData(
            raw_handle,
            RID_INPUT,
            None,
            ctypes.byref(size),
            header_size
        )

        if result == 0xFFFFFFFF or not size.value:
            return

        buffer = ctypes.create_string_buffer(size.value)

        result = self.user32.GetRawInputData(
            raw_handle,
            RID_INPUT,
            buffer,
            ctypes.byref(size),
            header_size
        )

        if result == 0xFFFFFFFF:
            return

        raw = ctypes.cast(
            buffer,
            ctypes.POINTER(RAWINPUT)
        ).contents

        if raw.header.dwType != 1:
            return

        if not self._is_card_reader(raw.header.hDevice):
            return

        keyboard = raw.data.keyboard

        # Ignore key release events.
        if keyboard.Flags & RI_KEY_BREAK:
            return

        key = keyboard.VKey

        # Check whether Enter marks the end of the card UID.
        if key == VK_RETURN:

            if self.buffer:
                self.cards.put(self.buffer)
                self.buffer = ""

            return

        # Collect numeric characters from the main keyboard row.
        if 0x30 <= key <= 0x39:
            self.buffer += chr(key)
            return

        # Collect hexadecimal letters from A to F.
        if 0x41 <= key <= 0x46:
            self.buffer += chr(key)
            return

        # Collect numeric characters from the numeric keypad.
        if 0x60 <= key <= 0x69:
            self.buffer += chr(key - 0x30)
            return
