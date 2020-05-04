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


### Cali:Step
the steps seem to be split into groups based on mode and ranges

internally modes are numbered:
0. Volt DC (5 ranges)
1. Volt AC (5 ranges)
2. Amps DC (6 ranges)
3. Amps AC (4 ranges)
4. Resistance (7 ranges)
5. 4 Wire Res (7 Ranges)
6. Frequency
7. Period
8. Continuity
9. Diode

The steps seep to follow that the setting byte is related to if step is a  Zero or gain step but toward the bottom of the list ther is obviously more going on. (1 seems to be ZERO, 0 seems to be GAIN).

|Start|Stop   |  Length | SettingByte   |Note   |
|---|---|---|---|---|
|0   |  4 |5 |1|VDC |
|10  | 14 |5 |1|VAC|
|19  | 25 |7 |1|Res2?|
|26  | 32 |7 |1|Res4?|
|33  | 33 |1 |1|VERY ODD behavior (AVOID)|
|34  | 38 |5 |0||
|105 |109 |5 |0||
|110 |114 |5 |0||
|116 |119 |4 |0||
|120 |126 |7 |0|Res2?|
|127 |133 |7 |0|Res4?|
|140 |140 |1 |0||
|141 |141 |1 |0||
|142 |146 |5 |10||
|147 |151 |5 |10||
|152 |158 |7 |10|Res2?|
|159 |165 |7 |10|Res4?|
|361 |361 |1 |11||
|362 |366 |5 |12||
|367 |371 |5 |13||
|372 |376 |5 |12||
|377 |381 |5 |13||
|382 |386 |5 |14||
|387 |391 |5 |15||
|392 |396 |5 |14||
|397 |401 |5 |15||
|402 |408 |7 |14|Res2?|
|409 |415 |7 |14|Res4?|
|416 |416 |1 |1||
|417 |417 |1 |1||
|418 |418 |1 |10||
|419 |419 |1 |13||
|420 |420 |1 |12||
|421 |421 |1 |14||
|422 |422 |1 |15||
|423 |427 |5 |16||
|428 |432 |5 |17||
|433 |437 |5 |19||
|438 |442 |5 |20||
|443 |447 |5 |21||
|448 |448 |1 |18||
|449 |452 |4 |16||
|453 |456 |4 |17||
|457 |460 |4 |19||
|461 |464 |4 |20||
|465 |468 |4 |21||
|469 |474 |6 |1||
|475 |480 |6 |10||
|481 |486 |6 |0||
|487 |487 |1 |NA| reset any hand calibration?|
|488 |488 |1 |NA||
|489 |489 |1 |NA|Half Range related?|
|490 |490 |1 |NA|Dump Default Calibration Table?|
|491 |491 |1 |NA|Disable Connection to terminal?|
|492 |492 |1 |NA|Enable Connection to terminals?|


The last 5 steps are very interesting. and have some impressive effects.


### Repo code
helper classes were created to make my life simpler while testing out theories.
- Fluke5500 is a calibrator that can generate the signals for the DM3058E
 - this, or similar, should be used if you want to actually align your multimeter
- DP832 is a multi channel power supply. *This is not a precision instrument don't calibrate your DMM with this!*
 - it is smaller than the Fluke5500 and fits on my desk, it is enough to figure out if i have actually realigned the DMM
- DM3058E is the multimeter under investigation.
- DM3058.py holds scripts that test alignment and calibration.



# Setup (Windows)
Generally a project like this would use Linux. I don't have a dedicated Linux box and NIVISA doesn't play nice with Windows Subsytem for Linux (WSL). This is developed and aimed at Windows with python3

### Install nivisa
https://pyvisa.readthedocs.io/en/latest/faq/getting_nivisa.html#faq-getting-nivisa

### Clone the Repo
```
git clone https://github.com/TBA
cd TBA
```

### Setup your virtual env (this is the windows version of virtual envirment)
```
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Enter the terminal
```bash
ipython -i -c "from DM3058E import \*"
````
This will attempt to connect to the fluke and the DMM. you may need to adjust your code to speak to the correct device.
