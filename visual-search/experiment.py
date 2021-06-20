import argparse
import os
from math import sin, cos, pi
from random import random
from typing import Dict, List
from psychopy import visual, core, event
from psychopy.hardware import keyboard

VALID_STIMULI_DIR = "true"
INVALID_STIMULI_DIR = "false"


class VisualSearch:
    def __init__(self, stimuli_location: str) -> None:
        self.window = visual.Window(fullscr=True, monitor="testMonitor", units="deg")
        self.stimuli = self.load_stimuli(stimuli_location)
        self.kb = keyboard.Keyboard()

    def place_stimuli(self, r: float) -> None:
        """ Place randomly the stimuli around a circle with radius `r`. """
        stimuli = self.stimuli["valid"] + self.stimuli["invalid"]

        angle_div = 2 * pi / len(stimuli)
        rand_offset = random() * 2 * pi

        for i, s in enumerate(stimuli):
            angle = angle_div * i + rand_offset
            s.pos = [r * cos(angle), r * sin(angle)]

    def draw(self) -> None:
        stimuli = self.stimuli["valid"] + self.stimuli["invalid"]
        for s in stimuli:
            s.draw()
        self.window.update()

    def run_trial(self, timeout=float('inf')) -> None:
        self.kb.clock.reset()
        keys = self.kb.waitKeys(maxWait=timeout, keyList=['x', 'm'])
        for key in keys:
            # TODO: store results.
            print(key.name, key.rt, key.duration)

    def load_stimuli(self, location: str) -> Dict[str, List[visual.ImageStim]]:
        # Check if location exists.
        if not os.path.isdir(location):
            raise ValueError("Invalid address: {}".format(location))
        # Check if there is something in the folder.
        valid_folder = os.path.join(location, VALID_STIMULI_DIR)
        invalid_folder = os.path.join(location, INVALID_STIMULI_DIR)
        if not os.path.isdir(valid_folder) and os.path.isdir(invalid_folder):
            raise ValueError(
                "Folder {} does not contain stimuli folders {} or {}.".format(
                    location,
                    VALID_STIMULI_DIR,
                    INVALID_STIMULI_DIR))

        # Now, we can get all images in the folders.
        stimuli = {"valid": [], "invalid": []}
        for im in os.listdir(valid_folder):
            stimuli["valid"].append(visual.ImageStim(win=self.window, image=os.path.join(valid_folder, im), size=2))

        for im in os.listdir(invalid_folder):
            stimuli["invalid"].append(visual.ImageStim(win=self.window, image=os.path.join(invalid_folder, im), size=2))

        return stimuli


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", default="stimuli", help="Address of directory containin stimuli.", type=str)

    args = parser.parse_args()

    vs = VisualSearch(args.d)

    r = 10

    def change_rad():
        global r
        r += 1
        vs.place_stimuli(r)
        vs.draw()
        vs.run_trial()

    event.globalKeys.add(key='q', modifiers=['ctrl'], func=core.quit)
    event.globalKeys.add(key='r', func=change_rad)

    while True:
        core.wait(0.001)
