from bibliopixel.layout import Matrix
from bibliopixel.drivers import SimPixel
from bibliopixel.animation.matrix import BaseMatrixAnim
import bibliopixel.colors as colors


class BeamAnimation(BaseMatrixAnim):
    def __init__(self, layout):
        super().__init__(layout)
        self.internal_delay = 0.05
        self.colors = [colors.Red, colors.Green, colors.Blue, colors.White]

    def step(self, amt=1):

        for px in range(self.layout.numLEDs):
            cols = int(self.layout.numLEDs / 2)
            row = px % cols
            c = colors.wheel.wheel_color((self._step + row) % 384)
            self.layout._set_base(px, c)

        self._step += 1

if __name__ == '__main__':
    driver = SimPixel.SimPixel(num=216)
    led = Matrix(driver, width=108, height=2, serpentine=False)

    animation = BeamAnimation(led)
    animation.run()

