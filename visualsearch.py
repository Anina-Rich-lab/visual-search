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
        `set_size`: Number of elements appearing on each trial
        `radio`: All elements appear in a circle of radio `radio` around the fixation
        `repetitions`: Number of trials per block
        `feedback_timeout`: How long the feedback should be shown (s)
        `fixation_timeout`: How long will it pass between the start of the trial and when the stimuli are shown (s)
        `response_timeout`: Maximum allowed response time (if the participant does not respond on time, the trial answer
                           will be marked as incorrect).
        `rotate_images`: If True, the stimuli will be rotated randomly on each trial.
"""
experiment_setup = [
    # Block 1
    {
        'set_size': 4,
        'radio': 10,
        'repetitions': 10,
        'feedback_timeout': 1,
        'fixation_timeout': 0.5,
        'response_timeout': 4,
        'rotate_images': True,
    },
    # Block 2
    {
        'set_size': 8,
        'radio': 10,
        'repetitions': 10,
        'feedback_timeout': 1,
        'fixation_timeout': 0.5,
        'response_timeout': 4,
        'rotate_images': True,
    },
    # Block 3
    {
        'set_size': 12,
        'radio': 10,
        'repetitions': 10,
        'feedback_timeout': 1,
        'fixation_timeout': 0.5,
        'response_timeout': 4,
        'rotate_images': True,
    }
    # ... Feel free to add more blocks.
]

"""
    Text shown in the introduction.
"""
introduction_text = """
    Example introduction.

    ---------------------
    In this experiment, you will be finding red circles in the screen.
    The experiment consists of several trials with increased difficulty.
    Each trial starts with an empty screen where only the center of the screen is marked by a cross.
    After some time, a set of objects will appear. You need to detect if a red circle is present on the screen.
    Press the `x` if you can see the target in the screen, and `m` if it is not there.

    When you are ready, press any key to start.
    ---------------------

    """

"""
    Text shown when finished.
"""
final_text = """ Thank you for participating! """

"""
    Size of stimuli.
