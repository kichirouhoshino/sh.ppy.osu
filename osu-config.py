#!/usr/bin/env python3
"""
osu! Pre-Launch Configuration GUI
Adjusts env-var mods and framework.ini settings before launching osu!
Built with PyGObject + GTK 3.
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

import configparser
import os
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
OSU_DATA_DEFAULT = os.path.expanduser("~/.var/app/sh.ppy.osu/data/osu")
CONFIG_DIR = os.path.expanduser("~/.var/app/sh.ppy.osu/config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "osu-launch-config.ini")

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULTS = {
    "strangle_fps": "0",
    "force_unlimited_framerate": "true",
    "pipewire_latency": "64",
    "force_pipewire_output": "true",
    "pulse_latency_msec": "1",
    "bass_dev_period": "2",
    "force_vulkan": "true",
    "force_wayland": "true",
    "enable_lfx": "true",
}


def get_osu_data_path():
    """Return the osu data folder, respecting storage.ini redirects."""
    storage_ini = os.path.join(OSU_DATA_DEFAULT, "storage.ini")
    if os.path.isfile(storage_ini):
        parser = configparser.RawConfigParser()
        with open(storage_ini, "r") as f:
            content = "[root]\n" + f.read()
        parser.read_string(content)
        if parser.has_option("root", "FullPath"):
            external = parser.get("root", "FullPath").strip()
            if os.path.isdir(external):
                return external
    return OSU_DATA_DEFAULT


def get_framework_ini_path():
    return os.path.join(get_osu_data_path(), "framework.ini")


def load_config():
    cfg = configparser.ConfigParser()
    cfg["launch"] = dict(DEFAULTS)
    if os.path.isfile(CONFIG_FILE):
        cfg.read(CONFIG_FILE)
    return cfg


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        cfg.write(f)


def _read_framework_ini(path):
    """Return an ordered dict of existing key=value pairs from framework.ini."""
    cfg = configparser.RawConfigParser()
    cfg.optionxform = str  # preserve case
    if os.path.isfile(path):
        with open(path, "r") as f:
            cfg.read_string("[root]\n" + f.read())
    else:
        cfg.read_string("[root]\n")
    if not cfg.has_section("root"):
        cfg.add_section("root")
    return cfg


def _write_framework_ini(path, cfg):
    """Write cfg back to framework.ini without a section header."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = [f"{k} = {v}" for k, v in cfg.items("root")]
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def set_framework_ini_value(key, value):
    """Set a single key=value pair in framework.ini."""
    path = get_framework_ini_path()
    cfg = _read_framework_ini(path)
    cfg.set("root", key, value)
    _write_framework_ini(path, cfg)


