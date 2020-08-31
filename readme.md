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
:CALI:<MODE>:ZERO <Range>
:CALI:<MODE>:GAIN <Range>
```
Where
- ```n``` is a number between 0 and 492 (with some gaps)
- ```mode``` is anything you could put after a ```:MEAS``` scpi commands (eg ```VOLT:DC```)
- ```Range``` 0,1,2,... corresponding to the Range being calibrated

Commands in the style ``` :CALI:VOLT:DC:ZERO 0 ``` work great, but can not currently be stored to non volatile memory. they cant survive ```*RST```

commands in the style ``` :CALI:STEP n ``` can be stored via ``` :CALI:STEP 487 ``` and be reset to factory defaults via ``` :CALI:STEP 488 ``` but it is not as simple as zero and gain there is some extra piece that seams to add in a non linearity and requires more research.


Steps >487 are important for writing and resetting values
487. seems to write the values into flash memory
488. resets the values to a built in default.
489. not clear but references AC half Ranges
490. prints the calibration constants (must use a raw read)
491. seems to disconnect the front terminals (hear a relay click)
492. seems to reconnect the front terminals (hear a relay click)

single elements of calibration can be accomplished but the entire procedure has not been mapped out yet.

before running calibration code the first few elements of the calibration constants were
```
In [47]: printCalibration(dumpCalibration())
b'00000000'
       0.00        1.00        1.00        1.00        1.00        0.00
```

```python
# this is intentionally aligning this to incorrect values to prove a point.
# to undo this  run step 488
dmm.range=0
cal.setVoltage(.01) #should really be a short (see above)
dmm.calibrate('step 0') # cal ZERO
cal.setVoltage(.1) # should really be 200mV
dmm.calibrate('step 34') # cal GAIN
dmm.calibrate('step 487') # write Vals
```

this results in:

```
In [45]: printCalibration(dumpCalibration())
b'00000000'
      -0.02        3.09        3.09        1.00        1.00        0.00
```

I'd call that a successful test. but it doesn't really work as well as it sound (introduces serious nonlinearity in the readings.)





### Side benefits
A few commands were discovered that are not directly related to calibration but are interesting none the less.
```C
":WEBcontrol:KEY:SET <n>" //tries to press a key but keys cant be pressed while remote is enabled
":WEBcontrol:KEY:GET?" // returns a bitmask related to keys that are currently lit. see the Expiriments page for mask values.
":WEBcontrol:GUI:GET?" // returns a bitmap of the current screen.
"SYSTEM:PROD:PASS rigolproduct" // allow you to change things you really shouldent
"SYST:PROD:SETType DM1234" // change model type (DM3058E,DM3068)
"SYSTEM:PROD:SETSerial <newserial>" // change your serial number (ie DM3R1234A1234)
"SYST:PROD:SETMacaddr aa:AA:aa:aa:aa:aa" // only really matters if you have an LXI interface...

"SYSTEM:PROD:CLOSE rigollan" // save those things you really shouldent change

"WINDOW:STATUS 0|1|ON|OFF" // turn off entire display
"WINDOW:STATUS?" // check if display is on


```

To save a png of the screen use ```SaveScreen("output.png")```




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

The steps seep to follow that the setting byte is related to if step is a  Zero or gain step but toward the bottom of the list there is obviously more going on. (1 seems to be ZERO, 0 seems to be GAIN).

most steps setup some internal memory locations then let the multimeter chug along.

```
//bad pseudocode
case n:
  IsCalRunning=1
  removeCalConstants??=1
  ZeroGain=<settingByte>
  SCPIprintf("CALIBRATION:STEP %d",n)
  break:
```
|Start | Stop   |  Length | Setting Byte   |Note   |
|---|---|---|---|---|
|0   |  4 |5 |1|VDC Zero (Ranges: 200mV, 2V, 20V, 200V, 1kV)|
|10  | 14 |5 |1| |
|19  | 25 |7 |1|Res2? SHORT|
|26  | 32 |7 |1|Res4? SHORT|
|33  | 33 |1 |1|Frequency Calibration (give 100kHz @ 2V) (DC will hang the dmm)|
|34  | 38 |5 |0| VDC gain |
|105 |109 |5 |0||
|110 |114 |5 |0||
|116 |119 |4 |0||
|120 |126 |7 |0|Res2? gain?|
|127 |133 |7 |0|Res4? gain?|
|140 |140 |1 |0|hangs without VAC input (tweaks Freq measurement)|
|141 |141 |1 |0|hangs without VAC input (tweaks Freq measurement)|
|142 |146 |5 |10| vdc related?|
|147 |151 |5 |10||
|152 |158 |7 |10|Res2?|
|159 |165 |7 |10|Res4?|
|361 |361 |1 |11||
|362 |366 |5 |12| effects CalConstant[3]|
|367 |371 |5 |13|effects CalConstant[3&4]|
|372 |376 |5 |12|effects CalConstant[3]|
|377 |381 |5 |13|effects CalConstant[3&4]|
|382 |386 |5 |14|AC and DC HANG|
|387 |391 |5 |15|NO DC (hangs)|
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
|469 |474 |6 |1| CAPacitance Zero?|
|475 |480 |6 |10| CAPacitance Gain?|
|481 |486 |6 |0||
|487 |487 |1 |NA| Write Calibrations to factory memory|
|488 |488 |1 |NA| Reload default constants|
|489 |489 |1 |NA| Half Range related?|
|490 |490 |1 |NA| Dump Calibration Constants|
|491 |491 |1 |NA|DMA4 coms(Disable Connection to terminal?)|
|492 |492 |1 |NA|DMA4 coms(Enable Connection to terminals?)|


The last 5 steps are very interesting. and have some impressive effects.


### internal function representations
functions are set in multiple places and do
_setfunction
- VDC  1
- VAC  2
- ADC  3
- AAC  4
- ReS2 5
- res4 9
- freq A
- peri 6
- cont 7
- diode b
- cap ???


- setRange - sets dmmMode
- VDC    0 - 0x1100
- VAC    1 - 0x3100  
- ADC    2 - 0x2100
- AAC    3 - 0x4100
- res2   4 - 0x5100
- res4   5 - 0x6100
- cont   6 - 0x9100
- diode  7 - 0xA100
- freq   9 - 0x7100
- Period a - 0x8100
- cap    b - 0xe100



### Repo code
helper classes were created to make my life simpler while testing out theories.
- Fluke5500 is a calibrator that can generate the signals for the DM3058E
 - this, or similar 5520A, should be used if you want to actually align your multimeter
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
git clone https://github.com/bveina/DM3058E-Calibration.git
cd DM3058E-Calibration
```

### Setup your virtual env (this is the windows version of virtual envirment)
```
virtualenv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Enter the terminal
```bash
ipython -i testbed.py
````
This will attempt to connect to the fluke and the DMM. you may need to adjust your code to speak to the correct device.
