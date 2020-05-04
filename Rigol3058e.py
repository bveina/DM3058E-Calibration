import visa
import time
from engineering_notation import EngNumber
import engineering_notation
from fluke5500a import Fluke5500A
from Rigol3058 import *
import matplotlib.pyplot as plt
import numpy as np
import struct

def get3058Res():
    rm = visa.ResourceManager()
    for dev in rm.list_resources():
      if "DM3R" in dev:
        return dev
    return None
    
def dmmConnect():
  global dmm
  dmm=None
  dmmName = get3058Res()
  print ("found dmm:",dmmName)
  dmm=Rigol3058E(rm.open_resource(dmmName))
  #dmm = Rigol3058E(rm.open_resource('ASRL15::INSTR'))
  dmm.inst.timeout=20000
     

rm = visa.ResourceManager()
print( 'got RM')
time.sleep(1)
#print('getting list')
#rm.list_resources()
#time.sleep(1)
print('getting DMM')


dmmConnect()

print('getting calibrator')
try:
  cal = Fluke5500A(rm.open_resource('GPIB0::5::INSTR'))
except:
  print("cant get the calibrator")
  cal=Fluke5500A(None)
  

VDC_SHORT=[(0, 8e-6, '200mV'), (1, 60e-6, '2V'), (2, 800e-6, '20V'), (3, 6e-3, '200V'), (4, 30e-3, '1000V')] 
ADC_SHORT=[(0, 10e-9, '200uA'), (1, 100e-9, '2mA'), (2, 4e-6, '20mA'), (3, 16e-6, '200mA'), (4, 400e-6, '2A'), (5, 1e-3, '10A')] 
FRES_SHORT=[(0,10e-3,'200R'),(1,60e-3,'2kR'),(2,600e-3,'20kR'),(3,6,'200kR'),(4,80,'2MR'),(5,300,'10MR'),(6,4000,'100MR')] 




vFull = [ 
    {'range':0, 'vals':['-200mV','0Ohm','200mV']},
    {'range':1, 'vals':['-2V','0Ohm','2V']},
    {'range':2, 'vals':['-20V','0Ohm','20V']},
    {'range':3, 'vals':['-200V','0Ohm','200V']},
    {'range':4, 'vals':['-1000V','0Ohm','1000V']}
    ]
            
def fullVReadback(stabilize=5):
    engineering_notation.engineering_notation._exponent_lookup_scaled['-9']="E"
    for d in vFull:
        readback(d['vals'],":MEAS:VOLT:DC {0}".format(d['range']))
    cal.write('out 0V')
            
#V200mV = [ -190,-180,-170,-160,-150,-140,-130,-120,-110,-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0,
#             10,  20,  30, 40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190]      
        
def getQSR():
  return {"qsrC":dmm.qsrC,"qsrEN":dmm.qsrEN,"qsrEV":dmm.qsrEV}
  
def getOSR():
  return {"osrC":dmm.osrC,"osrEN":dmm.osrEN,"osrEV":dmm.osrEV}
 

VDCcals = [ (0,'200mV'),(1,'2V'),(2,'20V'),(3,'200V'),(4,'1000V')]
  
def fixCalibration(range,maxVal,mode='VOLT:DC'):
  print("setting OUT min")
  cal.out=0
  print("setting range")
  dmm.range=range
  print("calibrating zero")
  dmm.write("CALI:{0}:ZERO rigolproduct".format(mode))
  waitForCali()
  input("has Zero Settled?")
  print("setting OUT max")
  cal.out=maxVal
  print("calibrating gain")
  dmm.write("CALI:{0}:GAIN rigolproduct".format(mode))
  waitForCali()
  input("has gain Settled?")  


def dumpCalibration(x=""):
  dmm.write("CALI:STEP 490 {0}".format(x),deep=False)
  return dmm.inst.read_raw()
  
def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
    yield lst[i:i + n]  
  
def printCalibration(tmp):
  for i,t in enumerate(chunks(tmp[4:],8)):
    print("{0:11.2f}".format(struct.unpack("d",t)[0]),end=" ")
    if ((i+1)%6==0): print()


def waitForCali():
  while (int(dmm.query(":CALI:STATUS?"))):
   print(".",end='')
   time.sleep(.5)
  
        
