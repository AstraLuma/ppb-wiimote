import ppb
from ppb.features import loadingscene
from ppb_mutant import Emoji
import bearmote


class LoadingScene(loadingscene.BaseLoadingScene):
    loading_icon = Emoji('bear')

    rotation_speed = 360 / 10

    def __init__(self, **props):
        super().__init__(**props)
        self.spinner = ppb.Sprite(image=self.loading_icon)
        self.add(self.spinner)

    def on_update(self, event, signal):
        self.spinner.rotation += self.rotation_speed * event.time_delta


class ConnectScene(bearmote.ConnectScene):
    connect_icon = Emoji('signal')

    def __init__(self, **props):
        super().__init__(**props)
        self.add(ppb.Sprite(image=self.connect_icon, size=3))

    def on_wiimote_connected(self, event, signal):
        signal(bearmote.SetWiimoteLed(id=event.id, leds={bearmote.Led1}))
        super().on_wiimote_connected(event, signal)


class PlayerSprite(ppb.Sprite):
    image = Emoji('bear')
    size = 2
    velocity = ppb.Vector(0, 0)

    BUTTONS = {
        bearmote.Right: ppb.Vector(1, 0),
        bearmote.Up: ppb.Vector(0, 1),
        bearmote.Left: ppb.Vector(-1, 0),
        bearmote.Down: ppb.Vector(0, -1),
    }

    def on_wiimote_button_pressed(self, event, signal):
        if event.button == bearmote.B:
            self.size *= 2
        elif event.button in self.BUTTONS:
            self.velocity += self.BUTTONS[event.button]

    def on_wiimote_button_released(self, event, signal):
        if event.button == bearmote.B:
            self.size /= 2
        elif event.button in self.BUTTONS:
            self.velocity -= self.BUTTONS[event.button]

    def on_update(self, event, signal):
        self.position += self.velocity * event.time_delta


class MainGame(ppb.BaseScene):
    def __init__(self, **props):
        super().__init__(**props)
        self.add(PlayerSprite())

    def on_scene_started(self, event, signal):
        signal(ppb.events.StartScene(new_scene=ConnectScene))


ppb.run(
    starting_scene=LoadingScene, scene_kwargs={'next_scene': MainGame},
    systems=[bearmote.WiimoteSystem],
)
