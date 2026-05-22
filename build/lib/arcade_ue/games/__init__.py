from .breakout import BreakoutPlugin
from .legacy import LegacyPlugin
from .mode7_demo import Mode7DemoPlugin
from .pinball import PinballPlugin
from .twinstick import TwinStickPlugin


def default_plugins():
    return [
        BreakoutPlugin(),
        TwinStickPlugin(),
        PinballPlugin(),
        Mode7DemoPlugin(),
        LegacyPlugin(),
    ]
