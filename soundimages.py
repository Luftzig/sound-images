"""
SoundImages: play sample taken from file

Author: Yoav Luft, yoav.luft _at_ gmail.com
"""

import Nsound as nsound
# import scikits.audiolab as audiolab
import numpy as np
import scipy.ndimage as ndimage
import threading
import matplotlib.pyplot as plt
import scipy.misc
from Queue import Queue

OUTPUT_SAMPLE_RATE = 44100.0


def subsample(img, c0, c1, num=441, tile=100):
    x, y = np.linspace(c0[0], c1[0], num), np.linspace(c0[1], c1[1], num)
    return np.tile(ndimage.map_coordinates(img, np.vstack((x, y))), tile)


def play_sample(img, c0, c1, num=441, tile=100):
    subsample(img, c0, c1, num, tile)


class AudioPlayer:
    """Simple audio player that consumes audio from a queue"""

    def __init__(self):
        self.snd_buffer = Queue(1)
        self.is_running = False
        self.player_thread = None
        self.output_stream = nsound.AudioPlayback(OUTPUT_SAMPLE_RATE)

    def run(self):
        self.player_thread = threading.Thread(target=self.play)
        self.is_running = True
        self.player_thread.daemon = True
        self.player_thread.start()

    def get_queue(self):
        return self.snd_buffer

    def play(self):
        print 'Play started'
        while 1:
            print 'Sampling'
            sample = self.snd_buffer.get()
            print 'Playing sample'
            self.output_stream << sample


class Display:
    def __init__(self, img):
        self.initialize_image_figure(img)
        self.last_click = (None, None)
        self.press_handler = self.image_figure.canvas.mpl_connect('button_press_event', self.press_handle)
        self.move_handler = self.image_figure.canvas.mpl_connect('motion_notify_event', self.move_handle)
        self.player = AudioPlayer()
        self.player.run()

    def initialize_image_figure(self, img):
        self.image = img
        self.image_figure = plt.figure()
        self.axes = self.image_figure.add_subplot(211)
        self.axes_image = self.axes.imshow(self.image)
        self.line = None
        self.subsample = self.image_figure.add_subplot(212)
        axes_axis = self.axes.axis()
        self.subsample.set_xlim(xmin=axes_axis[0], xmax=axes_axis[1])

    def press_handle(self, event):
        print 'Click event', event.xdata, event.ydata
        self.last_click = (event.xdata, event.ydata)

    def move_handle(self, event):
        # print 'Move event', event.xdata, event.ydata
        if self.last_click[0] is None or self.last_click[1] is None or event.xdata is None or event.ydata is None:
            return
        print('Last click was: {} event move: {}'.format(self.last_click, (event.xdata, event.ydata)))
        if self.line is not None:
            self.line[0].set_data([[self.last_click[0], event.xdata], [self.last_click[1], event.ydata]])
        else:
            self.line = self.axes.plot([self.last_click[0], event.xdata], [self.last_click[1], event.ydata], "ro-")
        self.axes.figure.canvas.draw()
        subsampled_line = subsample(self.image, self.last_click, (event.xdata, event.ydata), num=441)
        self.subsample.lines = []
        self.subsample.plot(subsampled_line)
        # print("Subsampled line {}".format(subsampled_line))
        # self.player.get_queue().put(subsampled_line)
        print


if __name__ == '__main__':
    lena = scipy.misc.lena()
    display = Display(lena)
    plt.show()
