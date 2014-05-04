"""
SoundImages: play sample taken from file

Author: Yoav Luft, yoav.luft _at_ gmail.com
"""

import scikits.audiolab as audiolab
import numpy as np
import scipy.ndimage as ndimage
import threading
import matplotlib.pyplot as plt
import scipy.misc
from Queue import Queue


def subsample(img, c0, c1, num=441, tile=100):
    x, y = np.linspace(c0[0], c1[0], num), np.linspace(c0[1], c1[1], num)
    return np.tile(ndimage.map_coordinates(img, np.vstack((x, y))), tile)


def playsample(img, c0, c1, num=441, tile=100):
    audiolab.play(subsample(img, c0, c1, num, tile))


class AudioPlayer:

    "Simple audio player that consumes audio from a queue"

    def __init__(self):
        self.snd_buffer = Queue(1)
        self.is_running = False
        self.player_thread = None

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
            audiolab.play(sample)


class Display:

    def __init__(self, img):
        self.image = img
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111)
        self.axes_image = self.ax.imshow(self.image)
        self.last_click = (None, None)
        self.press_cid = self.figure.canvas.mpl_connect( \
                'button_press_event', self.press_handle)
        self.move_cid = self.figure.canvas.mpl_connect( \
                'motion_notify_event', self.move_handle)
        self.player = AudioPlayer()
        self.line = self.ax.plot([0], [0])
        self.player.run()

    def press_handle(self, event):
        x, y = self.last_click
        # print 'Click event', event.xdata, event.ydata
        if event.inaxes != self.axes_image:
            return
        self.last_click = (event.xdata, event.ydata)

    def move_handle(self, event):
        # print 'Move event', event.xdata, event.ydata
        if event.inaxes != self.axes_image:
            return
        if self.last_click[0] == None or self.last_click[1] == None:
            return
        self.axis.plot(self.last_click, (event.xdata, event.ydata), 'ro-')
        self.axis.figure.canvas.draw()
        self.player.get_queue.put(subsample(\
                self.image, self.last_click, \
                    (event.xdata, event.ydata), \
                    num=441))
        print


if __name__ == '__main__':
    lena = scipy.misc.lena()
    display = Display(lena)
    plt.show()
