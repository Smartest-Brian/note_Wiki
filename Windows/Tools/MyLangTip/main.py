import sys
import ctypes
import win32gui
import win32process
from PyQt6.QtWidgets import QApplication, QLabel, QMenu
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QCursor

# Windows Constants
IME_CMODE_NATIVE = 0x0001
WM_IME_CONTROL = 0x0283
IMC_GETCONVERSIONMODE = 0x0001
VK_CAPITAL = 0x14

class GUITHREADINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("hwndActive", ctypes.c_void_p),
        ("hwndFocus", ctypes.c_void_p),
        ("hwndCapture", ctypes.c_void_p),
        ("hwndMenuOwner", ctypes.c_void_p),
        ("hwndMoveSize", ctypes.c_void_p),
        ("hwndCaret", ctypes.c_void_p), # Key for Electron apps like Teams
        ("rcCaret", ctypes.c_int * 4)
    ]

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(f"DPI Awareness initialization failed: {e}")

class LanguageIndicator(QLabel):
    def __init__(self):
        super().__init__("英 a")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Base Style: Using 'gray' for text as requested
        # Added a stronger white border (2px) to ensure visibility on black backgrounds
        self.base_style = """
            background-color: rgba(45, 45, 45, 210); 
            color: gray; 
            font-size: 18px; 
            font-family: "Microsoft JhengHei";
            font-weight: bold;
            padding: 3px 10px; 
            border-radius: 8px;
            border: 2px solid rgba(255, 255, 255, 200);
        """
        self.setStyleSheet(self.base_style)
        self.adjustSize()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(50) 
        print("Language Indicator active. Monitoring IME status.")

    def _find_child_hwnd_by_class(self, parent_hwnd, class_name_fragment):
        """Enumerate child windows to find one matching a class name fragment.
        Used to locate Chrome_RenderWidgetHostHWND in Electron apps like Teams.
        """
        result = []
        try:
            def callback(hwnd, _):
                try:
                    cn = win32gui.GetClassName(hwnd)
                    if class_name_fragment in cn:
                        result.append(hwnd)
                except Exception:
                    pass
                return True
            win32gui.EnumChildWindows(parent_hwnd, callback, None)
        except Exception:
            pass
        return result[0] if result else None

    def _get_conversion_mode(self, hwnd):
        """Try to read IME conversion mode from a given HWND.
        
        Method A: ImmGetContext + ImmGetConversionStatus (most direct, works for
                  standard Win32 and Chromium renderer windows)
        Method B: ImmGetDefaultIMEWnd + WM_IME_CONTROL (classic fallback)
        
        Returns the conversion mode integer, or None if unavailable.
        """
        # Method A: ImmGetContext (direct IME context query)
        himc = ctypes.windll.imm32.ImmGetContext(hwnd)
        if himc:
            conversion = ctypes.c_ulong(0)
            sentence   = ctypes.c_ulong(0)
            ok = ctypes.windll.imm32.ImmGetConversionStatus(
                himc, ctypes.byref(conversion), ctypes.byref(sentence)
            )
            ctypes.windll.imm32.ImmReleaseContext(hwnd, himc)
            if ok:
                return conversion.value

        # Method B: IME window message (classic approach)
        h_ime = ctypes.windll.imm32.ImmGetDefaultIMEWnd(hwnd)
        if h_ime:
            res = ctypes.windll.user32.SendMessageW(
                h_ime, WM_IME_CONTROL, IMC_GETCONVERSIONMODE, 0
            )
            if res is not None:
                return res

        return None

    def get_ime_status(self):
        """Multi-candidate IME detection supporting standard and Electron/Chromium apps.

        Candidate priority:
          1. hwndFocus from GUI thread info (standard apps)
          2. hwndCaret from GUI thread info (some Electron apps)
          3. Chrome_RenderWidgetHostHWND child window (Teams / Electron renderer)
          4. Foreground window itself (last resort)
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return "英"

            candidates = []

            # --- Candidate 1 & 2: focused / caret window from GUI thread ---
            gui_info = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
            _, thread_id = win32process.GetWindowThreadProcessId(hwnd)
            if ctypes.windll.user32.GetGUIThreadInfo(thread_id, ctypes.byref(gui_info)):
                if gui_info.hwndFocus:
                    candidates.append(gui_info.hwndFocus)
                if gui_info.hwndCaret and gui_info.hwndCaret != gui_info.hwndFocus:
                    candidates.append(gui_info.hwndCaret)

            # --- Candidate 3: Chromium renderer (Electron apps like Teams) ---
            chrome_hwnd = self._find_child_hwnd_by_class(hwnd, 'Chrome_RenderWidgetHostHWND')
            if chrome_hwnd and chrome_hwnd not in candidates:
                candidates.append(chrome_hwnd)

            # --- Candidate 4: foreground window itself ---
            if hwnd not in candidates:
                candidates.append(hwnd)

            # Try each candidate in order
            for target in candidates:
                mode = self._get_conversion_mode(target)
                if mode is not None:
                    return "中" if (mode & IME_CMODE_NATIVE) else "英"

            return "英"
        except Exception as e:
            print(f"IME monitoring error: {e}")
            return "英"

    def get_caps_lock_status(self):
        """Detect Caps Lock state using GetKeyState."""
        try:
            # GetKeyState returns the toggle state in the low-order bit
            state = ctypes.windll.user32.GetKeyState(VK_CAPITAL)
            return (state & 0x0001) != 0
        except Exception as e:
            print(f"Caps Lock detection error: {e}")
            return False

    def update_status(self):
        """Refresh status and track mouse position."""
        ime_status = self.get_ime_status()
        caps_on = self.get_caps_lock_status()
        caps_text = "A" if caps_on else "a"
        display_text = f"{ime_status} {caps_text}"
        
        if self.text() != display_text:
            self.setText(display_text)
            self.adjustSize()
            # Visual feedback: subtle background shift while keeping 'gray' text
            if ime_status == "中":
                # Light blue-ish background for Chinese mode
                self.setStyleSheet(self.base_style.replace("rgba(45, 45, 45, 210)", "rgba(50, 100, 150, 220)"))
            else:
                # Original dark background for English mode
                self.setStyleSheet(self.base_style)
        
        try:
            pos = QCursor.pos()
            self.move(pos.x() + 25, pos.y() + 25)
            if not self.isVisible():
                self.show()
        except Exception as e:
            print(f"Positioning error: {e}")

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: white; color: black; }")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        menu.exec(event.globalPos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    indicator = LanguageIndicator()
    sys.exit(app.exec())
