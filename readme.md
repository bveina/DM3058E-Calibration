# Rigol DM3058 Calibration Project
The Rigol DM3058E digital multimeter's Calibration/Alignment procedure is undocumented. This repo is to support research into automating both Calibration testing and creating the possibility of Alignment without having to send equipment to Rigol.

## DISCLAIMER
*Alignment should only be preformed if you have the equipment and skills required! If you don't know what you are doing you will end up with a LESS accurate meter, not a more accurate meter*

## Definitions
- Calibration - check if system is within spec, do not modify the system.
- Alignment - modify the system so it is back with spec.

## State of the project

Currently a partial picture of the alignment process has been uncovered. After partially analyzing the firmware, the following commands can be issued through  the SCPI USB interface.

```
:CALI:STEP <n>
:CALI:STATUS?
:CALI:<MODE>:ZERO <unk>
:CALI:<MODE>:GAIN <unk>
```
Where
- ```n``` is a number between 0 and 492 (with some gaps)
- ```mode``` is anything you could put after a ```:MEAS``` scpi commands (eg ```VOLT:DC```)
- ```unk``` is any text. at this time is looks like it is unused.

### repo code
helper classes were created to make my life simpler while testing out theories.
- Fluke5500 is a calibrator that can generate the signals for the DM3058E
 - this, or similar, should be used if you want to actually align your multimeter
- DP832 is a multi channel power supply. *This is not a precision instrument don't calibrate your DMM with this!*
 - it is smaller than the Fluke5500 and fits on my desk, it is enough to figure out if i have actually realigned the DMM
- DM3058E is the multimeter under investigation.
- DM3058.py holds scripts that test alignment and calibration.



# setup (Windows)
Geneerally a project like this would use unix. i dont have a dedicated unix box and NIVISA doesnt play nice with Windows Subsytem for linux (WSL) this is developed and aimed at Windows with python3

### Install nivisa
https://pyvisa.readthedocs.io/en/latest/faq/getting_nivisa.html#faq-getting-nivisa

### Setup your virtual env
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt

### Enter the terminal
```bash
ipython -i -c "from DM3058E import \*"
```
this will attempt to connect to the fluke and the DMM. you may need to adjust your code to speak to the correct device.
