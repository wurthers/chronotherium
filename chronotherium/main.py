from chronotherium.scene import StartScene
from chronotherium.window import Window
from clubsandwich.director import DirectorLoop

window = Window()


class SceneLoop(DirectorLoop):
    def get_initial_scene(self):
        return StartScene()


if __name__ == '__main__':
     SceneLoop().run()