V200mV = [
    (0,'-200.0mV'), (1,'-187.5mV'), (2,'-175.0mV'), 
    (3,'-162.5mV'), (4,'-150.0mV'), (5,'-137.5mV'), 
    (6,'-125.0mV'), (7,'-112.5mV'), (8,'-100.0mV'),
    (9,'-87.5mV'), (10,'-75.0mV'), (11,'-62.5mV'), 
    (12,'-50.0mV'), (13,'-37.5mV'), (14,'-25mV'),
    (15,'-12.5mV'),(16, '0.0mV'), (17,'12.5mV'),
    (18, '25.0mV'), (19,'37.5mV'), (20,'50.0mV'), 
    (21,'62.5mV'), (22,'75.0mV'), (23,'87.5mV'),
    (24,'100.0mV'), (25, '112.5mV'), (26, '125.0mV'), 
    (27,'137.5mV'), (28,'150.0mV'), (29,'162.5mV'), 
    (30,'175.0mV'), (31,'187.5mV'), (32,'200.0mV')]

V2V = [
    (0, '-2.0V'), #(1, '-1.9V'), (2, '-1.8V'), (3, '-1.7V'), 
    #(4, '-1.6V'), (5, '-1.5V'), (6, '-1.4V'), (7, '-1.3V'), 
    #(8, '-1.2V'), (9, '-1.1V'), (10, '-1.0V'), (11, '-0.9V'), 
    #(12, '-0.8V'), 
    (13, '-0.7V'), (14, '-0.6V'), (15, '-0.5V'), 
    (16, '-0.4V'), (17, '-0.3V'), (18, '-0.2V'), (19, '-0.1V'), 
    (20, '0.0V'), (21, '0.1V'), (22, '0.2V'), (23, '0.3V'), 
    (24, '0.4V'), (25, '0.5V'), (26, '0.6V'), (27, '0.7V'), 
    #(28, '0.8V'), (29, '0.9V'), (30, '1.0V'), (31, '1.1V'), 
    #(32, '1.2V'), (33, '1.3V'), (34, '1.4V'), (35, '1.5V'), 
    #(36, '1.6V'), (37, '1.7V'), (38, '1.8V'), (39, '1.9V'), 
    (40, '2.0V')
    ]
    
    
def SetCal(val):
    cal.write("out {0}".format(val))
    if (val == '0 OHM'):
        cal.write('ZCOMP 4WIRE')
    while (int(cal.query('oper?'))==0):
        time.sleep(1)
        cal.write('oper')
    
def calRange(lst,needPause=False): 
    brvWrite(':MEASure:VOLT:DC 0')
    for i,x in lst:
        print ("out is {0}".format(x))
        cali(i,x,needPause)
        

def cali(step,val,needPause=False):
    cal.write("out {0}".format(val))
    if (val == '0 OHM'):
        cal.write('ZCOMP 4WIRE')
    cal.write('oper')
    
    if needPause:input("cont>")
    try:
        res = dmm.query(":CALI:STEP {0}".format(step))
        print(res)
    except visa.VisaIOError:
        print("ignoring lack of response")
    
    while (int(dmm.query(":CALI:STATUS?"))):
        print(".",end='')
        time.sleep(.5)
    if needPause: input("cont>")
    
def readback(lst,range=':MEAS:VOLT:DC 1'):
    engineering_notation.engineering_notation._exponent_lookup_scaled['-9']="E"
    dmm.write(range)
    time.sleep(1) #life is to short to wait for the output to stabilize while testing this crap
    for x in lst:
        cal.write('out {0}'.format(x))
        if (x == '0 OHM'):
            cal.write('ZCOMP 4WIRE')
        cal.write('oper')
        time.sleep(1)#life is to short to wait for the output to stabilize while testing this crap
        t = float(dmm.query(":MEASURE:VOLT:DC?"))
        
        print("exp: {0:9s} recv: {1}".format(x,EngNumber(t,precision=5)))
 
def shortTest(tolerances,settingCmd,measureCmd,tSettle=5):
    status=True
    for rng,tol,desc in tolerances:
        st = settingCmd+ ' ' + str(rng)
        print(st)
        dmm.write(st)
        time.sleep(tSettle)
        val = dmm.query(measureCmd)
        val = float(val)
        if abs(val)<=tol:
            print("range {0}: |{1}| <= {2}".format(desc,EngNumber(val),EngNumber(tol)))
        else:
            print("Tolerance failure: range {0} is {1} should be less than {2}".format(
                desc, EngNumber(val), EngNumber(tol)))
            status=False
    return status



