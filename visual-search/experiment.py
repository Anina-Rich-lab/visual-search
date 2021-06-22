import argparse
import os
import csv
from math import sin, cos, pi
from random import random
from typing import Dict, List, Optional
from psychopy import visual, core, event
from psychopy.hardware import keyboard

VALID_STIMULI_DIR = "true"
INVALID_STIMULI_DIR = "false"


class VisualSearch:
    def __init__(self, stimuli_location: str, circle_rad: float) -> None:
        self.window = visual.Window(fullscr=True, monitor="testMonitor", units="deg")
        self.fixation = visual.ShapeStim(self.window,
                                         vertices=((0, -0.5), (0, 0.5), (0, 0), (-0.5, 0), (0.5, 0)),
                                         lineWidth=2,
                                         closeShape=False,
                                         lineColor="black")
        self.stimuli = self.load_stimuli(stimuli_location)
        self.kb = keyboard.Keyboard()
        self.rad = circle_rad

    def get_valid(self) -> List[visual.ImageStim]:
        return random.sample(self.stimuli["valid"], 1)

    def get_invalid(self, n: int) -> List[visual.ImageStim]:
        return random.sample(self.stimuli["valid"], n)

    def place_stimuli(self, nc: int, is_target_present: bool) -> List[visual.ImageStim]:
        """ Place randomly the stimuli around a circle with radius `r`. """

        stimuli = self.get_valid() + self.get_invalid(nc - 1) if is_target_present else self.get_invalid(nc)
        random.shuffle(stimuli)

        angle_div = 2 * pi / len(stimuli)
        rand_offset = random() * 2 * pi

        for i, s in enumerate(stimuli):
            angle = angle_div * i + rand_offset
            s.pos = [self.rad * cos(angle), self.rad * sin(angle)]

        return stimuli

    def show_items(self, stimuli: List[visual.ImageStim], show_fix: Optional[bool] = True) -> None:
        for s in stimuli:
            s.draw()
        if show_fix:
            self.fixation.draw()
        self.window.update()

    def show_fixation(self) -> None:
        self.fixation.draw()
        self.window.update()

    def show_feedback(self, success: bool) -> None:
        if success:
            self.success_visual.draw()
        else:
            self.failure_visual.draw()
        self.window.update()

    def run_trial(self,
                  feedback_timeout: Optional[float] = 3.0,
                  fixation_timeout: Optional[float] = 2.0,
                  response_timeout: Optional[float] = float('inf')) -> None:
        """
            Each trial runs in three stages:
            1. Show fixation screen for a fixed period `fixation_timeout`.
            2. Show a number of items `n_items`, then wait for keyboard response up to a limit `response_timeout`.
            3. Show feedback for a `feedback_timeout`.
        """
        # TODO: 0. Get items for experiment
        stimuli = self.place_stimuli(nc=4, is_target_present=True)

        # 1. Show blank with fixation.
        self.show_fixation()
        core.wait(fixation_timeout)

        # 2. Redraw now with items, wait for response
        self.show_items(stimuli)
        self.kb.clock.reset()
        keys = self.kb.waitKeys(maxWait=response_timeout, keyList=['x', 'm'])
        for key in keys:
            # TODO: store results.
            print(key.name, key.rt, key.duration)

        # 3. Show feedback.
        self.show_feedback(True)
        core.wait(feedback_timeout)

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

    def store_data(self, info: dict) -> None:
        with open('path/to/csv_file', 'w') as f:
            writer = csv.writer(f)
            writer.writerow()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", default="stimuli", help="Address of directory containin stimuli.", type=str)
    parser.add_argument("-r", default=5.0, help="Distance of stimuli from center.", type=float)

    args = parser.parse_args()

    vs = VisualSearch(stimuli_location=args.d,
                      circle_rad=args.r)

    def start():
        vs.rad += 1
        vs.run_trial()

    event.globalKeys.add(key='q', modifiers=['ctrl'], func=core.quit)
    event.globalKeys.add(key='r', func=start)

    while True:
        core.wait(0.001)