"""
size_of_stimuli = 2

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
    """
        Visual search experiment.
    """
    def __init__(self,
                 config: Dict,
                 data_file: str,
                 target_present_key: Optional[str] = 'x',
                 target_not_present_key: Optional[str] = 'm') -> None:

        # Configuration
        self.config = config
        self.data_file = data_file
        self.config['RunNumber'] = self.subject_run_number()

        # Window setup
        self.window = visual.Window(fullscr=True, monitor="testMonitor", units="cm")
        event.globalKeys.add(key='escape', func=core.quit)
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
        """ Generate a list of stimuli. """
        if repeat:
            return [visual.ImageStim(win=self.window,
                                     image=random.choice(self.stimuli[sid]),
                                     size=size_of_stimuli) for _ in range(n)]
        else:
            return [visual.ImageStim(win=self.window,
                                     image=f,
                                     size=size_of_stimuli) for f in random.sample(self.stimuli[sid], n)]

    def get_target(self) -> List[visual.ImageStim]:
        """ Generate a list with one target stimuli. """
        return self.get_image_stim("target", 1, repeat=False)

    def get_distractor(self, n: int) -> List[visual.ImageStim]:
        """ Generate a list with n distractor stimuli. """
        return self.get_image_stim("distractor", n)

    def place_stimuli(self, nc: int, is_target_present: bool, r: float, rotated: bool) -> List[visual.ImageStim]:
        """ Place randomly the stimuli around a circle with radius `r`. """

        stimuli = self.get_target() + self.get_distractor(nc - 1) if is_target_present else self.get_distractor(nc)
        random.shuffle(stimuli)

        angle_div = 2 * pi / len(stimuli)
        rand_offset = random.random() * 2 * pi

        for i, s in enumerate(stimuli):
            angle = angle_div * i + rand_offset
            s.pos = [r * cos(angle), r * sin(angle)]
            if rotated:
                s.ori = random.random() * 360

        return stimuli

    def show_items(self, stimuli: List[visual.ImageStim], show_fix: Optional[bool] = True) -> None:
        """ Update screen to show the fixation and stimuli. """
        for s in stimuli:
            s.draw()
        if show_fix:
            self.fixation.draw()
        self.window.update()

    def show_fixation(self) -> None:
        """ Update screen to show the fixation only. """
        self.fixation.draw()
        self.window.update()

    def show_feedback(self, success: bool) -> None:
        """ Update screen to show whether the answer was correct. """
        if success:
            self.tick.draw()
        else:
            self.fail.draw()
        self.window.update()

    def show_text_page(self, text: str, blocking: Optional[bool] = True) -> None:
        """ Show page with some text. """
        introduction = visual.TextStim(self.window, text=text, wrapWidth=100)
        introduction.draw()
        self.window.update()
        if blocking:
            self.kb.waitKeys()

    def show_introduction(self) -> None:
        """ Show page with introduction text. """
        self.show_text_page(self.config['intro'])

    def show_outro(self) -> None:
        """ Show page with introduction text. """
        self.show_text_page(self.config['outro'])

    def run_trial(self,
                  is_target_present: bool,
                  set_size: int,
                  radio: float,
                  images_rotate: bool,
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
        stimuli = self.place_stimuli(nc=set_size, is_target_present=is_target_present, r=radio, rotated=images_rotate)
        result = {
                'sId': self.config['Subject'],
                'run_number': self.config['RunNumber'],
                'target_present': is_target_present,
                'set_size': set_size,
                'radio': radio,
                'stimuli_rotated': images_rotate,
                'fixation_timeout': fixation_timeout,
                'feedback_timeout': feedback_timeout,
                'timestamp': core.getAbsTime()
            }

        # 1. Show blank with fixation.
        self.show_fixation()
        core.wait(fixation_timeout)

        # 2. Redraw now with items, wait for response
        self.show_items(stimuli)
        self.kb.clock.reset()
        keys = self.kb.waitKeys(maxWait=response_timeout, keyList=[self.tp_key, self.ntp_key])

        correct = False
        if keys:
            for key in keys:
                correct = key.name == (self.tp_key if is_target_present else self.ntp_key)
                result['correct_answer'] = correct
                result['pressed_key'] = key.name
                result['response_time'] = key.rt
                result['response_timed_out'] = False
        else:
            result['correct_answer'] = False
            result['pressed_key'] = ''
            result['response_time'] = 0
            result['response_timed_out'] = True

        # 3. Show feedback.
        self.show_feedback(correct)
        core.wait(feedback_timeout)

        # 4. Clear the screen.
        self.window.update()
        return result

    def load_stimuli(self, location: str) -> Dict[str, List[str]]:
        """
            Check the stimuli folder and get the files for target and distractors.

            Accepted file extensions: 'png', 'jpg'
        """

        # Check if location exists.
        if not os.path.isdir(location):
            raise ValueError("Invalid address: {}".format(location))
        # Check if there is something in the folder.
        target_folder = os.path.join(location, target_stimuli_dir_name)
        distractor_folder = os.path.join(location, distractor_stimuli_dir_name)
        if not os.path.isdir(target_folder) and os.path.isdir(distractor_folder):
            raise ValueError(
                "Folder {} does not contain stimuli folders {} or {}.".format(
                    location,
                    target_stimuli_dir_name,
                    distractor_stimuli_dir_name))

        # Now, we can get all images in the folders.
        stimuli = {"target": [], "distractor": []}
        for im in os.listdir(target_folder):
            if im.endswith("png") or im.endswith("jpg"):
                stimuli["target"].append(os.path.join(target_folder, im))

        for im in os.listdir(distractor_folder):
            if im.endswith("png") or im.endswith("jpg"):
                stimuli["distractor"].append(os.path.join(distractor_folder, im))

        return stimuli

    def store_data(self, info: dict) -> None:
        """ Write entry of CSV file. """
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

    def subject_run_number(self) -> int:
        """ Get the last experiment number for a given subject. """
        if not os.path.isfile(self.data_file):
            return 0
        with open(self.data_file, 'r') as f:
            entries = []
            reader = csv.DictReader(f)
            for row in reader:
                if row['sId'] == self.config['Subject']:
                    entries.append(int(row['run_number']))
            if len(entries) == 0:
                return 0
            else:
                return max(entries) + 1

    @staticmethod
    def gen_trials(n: int) -> List[bool]:
        """
            For a number of trials `n`, create an index of trials where 50% are guaranteed to be positive and 50%
            negative.
        """
        trials = [True if i < n // 2 else False for i in range(n)]
        random.shuffle(trials)
        return trials

    def run(self) -> None:
        """ Run the experiment. """
        self.show_introduction()
        for block in self.config['blocks']:
            trials = self.gen_trials(block['repetitions'])
            for t in trials:
                r = self.run_trial(is_target_present=t,
                                   set_size=block['set_size'],
                                   radio=block['radio'],
                                   images_rotate=block.get('rotate_images', False),
                                   feedback_timeout=block.get('feedback_timeout', 3.0),
                                   fixation_timeout=block.get('fixation_timeout', 2.0),
                                   response_timeout=block.get('response_timeout', float('inf')))
                self.store_data(r)
        self.show_outro()


if __name__ == '__main__':

    config = {
        'Subject': '',
    }

    info_dlg = gui.DlgFromDict(config)

    if info_dlg.OK:
        # Append experiment setup configuration.
        config['blocks'] = experiment_setup

        # Append text to configuration
        config['intro'] = introduction_text
        config['outro'] = final_text

        vs = VisualSearch(config=config, data_file=data_file)
        vs.run()