def testDCVoltsShort(tSettle=5):
    return shortTest(VDC_SHORT,':MEAS:VOLT:DC',':MEAS:VOLT:DC?',tSettle)
   
                
def testDCAmpsShort(tSettle=5):
    return shortTest(ADC_SHORT,':MEAS:CURR:DC',':MEAS:CURR:DC?',tSettle)
                
def testResShort(tSettle=5):
    return shortTest(FRES_SHORT,':MEAS:FRES',':MEAS:FRES?',tSettle) 
              

def getFlukeVal(inst):
    inst.query('VAL1?')
    val = inst.read()
    inst.read()
    val=float(val)
    return val
    
def setFlukeRange(inst,mode,range,Speed):
    volt_fast = [300e-3, 3, 30, 300, 1000]
    ohm_Fast = [300, 3e3, 30e3, 300e3, 3e6, 30e6, 300e6]
    curr_Fast = [30e-3, 100e-3, 10]
    freq_Fast = [1e3, 10e3, 100e3, 1e6]
    
    volt_Slow = [0.1,1,10,100,1000]
    ohm_Slow = [100,1e3,10e3,100e3,1e6,10e6,100e6]
    curr_Slow = [.01,.1,10]
    freq_Slow = [1e3, 10e3, 100e3, 1e6]
    
def Fluke8842_Check(inst,cal):
    mode={'VDC':'F1','VAC':'F2','RES2':'F3','RES4':'F4',
        'DCA':'F5','ACA':'F6'}
    range={'auto on':'R0','20m':'R8','200m':'R1',
        '2':'R2','20':'R3','200':'R4','2000':'R5',
        'auto off':'R7'}
    rate = {'slow':'S0','medium': 'S1','fast':'S2'}    
    
def brvWrite(val):
    t=""
    try:
        t=dmm.write(val)
    except visa.VisaIOError:
        print("VISAIOERROR")
    print("ERROR:",dmm.query(':SYSTEM:ERROR?'))
    dmm.write("*CLS")
    return t
    
def brvQuery(val):
    t=""
    try:
        t=dmm.query(val)
    except visa.VisaIOError:
        print("VISAIOERROR")
    print("ERROR:",dmm.query(':SYSTEM:ERROR?'))    
    dmm.write("*CLS")
    return t

def fullVReadback(stabilize=5):
    engineering_notation.engineering_notation._exponent_lookup_scaled['-9']="E"
    for d in vFull:
        readback(d['vals'],":MEAS:VOLT:DC {0}".format(d['range']))
    cal.write('out 0V')

vals=np.linspace(-200,200,num=21)
def readBack(rng,fileName,unit):
    res=[]
    for i in rng:
        cal.out="{0}{1}".format(i,unit)
        try:
        
          t = float(dmm.getVal())
          if (abs(t)>1000000):
            res.append(None)
          else:
            res.append(t)
        except VisaIOError:
          res.append(None)
    fig=plt.figure()
    plt.plot(rng,res)    
    fig.savefig(fileName)
    plt.show() 
    plt.close()

    
def Fluke45_VDCCheck(inst,cal):
    # range, speed, calibrator output, (min, max)
    tests = [ (1,'S','0 Ohm',(-.006,0.006)),
              (1,'S','90 mV',(89.971e-3,90.029e-3)),
              (4,'S','900 mV',(899.71e-3,900.29e-3)),
              (1,'F','0 Ohm',(-0.02,0.02)),
              (1,'F','300 mV',(299.90e-3,300.1e-3)),
              (2,'F','3 V',(2.999,3.001)),
              (2,'F','-3 V',(-3.001,-2.999)),
              (3,'F','30 V',(29.990,30.010)),
              (4,'F','300 V',(299.9,300.1)),
              (5,'F','1000 V',(999.5,1000.5)) ]
    inst.query("VDC")
    inst.read()
    cal.write('stby')
    
    
    for tst  in tests:
        status='none'
        rng,speed,outputVal,limits = tst
        inst.query('RANGE {0}'.format(range))
        inst.read()
        inst.query('RATE {0}'.format(speed))
        inst.read()
        cal.write('stby')
        cal.write('out {0}'.format(outputVal))
        cal.write('oper')
        time.sleep(5)
        val=getFlukeVal(inst)
        
        if (val >= limits[0] and val <= limits[1]):
            status='PASS'
        else:
            status='FAIL'
        print('{2}: {0} -- {1},{3}'.format(outputVal,EngNumber(val),status,limits))
                