def init_framework_ini(values: dict):
    """Create framework.ini (and its parent osu folder) from scratch with the
    given key/value pairs. Called on first launch when the file doesn't exist."""
    path = get_framework_ini_path()
    cfg = _read_framework_ini(path)  # starts empty if file missing
    for key, value in values.items():
        cfg.set("root", key, value)
    _write_framework_ini(path, cfg)


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = """
* {
    font-family: "Cantarell", "DejaVu Sans", sans-serif;
}

window {
    background-color: #1a1a2e;
}

.header-box {
    background: linear-gradient(135deg, #e91e8c 0%, #9b27af 100%);
    padding: 20px 28px 16px 28px;
}

.header-title {
    font-size: 20px;
    font-weight: 800;
    color: #ffffff;
}

.header-subtitle {
    font-size: 11px;
    color: rgba(255,255,255,0.75);
}

.settings-box {
    background-color: #1a1a2e;
    padding: 16px 24px 8px 24px;
}

.section-label {
    font-size: 9px;
    font-weight: 700;
    color: #e91e8c;
    letter-spacing: 2px;
}

.setting-row {
    background-color: #16213e;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 5px;
}

.setting-name {
    font-size: 13px;
    font-weight: 600;
    color: #e8e8f0;
}

.setting-hint {
    font-size: 10px;
    color: #8888aa;
}

spinbutton {
    background-color: #0f3460;
    color: #ffffff;
}

.footer-box {
    background-color: #0f0f23;
    padding: 14px 24px;
    border-top: 1px solid rgba(233,30,140,0.3);
}

.btn-launch {
    background: linear-gradient(135deg, #e91e8c 0%, #9b27af 100%);
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    border-radius: 8px;
    padding: 6px 28px;
    border: none;
}

.btn-cancel {
    color: #8888aa;
    font-size: 13px;
    border-radius: 8px;
    padding: 6px 18px;
    background-color: transparent;
    border: 1px solid rgba(136,136,170,0.4);
}
"""


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class OsuConfigWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="osu! Launch Settings")
        self.set_default_size(520, 640)
        self.set_resizable(False)
        self.connect("delete-event", self._on_delete)
        self._result = 1  # default: cancelled

        # Apply CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS.encode())
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.cfg = load_config()
        s = self.cfg["launch"]

        # ---- Root layout ----
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(root)

        # ---- Header ----
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        header.get_style_context().add_class("header-box")
        header.set_border_width(0)

        title = Gtk.Label(label="osu! Launch Settings")
        title.get_style_context().add_class("header-title")
        title.set_halign(Gtk.Align.START)
        header.pack_start(title, False, False, 0)

        subtitle = Gtk.Label(label="Configure performance and audio settings before launching")
        subtitle.get_style_context().add_class("header-subtitle")
        subtitle.set_halign(Gtk.Align.START)
        header.pack_start(subtitle, False, False, 0)
        root.pack_start(header, False, False, 0)

        # ---- Scrollable settings area ----
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        settings_box.get_style_context().add_class("settings-box")
        scroll.add(settings_box)
        root.pack_start(scroll, True, True, 0)

        # ---- Section: Framerate ----
        self._section(settings_box, "FRAMERATE")
        self.w_fps = self._spin_row(
            settings_box, "Framerate Cap",
            "Cap for the game framerate. 0 = disabled. For VRR monitors, set to (refresh rate − 1).",
            value=int(s.get("strangle_fps", 0)), min_val=0, max_val=9999,
        )
        self.w_unlimited = self._toggle_row(
            settings_box, "Force Unlimited Framerate In-Game",
            "Sets FrameSync=Unlimited in framework.ini. Recommended when using the framerate cap.",
            active=s.getboolean("force_unlimited_framerate", fallback=False),
        )

        # ---- Section: Audio ----
        self._section(settings_box, "AUDIO")
        self.w_pw_lat = self._spin_row(
            settings_box, "PipeWire Latency (quant)",
            "Latency quant on the PipeWire side (default 64). Increase to 128+ for audio issues. Requires PipeWire Sound Server output.",
            value=int(s.get("pipewire_latency", 64)), min_val=16, max_val=8192,
        )
        self.w_force_pw = self._toggle_row(
            settings_box, "Force PipeWire Output",
            "Sets AudioDevice=PipeWire Sound Server in framework.ini. Recommended for lowest latency.",
            active=s.getboolean("force_pipewire_output", fallback=False),
        )
        self.w_pulse_lat = self._spin_row(
            settings_box, "PulseAudio Latency (ms)",
            "Latency on the PulseAudio side. Increase if needed. Only applies with Default/PulseAudio output.",
            value=int(s.get("pulse_latency_msec", 1)), min_val=1, max_val=500,
        )
        self.w_bass = self._spin_row(
            settings_box, "BASS Audio Latency (game-side)",
            "Internal BASS latency. Increase if you get audio cracking. A pop-up will appear on osu launch — safe to ignore.",
            value=int(s.get("bass_dev_period", 2)), min_val=-100, max_val=100,
        )

        # ---- Section: Renderer ----
        self._section(settings_box, "RENDERER")
        self.w_vulkan = self._toggle_row(
            settings_box, "Force Vulkan Renderer",
            "Sets Renderer=Deferred_Vulkan in framework.ini. Required for framerate cap and LatencyFleX to work.",
            active=s.getboolean("force_vulkan", fallback=False),
        )
        self.w_wayland = self._toggle_row(
            settings_box, "Force Wayland",
            "Sets SDL_VIDEODRIVER=wayland,x11. Falls back to X11 if Wayland is unavailable.",
            active=s.getboolean("force_wayland", fallback=False),
        )
        self.w_lfx = self._toggle_row(
            settings_box, "Enable LatencyFleX",
            "Sets LFX=1 for lower mouse latency. Most effective with VRR. May not work on all GPUs.",
            active=s.getboolean("enable_lfx", fallback=False),
        )

        # bottom padding
        settings_box.pack_start(Gtk.Box(height_request=10), False, False, 0)

        # ---- Footer ----
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.get_style_context().add_class("footer-box")
        footer.set_halign(Gtk.Align.END)
        root.pack_start(footer, False, False, 0)

        btn_cancel = Gtk.Button(label="Cancel")
        btn_cancel.get_style_context().add_class("btn-cancel")
        btn_cancel.connect("clicked", self._on_cancel)
        footer.pack_start(btn_cancel, False, False, 0)

        btn_launch = Gtk.Button(label="▶  Launch osu!")
        btn_launch.get_style_context().add_class("btn-launch")
        btn_launch.connect("clicked", self._on_launch)
        footer.pack_start(btn_launch, False, False, 0)

    # -----------------------------------------------------------------------
    # UI helpers
    # -----------------------------------------------------------------------
    def _section(self, parent, label_text):
        box = Gtk.Box()
        box.set_margin_top(14)
        box.set_margin_bottom(4)
        lbl = Gtk.Label(label=label_text)
        lbl.get_style_context().add_class("section-label")
        lbl.set_halign(Gtk.Align.START)
        box.pack_start(lbl, False, False, 0)
        parent.pack_start(box, False, False, 0)

    def _spin_row(self, parent, name, hint, value, min_val, max_val):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.get_style_context().add_class("setting-row")
        row.set_margin_bottom(5)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text_box.set_hexpand(True)
        text_box.set_valign(Gtk.Align.CENTER)

        lbl_name = Gtk.Label(label=name)
        lbl_name.get_style_context().add_class("setting-name")
        lbl_name.set_halign(Gtk.Align.START)
        text_box.pack_start(lbl_name, False, False, 0)

        lbl_hint = Gtk.Label(label=hint)
        lbl_hint.get_style_context().add_class("setting-hint")
        lbl_hint.set_halign(Gtk.Align.START)
        lbl_hint.set_line_wrap(True)
        lbl_hint.set_max_width_chars(48)
        text_box.pack_start(lbl_hint, False, False, 0)

        row.pack_start(text_box, True, True, 0)

        adj = Gtk.Adjustment(value=value, lower=min_val, upper=max_val,
                             step_increment=1, page_increment=10, page_size=0)
        spin = Gtk.SpinButton(adjustment=adj, climb_rate=1, digits=0)
        spin.get_style_context().add_class("setting-widget")
        spin.set_valign(Gtk.Align.CENTER)
        spin.set_size_request(90, -1)
        row.pack_start(spin, False, False, 0)

        parent.pack_start(row, False, False, 0)
        return spin

    def _toggle_row(self, parent, name, hint, active):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.get_style_context().add_class("setting-row")
        row.set_margin_bottom(5)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text_box.set_hexpand(True)
        text_box.set_valign(Gtk.Align.CENTER)

        lbl_name = Gtk.Label(label=name)
        lbl_name.get_style_context().add_class("setting-name")
        lbl_name.set_halign(Gtk.Align.START)
        text_box.pack_start(lbl_name, False, False, 0)

        lbl_hint = Gtk.Label(label=hint)
        lbl_hint.get_style_context().add_class("setting-hint")
        lbl_hint.set_halign(Gtk.Align.START)
        lbl_hint.set_line_wrap(True)
        lbl_hint.set_max_width_chars(48)
        text_box.pack_start(lbl_hint, False, False, 0)

        row.pack_start(text_box, True, True, 0)

        sw = Gtk.Switch()
        sw.set_active(active)
        sw.set_valign(Gtk.Align.CENTER)
        row.pack_start(sw, False, False, 0)

        parent.pack_start(row, False, False, 0)
        return sw

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------
    def _on_delete(self, _win, _event):
        self._result = 1
        Gtk.main_quit()
        return False

    def _on_cancel(self, _btn):
        self._result = 1
        Gtk.main_quit()

    def _on_launch(self, _btn):
        self._save_settings()
        self._result = 0
        Gtk.main_quit()

    def _save_settings(self):
        s = self.cfg["launch"]
        s["strangle_fps"] = str(int(self.w_fps.get_value()))
        s["force_unlimited_framerate"] = str(self.w_unlimited.get_active()).lower()
        s["pipewire_latency"] = str(int(self.w_pw_lat.get_value()))
        s["force_pipewire_output"] = str(self.w_force_pw.get_active()).lower()
        s["pulse_latency_msec"] = str(int(self.w_pulse_lat.get_value()))
        s["bass_dev_period"] = str(int(self.w_bass.get_value()))
        s["force_vulkan"] = str(self.w_vulkan.get_active()).lower()
        s["force_wayland"] = str(self.w_wayland.get_active()).lower()
        s["enable_lfx"] = str(self.w_lfx.get_active()).lower()
        save_config(self.cfg)

        framework_ini = get_framework_ini_path()
        first_launch = not os.path.isfile(framework_ini)

        if first_launch:
            # Build all framework.ini values from the current toggle state in one shot
            initial_values = {}
            if self.w_unlimited.get_active():
                initial_values["FrameSync"] = "Unlimited"
            if self.w_force_pw.get_active():
                initial_values["AudioDevice"] = "PipeWire Sound Server"
            if self.w_vulkan.get_active():
                initial_values["Renderer"] = "Deferred_Vulkan"
            if initial_values:
                init_framework_ini(initial_values)
        else:
            # File already exists — update only the enabled keys, leave everything else
            if self.w_unlimited.get_active():
                set_framework_ini_value("FrameSync", "Unlimited")
            if self.w_force_pw.get_active():
                set_framework_ini_value("AudioDevice", "PipeWire Sound Server")
            if self.w_vulkan.get_active():
                set_framework_ini_value("Renderer", "Deferred_Vulkan")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    win = OsuConfigWindow()
    win.show_all()
    Gtk.main()
    sys.exit(win._result)


if __name__ == "__main__":
    main()
