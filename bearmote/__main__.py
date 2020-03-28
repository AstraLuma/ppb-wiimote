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


ppb.run(
    starting_scene=LoadingScene, scene_kwargs={'next_scene': ConnectScene},
    systems=[bearmote.WiimoteSystem],
)
