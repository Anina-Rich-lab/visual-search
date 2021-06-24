import os
import csv
from math import sin, cos, pi
import random
from typing import Dict, List, Optional
from psychopy import visual, core, event, gui
from psychopy.hardware import keyboard


"""
    Change the settings for the experiment.
    `experiment_setup` is a list of experiment blocks with different settings. You can change these settings to
    configure the experiment.

    On each block:
        `conditions`: Number of elements appearing on each trial
        `radio`: All elements appear in a circle of radio `radio` around the fixation
        `repetitions`: Number of trials per block
"""
experiment_setup = [
    # Block 1
    {
        'conditions': 8,
        'radio': 10,
        'repetitions': 10
    },
    # Block 2
    {
        'conditions': 12,
        'radio': 12,
        'repetitions': 10
    },
    # Block 3
    {
        'conditions': 16,
        'radio': 14,
        'repetitions': 10
    }
    # ... Feel free to add more blocks.
]

"""
    By default, we expect the stimuli images to be placed in a folder called `stimuli` next to this script, and
    containing two subfolders `target` and `distractor` containing the target and distractor stimuli respectively (like
    in the provided example).

    If you want, here you can change the expected location or name of the `stimuli` folder, or the name of the
    subfolders.
"""
stimuli_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stimuli')
target_stimuli_dir_name = "target"
distractor_stimuli_dir_name = "distractor"

"""
    Full path to file where data will be stored.
    By default, it will be `<Path to visual-search>/data.csv`
"""
data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.csv')


