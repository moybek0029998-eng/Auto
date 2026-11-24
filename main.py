from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

# ============================================================
# SHU YERNI TO'LDIRING: magnitofon pultining kodlari (NEC)
# ADDR - umumiy manzil, CMD - har bir tugma kodi
# Hozir turgan qiymatlar NAMUNA, haqiqiy kodlar bilan almashtiring.
# ============================================================
ADDR = 0x00

CODES = {
    "PLAY/PAUSE": 0x01,
    "STOP": 0x02,
    "MUTE": 0x03,
    "ORQAGA": 0x04,
    "OLDINGA": 0x05,
    "0": 0x10,
    "1": 0x11,
    "2": 0x12,
    "3": 0x13,
    "4": 0x14,
    "5": 0x15,
    "6": 0x16,
    "7": 0x17,
    "8": 0x18,
    "9": 0x19,
    "10": 0x1A,
}

CARRIER = 38000


def nec_pattern(addr, cmd):
    data = addr | ((~addr & 0xFF) << 8) | (cmd << 16) | ((~cmd & 0xFF) << 24)
    p = [9000, 4500]
    for i in range(32):
        p += [560, 1690 if (data >> i) & 1 else 560]
    p.append(560)
    return p


class IR:
    def __init__(self):
        self.ok = False
        if platform == "android":
            try:
                from jnius import autoclass
                activity = autoclass("org.kivy.android.PythonActivity").mActivity
                Context = autoclass("android.content.Context")
                self.mgr = activity.getSystemService(Context.CONSUMER_IR_SERVICE)
                self.ok = bool(self.mgr and self.mgr.hasIrEmitter())
            except Exception:
                self.ok = False

    def send(self, name):
        if not self.ok:
            return False
        try:
            self.mgr.transmit(CARRIER, nec_pattern(ADDR, CODES[name]))
            return True
        except Exception:
            return False


class PultApp(App):
    def build(self):
        self.ir = IR()
        root = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.status = Label(
            text="IR tayyor" if self.ir.ok else "IR port topilmadi",
            size_hint_y=0.08,
        )
        root.add_widget(self.status)

        top = GridLayout(cols=2, spacing=10, size_hint_y=0.3)
        for n in ["PLAY/PAUSE", "STOP", "ORQAGA", "OLDINGA", "MUTE"]:
            top.add_widget(self.btn(n))
        root.add_widget(top)

        nums = GridLayout(cols=3, spacing=10)
        for n in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "10"]:
            nums.add_widget(self.btn(n))
        root.add_widget(nums)
        return root

    def btn(self, name):
        b = Button(text=name, font_size="22sp")
        b.bind(on_release=lambda _b, n=name: self.press(n))
        return b

    def press(self, name):
        sent = self.ir.send(name)
        self.status.text = ("Yuborildi: " if sent else "Xato: ") + name


if __name__ == "__main__":
    PultApp().run()
