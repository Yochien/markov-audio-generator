# Markov Audio Generator

Tool to aid in computer music creation by providing a framework to quickly iterate on pieces using the markov process.

## How to Use

*Note*: You can run either sub program with the `-h` flag to get an explanation of any arguments.

### Generate Your Config File

1. Build your FSM using [this](https://www.cs.unc.edu/~otternes/comp455/fsm_designer/) site or [this](https://madebyevan.com/fsm/) site making sure to follow the caveats below.
    - **Disclaimer**: This project relies on the work by [Evan Wallace](https://github.com/evanw) linked above, but is not affiliated with them in any way.
    - *Note*: The first link has a version that will allow for reuploading previous works to modify them.
    1. *Note*: To indicate that there is a percentage chance to transition from a given state to another one, use a decimal representing that percentage. Ex: 20% chance to transition from A to B would be denoted with a connecting arrow labelled `.2`.
    2. *Note*: Requires a state named `end` in order to properly exit.
2. Save your FSM as a `.json` file.
3. Run the `build_config` script with your FSM file as the input.
    - This will generate a `.yaml` file that is used for configuring the audio generation script later.

### Configuring Your Generator

*This configuration is done in your `.yaml` file generated in the previous section.*

1. Each state in your FSM `.json` file gets an entry under the `group_audio_map` list.
2. Under each state is a list of file paths. Each state can have any number of sounds associated with it that are selected at random when the state is selected during audio generation.
3. Update the file paths to your desired audio files, making sure to have at least one per state.
4. The `state_group_map` list associates each set of choices for a state to its state name. If you changed the name of any of the entries under `group_audio_map`, make sure to update the `state_group_map` to reflect your changes.
5. `minimum_simulation_length` represents the shortest number of combinations of sounds you are willing to accept for your final audio output.
    - i.e. if you set the `minimum_simulation_length` to `10` and the markov process terminates with a run of audio that uses only `9` sounds, the program will retry generating automatically and discard the short result.
6. `maximum_simulation_length` exists to prevent situations where the program would run forever, either due to an improperly exiting FSM or too strict a minimum output length.
    - This option will end generation after traversing `maximum_simulation_length` number of states.

### Generating Your Piece

1. Run the `build_markov` script and provide it both the FSM `.json` file and configuration `.yaml` file.
    - The traversal through the markov process, assuming multiple samples and some state transition choices, should yield different results every time.

## Credits

Example samples generated with [sfxr](https://sfxr.me/).