class VisualSearch:
    def __init__(self,
                 config: Dict,
                 data_file: str,
                 target_present_key: Optional[str] = 'x',
                 target_not_present_key: Optional[str] = 'm') -> None:

        self.config = config
        self.data_file = data_file

        # Window setup
        self.window = visual.Window(fullscr=True, monitor="testMonitor", units="deg")
        event.globalKeys.add(key='q', modifiers=['ctrl'], func=core.quit)
        self.fixation = visual.ShapeStim(self.window,
                                         vertices=((0, -0.5), (0, 0.5), (0, 0), (-0.5, 0), (0.5, 0)),
                                         lineWidth=2,
                                         closeShape=False,
                                         lineColor="black")
        self.tick = visual.ImageStim(win=self.window,
                                     size=2,
                                     image=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                        "assets",
                                                        "tick.png"))
        self.fail = visual.ImageStim(win=self.window,
                                     size=2,
                                     image=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                        "assets",
                                                        "fail.png"))

        # Check stimuli directory.
        self.stimuli = self.load_stimuli(stimuli_dir)

        # Keyboard setup.
        self.kb = keyboard.Keyboard()
        self.tp_key = target_present_key
        self.ntp_key = target_not_present_key

    def get_image_stim(self, sid: str, n: int, repeat: Optional[bool] = True) -> List[visual.ImageStim]:
        if repeat:
            return [visual.ImageStim(win=self.window, image=random.choice(self.stimuli[sid]), size=2) for _ in range(n)]
        else:
            return [visual.ImageStim(win=self.window, image=f, size=2) for f in random.sample(self.stimuli[sid], n)]

    def get_valid(self) -> List[visual.ImageStim]:
        return self.get_image_stim("valid", 1, repeat=False)

    def get_invalid(self, n: int) -> List[visual.ImageStim]:
        return self.get_image_stim("invalid", n)

    def place_stimuli(self, nc: int, is_target_present: bool, r: float) -> List[visual.ImageStim]:
        """ Place randomly the stimuli around a circle with radius `r`. """

        stimuli = self.get_valid() + self.get_invalid(nc - 1) if is_target_present else self.get_invalid(nc)
        random.shuffle(stimuli)

        angle_div = 2 * pi / len(stimuli)
        rand_offset = random.random() * 2 * pi

        for i, s in enumerate(stimuli):
            angle = angle_div * i + rand_offset
            s.pos = [r * cos(angle), r * sin(angle)]

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
            self.tick.draw()
        else:
            self.fail.draw()
        self.window.update()

    def run_trial(self,
                  is_target_present: bool,
                  n_conditions: int,
                  radio: float,
                  feedback_timeout: Optional[float] = 3.0,
                  fixation_timeout: Optional[float] = 2.0,
                  response_timeout: Optional[float] = float('inf')) -> Dict:
        """
            Each trial runs in three stages:
            1. Show fixation screen for a fixed period `fixation_timeout`.
            2. Show a number of items `n_items`, then wait for keyboard response up to a limit `response_timeout`.
            3. Show feedback for a `feedback_timeout`.
        """
        # 0. Get items for experiment
        stimuli = self.place_stimuli(nc=n_conditions, is_target_present=is_target_present, r=radio)
        result = {
                'sId': self.config['Subject'],
                'target_present': is_target_present,
                'conditions': n_conditions,
                'radio': radio,
                'fixation_time': fixation_timeout,
                'feedback_time': feedback_timeout,
                'timestamp': core.getAbsTime()
            }

        # 1. Show blank with fixation.
        self.show_fixation()
        core.wait(fixation_timeout)

        # 2. Redraw now with items, wait for response
        self.show_items(stimuli)
        self.kb.clock.reset()
        keys = self.kb.waitKeys(maxWait=response_timeout, keyList=[self.tp_key, self.ntp_key])

        for key in keys:
            correct = key.name == (self.tp_key if is_target_present else self.ntp_key)
            result['response_time'] = key.rt
            result['correct_answer'] = correct
            result['pressed_key'] = key.name

        # 3. Show feedback.
        self.show_feedback(correct)
        core.wait(feedback_timeout)

        # 4. Clear the screen.
        self.window.update()
        return result

    def load_stimuli(self, location: str) -> Dict[str, List[visual.ImageStim]]:
        # Check if location exists.
        if not os.path.isdir(location):
            raise ValueError("Invalid address: {}".format(location))
        # Check if there is something in the folder.
        valid_folder = os.path.join(location, target_stimuli_dir_name)
        invalid_folder = os.path.join(location, distractor_stimuli_dir_name)
        if not os.path.isdir(valid_folder) and os.path.isdir(invalid_folder):
            raise ValueError(
                "Folder {} does not contain stimuli folders {} or {}.".format(
                    location,
                    target_stimuli_dir_name,
                    distractor_stimuli_dir_name))

        # Now, we can get all images in the folders.
        stimuli = {"valid": [], "invalid": []}
        for im in os.listdir(valid_folder):
            stimuli["valid"].append(os.path.join(valid_folder, im))

        for im in os.listdir(invalid_folder):
            stimuli["invalid"].append(os.path.join(invalid_folder, im))

        return stimuli

    def store_data(self, info: dict) -> None:
        if not os.path.isfile(self.data_file):
            # Create new file and add header.
            with open(self.data_file, 'w') as f:
                writer = csv.DictWriter(f, tuple(info.keys()))
                writer.writeheader()
                writer.writerow(info)
        else:
            with open(self.data_file, 'a') as f:
                writer = csv.DictWriter(f, tuple(info.keys()))
                writer.writerow(info)

    @staticmethod
    def gen_trials(n_trials):
        trials = [True if i < n_trials // 2 else False for i in range(n_trials)]
        random.shuffle(trials)
        return trials

    def run(self):
        for block in self.config['blocks']:
            trials = self.gen_trials(block['repetitions'])
            for t in trials:
                r = self.run_trial(is_target_present=t, n_conditions=block['conditions'], radio=block['radio'])
                self.store_data(r)


if __name__ == '__main__':

    config = {
        'Subject': '',
    }

    gui.DlgFromDict(config)

    # Append experiment setup configuration.
    config['blocks'] = experiment_setup

    vs = VisualSearch(config=config, data_file=data_file)
    vs.run()
