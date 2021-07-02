# Visual search experiment.

Experiment template for visual search, based on psychopy.

In this specific case, a set of stimuli appear in a circle around the center of the screen.
On each trial, there is a 50% chance of the `target` stimuli to appear.
The task for the subjects is to respond as fast as possible whether the target is present in the current trial.

To recreate this experiment, you can download this repository, open it on psychopy and run the `visualsearch.py` script.
When you run the script, you will be prompted with a dialog to enter the id of the participant.

After each trial, the result will be written to a file `data.csv` next to the script.

You can press the `esc` key to exit the experiment.

## Changes to the experiment.
There is a few options that you can play with in this script:

- Change the stimuli images:
By default, a set of stimuli are included in the `stimuli` folder, and can be targets (in the `target` folder) or distractors (in `distractor`).
Feel free to change the images in this folder for your experiment, but note that only `jpg` and `png` files can be used.

- Change condition blocks:
In the provided example, 3 blocks of trials with different settings.
You can change the existing blocks or add more to your experiment by editing the `experiment_setup` variable in the `visualsearch.py` script.
The avaliable settings are:
    - `set_size`: Number of elements appearing on each trial.
    - `radio`: All elements appear in a circle of radio `radio` around the fixation (you should keep it between 5 and 15).
    - `repetitions`: Number of trials per block.
    - `feedback_timeout`: How long the feedback should be shown (in seconds).
    - `prerun_timeout`: How long will it pass between the start of the trial and when the stimuli are shown (in seconds).
    - `response_timeout`: Maximum allowed response time (if the participant does not respond on time, the trial answer will be marked as incorrect).
    - `rotate_images`: If True, the stimuli will be rotated randomly on each trial.

- Change the introduction and goodbye texts via the `introduction_text` and `final_text` variables.

- Change the size of the stimuli with the `size_of_stimuli` variable.

## CSV file fields.
Description of the fields in the csv file where the data is stored.

| Key | Value |
| --- | --- |
| sId | Id of the subject for the experiment. |
| age | Subject age. |
| handedness | Subject handedness. |
| sex | Subject sex. |
| run_number | For each subject, the id of the run. This allows differentiating when the same the subject runs the experiment multiple times. |
| target_present | True if the target was visible in the trial, otherwise False. |
| set_size | Number of conditions in the trial. |
| radio | Distance from the center of the screen to each stimuli. |
| feedback_timeout | Period of time where only the fixation was shown (before stimuli appear) in seconds.|
| prerun_timeout | Period of time where the feedback was visible (after participant responds) in seconds. |
| timestamp | Timestamp marking the beggining of a trial (Unix timestamp).|
| response_time | Time between the moment when the stimuli are shown and the participant response is detected. |
| correct_answer | whether the participant answered correctly (True) or not (False). |
| pressed_key | What key was pressed by the participant. |
| response_timed_out | True if the participand did not respond on time. |
| stimuli_rotated | True if the stimuli were rotated randomly for this trial. |
