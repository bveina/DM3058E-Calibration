# Manual Experiments
for these Experiments the goal is to elicit a noticible and mathmatically relevant offset and gain. not to make the instrument more accurate.

*save yourself some keystrokes and change the cal password to 'Z'*



##identifying led lights

running ```WEB:KEY:GET?``` with different key lights lit.

|KEYS|VALS|
|---|---|
|VDC, RUNHOLD| 0x80008|
| VDC, SINGLE| 0x40008|
|ADC, RUNHOLD| 0x80004|
|OHM, RUNHOLD| 0x80002|
| CONT, RUNHOLD | 0x80001|
| FREQ, RUNHOLD | 0x80800|
|FREQ, PRESET,RUNHOLD| 0x80C00|
|FREQ, PRESET, RUNHOLD, 2nd| 0x84C00|
|VAC, SINGLE| 0x40010|
|AAC, SINGLE| 0x40020|
|CAP, SINGLE| 0x40040|
|DIODE, SINGLE| 0x40080|
|SENSOR, SINGLE|0x480000|
|CONT, MEAS, SINGLE| 0x40201|
|VDC, MATH, SINGLE| 0x40108|
|VDC, TRIG, SINGLE|0x50008|
|VDC, HELP, SINGLE|0x42008|
|VDC, SAVE, SINGLE| 0x41008|
|VDC, UTILITY, SINGLE| 0x60008|

Conclusions:

|KEY|MASK|BIT|
|---|---|---|
|CONT   | 0x00001|0
|OHM    | 0x00002|1
|ADC    | 0x00004|2
|VDC    | 0x00008|3
|VAC    | 0x00010|4
|AAC    | 0x00020|5
|CAP    | 0x00040|6
|DIODE  | 0x00080|7
|MATH   | 0x00100|8
|MEAS   | 0x00200|9
|PRESET | 0x00400|10
|FREQ   | 0x00800|10
|SAVE   | 0x01000|12
|HELP   | 0x02000|13
|2ND    | 0x04000|14
|SENSOR | 0x08000|15
|TRIG   | 0x10000|16
|UTILITY| 0x20000|17
|SINGLE | 0x40000|18
|RUNHOLD| 0x80000|19



## identifying VDC cal table values

running the following code should produce incorrect results for the calibration tables for volts dc across all ranges. the assumption is that range 0-4 are the zero points, and steps 34-38 are the gain points for the DC ranges.
```python
for i in range(5):
    x=[.2,2,20,30,60]
    dmm.range=i
    cal.setVoltage(0)
    dmm.calibrate("step {0}".format(0+i))
    cal.setVoltage(x[i]/2)
    dmm.calibrate("step {0}".format(34+i))
dmm.calibrate("step 487")
```


```
In [3]: printCalibration(dumpCalibration())
b'00000000'
 -0.01   3.03   3.03   1.00   1.00   0.00   0.00   0.00
 -0.01   3.44   3.44   1.00   1.00   0.00   0.00   0.00
 -0.01   3.50   3.50   1.00   1.00   0.00   0.00   0.00
 -0.01  -3.11  -3.11   1.00   1.00   0.00   0.00   0.00
 -0.03  -0.70  -0.70   1.00   1.00   0.00   0.00   0.00
  0.00   1.00   1.00   0.00   0.00   0.00   0.00   0.00
```
Conclusions there seem to be 8 locations per range.
[0] is the zero offset
[1] and [2] are the GAIN
[3:7] are unknown

## identifying Frequncy Cal tables
using the analog discovery2 i created a 2VPk 150kHz sine wave an applied it to the DMM. after putting it in freqency mode:
Code to run
```python
In [8]: dmm.calibrate("step 33")
:CALIBRATION:STEP 33
.................................................................................
In [9]: dmm.calibrate("step 487")
:CALIBRATION:STEP 487
```
results in the dmm reporting 100kHz for the 150kHz sine wave.
the only changes in the calibration table are
```
before:
[row 34]
0.00   0.00   1.00   0.00   0.00   0.00   0.00   0.00
[row 34]
0.00   0.00   0.67   0.00   0.00   0.00   0.00   0.00
```

Conclusions
the freqwuency gain is stored at location 34*8+2=274

## issue step commands while in utility menu
 what if i am in that calibrate menu, then issue a step command?

1. mode VDC 200mV ranges

 before:

 |DVC | | | M 200mV | | |
|---|---|---|---|---|---|
|uncal 0:|| 0.000mV|Cal 0:|| 0.000mV|
|uncal G:|| 1.000 | Cal G:|| 1.000|
|Zero|Gain| |Default|Save| -^|

 after step 0, same as step 10:

 |DVC | | | M 200mV | | |
