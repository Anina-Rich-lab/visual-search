# Visual search experiment.

Experiment template for visual search, based on psychopy.

In this specific case, a set of stimuli appear in a circle around the center of the screen.
On each trial, there is a 50% chance of the `target` stimuli to appear.
The task for the subjects is to respond as fast as possible wether the target is present in the current trial.

To recreate this experiment, you can download this repository, open it on psychopy and run the `visualsearch.py` script.
When you run the script, you will be prompted with a dialog to enter the id of the participant.

After each trial, the result will be written to a file `data.csv` next to the script.

## Changes to the experiment.
There is a few options that you can play with in this script:

- Change the stimuli images:
By default, a set of stimuli are included in the `stimuli` folder, and can be targets (in the `target` folder) or distractors (in `distractor`).
Feel free to change the images in this folder for your experiment.

- Change condition blocks:
In the provided example, 3 blocks of trials with different number of conditions, distance to the center of the screen and number of repetitions are provided.
You can change the existing blocks or add more to your experiment by editing the `experiment_setup` variable in the `visualsearch.py` script.

