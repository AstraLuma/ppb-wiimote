"""
PPB Support for a wiimote.
"""
import typing

import concurrent.futures
from dataclasses import dataclass
import functools
import operator

import cwiid
import ppb.events
from ppb import BaseScene
from ppb.systemslib import System
from ppb.flags import Flag


@dataclass
class ConnectWiimote:
    """
    Connect a wiimote
    """


@dataclass
class WiimoteConnected:
    """
    Wiimote has been connected.
    """
    id: typing.Any = None


class WiimoteButton(Flag, abstract=True):
    """
    A Wiimote Button
    """


@dataclass
class WiimoteButtonPressed:
    """
    Fired when a button is pressed
    """
    button: WiimoteButton


@dataclass
class WiimoteButtonReleased:
    """
    Fired when a button is pressed
    """
    button: WiimoteButton


class One(WiimoteButton):
    """
    The 1 button
    """


class Two(WiimoteButton):
    """
    The 2 button
    """


class A(WiimoteButton):
    """
    The A button
    """


class B(WiimoteButton):
    """
    The B/trigger button
    """


class Up(WiimoteButton):
    """
    Up on the d-pad (when held upright)
    """


class Down(WiimoteButton):
    """
    Down on the d-pad (when held upright)
    """


class Left(WiimoteButton):
    """
    Left on the d-pad (when held upright)
    """


class Right(WiimoteButton):
    """
    Right on the d-pad (when held upright)
    """


class Plus(WiimoteButton):
    """
    The + button
    """


class Minus(WiimoteButton):
    """
    The - button
    """


class Home(WiimoteButton):
    """
    The Home button
    """


_button_map = {
    cwiid.BTN_1: One,
    cwiid.BTN_2: Two,
    cwiid.BTN_A: A,
    cwiid.BTN_B: B,
    cwiid.BTN_DOWN: Down,
    cwiid.BTN_HOME: Home,
    cwiid.BTN_LEFT: Left,
    cwiid.BTN_MINUS: Minus,
    cwiid.BTN_PLUS: Plus,
    cwiid.BTN_RIGHT: Right,
    cwiid.BTN_UP: Up,
}


class WiimoteLed(Flag, abstract=True):
    """
    Wiimote LEDs
    """


@dataclass
class SetWiimoteLed:
    """
    Set the LEDs on the wiimote
    """
    id: typing.Any
    leds: typing.Set[WiimoteLed]


class Led1(WiimoteLed):
    pass


class Led2(WiimoteLed):
    pass


class Led3(WiimoteLed):
    pass


class Led4(WiimoteLed):
    pass


_led_map = {
    cwiid.LED1_ON: Led1,
    cwiid.LED2_ON: Led2,
    cwiid.LED3_ON: Led3,
    cwiid.LED4_ON: Led4,
}


def _bitfield2set(field, map):
    return {
        flag
        for mask, flag in map.items()
        if field & mask
    }


def _set2bitfield(pile, map):
    return functools.reduce(operator.or_, (
        mask
        for mask, flag in map.items()
        if flag in pile
    ))


class ConnectScene(BaseScene):
    """
    A helper base class for making "Connect wiimote" scenes.

    Handles all the talking-to-the-wiimote bits. The user is expected to
    populate UI.
    """

    def on_scene_started(self, event, signal):
        signal(ConnectWiimote())

    def on_wiimote_connected(self, event, signal):
        signal(ppb.events.StopScene())


@dataclass
class MoteState:
    """
    Object to keep track of the mote's state
    """
    buttons: set


class WiimoteSystem(System):
    def __init__(self, engine, **kws):
        super().__init__(engine=engine, **kws)
        self.engine = engine
        self._motes = {}
        self._exec = concurrent.futures.ThreadPoolExecutor()

    def __exit__(self, *exc):
        for mote in self._motes.values():
            mote.close()
        super().__exit__(*exc)

    def on_connect_wiimote(self, event, signal):
        def _on_complete(fut):
            try:
                wiimote = fut.result()
            except RuntimeError:
                # Error opening wiimote connection
                # TODO: Do something
                signal(ppb.events.Quit())
                raise

            # Save wiimote and send out event
            # wiimote doesn't actually give us an address or _anything_
            last_id = max(self._motes.keys() or (-1,))
            this_id = last_id + 1
            self._motes[this_id] = wiimote
            signal(WiimoteConnected(id=this_id))

            # Configure
            # We do this after WiimoteConnected so that events can't get out-of-order
            state = MoteState(buttons=set())
            wiimote.mesg_callback = functools.partial(
                self._wiimote_handler, this_id, state,
            )
            wiimote.enable(cwiid.FLAG_MESG_IFC)
            wiimote.rpt_mode = cwiid.RPT_BTN

        fut = self._exec.submit(cwiid.Wiimote)
        fut.add_done_callback(_on_complete)

    def _wiimote_handler(self, mid, state, mesgs, timestamp):
        for mesg in mesgs:
            mtype, *payload = mesg
            if mtype == cwiid.MESG_STATUS:
                # Battery & extension info
                # TODO: Signal event
                pass
            elif mtype == cwiid.MESG_BTN:
                new_buttons = _bitfield2set(payload[0], _button_map)
                for btn in new_buttons - state.buttons:
                    self.engine.signal(WiimoteButtonPressed(button=btn))
                for btn in state.buttons - new_buttons:
                    self.engine.signal(WiimoteButtonReleased(button=btn))
                state.buttons = new_buttons
            # TODO: Additional stuff

    def on_set_wiimote_leds(self, event, signal):
        self._motes[event.id].led = _set2bitfield(event.leds, _led_map)