|---|---|---|---|---|---|
|uncal 0:|| 0.000mV|Cal 0:|| -0.0127mV|
|Behi Gain|| 0.000 | Cal G:|| 1.000|
|Zero|Full|Middle |Default| Save| -^|

2. VAC 200mV (terminals shorted or 1kHz 100mVpk)

 before:

 |ACV | | | M 200mV | | |
|---|---|---|---|---|---|
|uncal M:|| 100.000mV|Cal 0:|| 100.000mV|
|uncal G:|| 1.000 | Cal G:|| 1.000|
|Middle|Gain| |Default| Save| -^|

 after step 0 (hangs), or step 10(hangs) :

 |ACV | | | M 200mV | | |
 |---|---|---|---|---|---|
|uncal 0:|| 0.000mV|Cal 0:|| 0.000mV|
|uncal G:|| 1.000 | Cal G:|| 1.000|
|Middle|Gain| Freq |Little| Save| -^|

#### conclusion
no clear explaination of what happens. there are definite changes, but its unclear why these changes occur. this seems to be a case the designers of the meter didnt really intend.




## step 33: what is this thing?
this is a very strange step, what functions did the developers aim this at?

### test1 (this is the one that breaks)
1. disconnect all dm3058E inputs
2. put on volt DC 200mV Scale
3. use scpi to run step 33
#### Results
this never comes back and you have to reset the multimeter

### testN (i tried other functions until this one worked)
1. connect analog discovery to multimeter and set for 100kHz @ 2Vpk. this is the described method in the calibration guide for Frequency calibration.

2. run step 33.

#### results
Eventually this does return! (it takes 4ish times longer than most steps but it does return.)
aditionally this has very similar results as the "Breaking Frequency calibration" test!


## Breaking Frequency calibration
 using the manual calibration interface
### Equipment: analog dicovery 2, DM3058E

### Steps:

1. on DM3058, select Freq. and set to 2V scale (as described in calibation manual)
2. set Analog discovery to 2V_pk, 100kHz.
3. connect analog discovery output to DM3058E
4. Enter calibration menu and select GAIN
5. record results for different frequncies and voltages.

### Results
the utility calibration only shows Gain as a soft key.

|input|cal G|
|---|---|
|150kHz,2V| 0.667|
|100kHz,2V| 1.000|
|100kHz,1.5V| 1.000|
|50kHz,2V| 2.000|
|50kHz,1V| 2.000|

### Conclusion
Calibration only cares about the frequency. not the Voltage.


# dump CALIBRATION
step 490 requires you to do a ```read_raw``` to get the resulting data. looks like a factory calibration table.

calibration step 487 overwrites the values in this table.

calibration step 488 resets these to default values.


3484 bytes long, looks reasonable when viewed as 8 byte floating point numbers if you skip the first 4 bytes.


```
# viewed as Double precision floating point
       0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        0.00
       1.00       
       0.00        0.00        0.00        0.00        0.00        0.00       
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00       
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        1.00
       0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        
       0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        
       0.00        0.00        0.00        0.00        0.00       0.00        0.00        
       1.00        
       0.00        0.00        0.00        0.00        0.00  
       9997069.55  9997754.39        
       0.06        0.60        6.00       60.00      600.00        
       0.00        0.00        
       0.01        0.07        0.70        7.00       
      60.00      600.00     6000.00   60000.00   600000.00  3000000.00        
       0.00       
      60.00      600.00    6000.00    60000.00   600000.00  3000000.00        
       0.00       
      -0.06      -0.60       -6.00      -60.00     -600.00       
      -0.00       -0.00
      -0.01       -0.07       -0.70       -7.00        0.00        0.00
       1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        0.00       
       1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        0.00
       1.00        
       0.00        0.00        0.00        0.00        0.00        0.00        0.00        
       1.00        
       0.00        0.00        0.00        0.00        0.00        
       1.00        1.00        1.00        1.00        1.00        1.00        1.00        1.00        1.00        1.00        1.00        1.00        1.00        1.00        1.00        
       0.00
       0.00        1.00        0.00        0.00        0.00        0.00
       0.00        0.00        0.00        1.00        0.00        0.00
       0.00        0.00        0.00        0.00        0.00        1.00
       0.00        0.00        0.00        0.00        0.00        0.00
       0.00        1.00        0.00        0.00        0.00        0.00
       0.00        1.00        1.00        1.00        1.00        1.00
       1.00        1.00        1.00        1.00        1.00        1.00
       1.00        0.00        0.00        0.00        0.00        0.00
       0.01        0.00        0.00        0.00        0.00        0.00
       0.00        0.00        0.00        0.00        0.00        0.00
       0.00        0.00        0.00        0.00        0.00        0.00
       0.00        0.00        0.00
I
```
