import visa
import time
from engineering_notation import EngNumber
import engineering_notation
from fluke5500a import Fluke5500A
from Rigol3058E import *
from DP832 import *
import matplotlib.pyplot as plt
import numpy as np
import binascii
import PIL
import struct

def get3058Res():
    rm = visa.ResourceManager()
    for dev in rm.list_resources():
      if "DM3R" in dev:
        return dev
    return None

def getDP832Res():
    rm = visa.ResourceManager()
    for dev in rm.list_resources():
      if "DP8" in dev:
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
  print("cant get the calibrator trying DP832")
  cal = DP832Single(rm.open_resource(  getDP832Res()))


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
    #cal.write('out 0V')
    cal.setVoltage(0)

#V200mV = [ -190,-180,-170,-160,-150,-140,-130,-120,-110,-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0,
#             10,  20,  30, 40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190]

def getQSR():
  return {"qsrC":dmm.qsrC,"qsrEN":dmm.qsrEN,"qsrEV":dmm.qsrEV}

def getOSR():
  return {"osrC":dmm.osrC,"osrEN":dmm.osrEN,"osrEV":dmm.osrEV}


VDCcals = [ (0,'200mV'),(1,'2V'),(2,'20V'),(3,'200V'),(4,'1000V')]

def fixCalibration(range,maxVal,mode='VOLT:DC',rng=0):
  print("setting OUT min")
  #cal.out=0
  cal.setVoltage(0)
  print("setting range")
  dmm.range=range
  dmm.rate='F'
  print("calibrating zero")
  dmm.write("CALI:{0}:ZERO {1}".format(mode,rng))
  waitForCali()
  input("has Zero Settled?")
  print("setting OUT max")
  #cal.out=maxVal
  cal.setVoltage(maxVal)
  print("calibrating gain")
  dmm.write("CALI:{0}:GAIN {1}".format(mode,rng))
  waitForCali()
  input("has gain Settled?")


def dumpCalibration(x=""):
  dmm.write("CALI:STEP 490 {0}".format(x),deep=False)
  return dmm.inst.read_raw()

def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
    yield lst[i:i + n]

def printCalibration(tmp,first=None,last=None):
  print(binascii.hexlify(tmp[0:4]))
  for i,t in enumerate(chunks(tmp[4:],8)):
    if first is not None:
      if i<first:continue
    if last is not None:
      if i>last: break
    print("{0:6.2f}".format(struct.unpack("d",t)[0]),end=" ")
    if ((i+1)%8==0): print()

def multiCal(d,range=0,vals = np.linspace(0,.2,num=41)):
    dmm.calibrate('step 488')
    dmm.calibrate('step 487')
    speedHold = dmm.rate
    dmm.rate='F'
    dmm.range=range
    text = "{0:7s} {1:7s} {2:8s}\n".format("step", "set","after")
    for step,volt in d:
      cal.setVoltage(volt)
      dmm.calibrate("step {0}".format(step))
      dmm.calibrate("step 487")
      #input("cont>")
      time.sleep(0.1)
      tmpVal=getAverage()
      if tmpVal is None:tmpVal = 999.0
      text+="{0:7d} {1:7.5f} {2:8.5f}\n".format(step,volt,tmpVal)
      printCalibration(dumpCalibration(),8*range,8*range+7)
    plt=readBack(vals,"tmp.png",text)
    dmm.rate=speedHold

def waitForCali():
  while (int(dmm.query(":CALI:STATUS?"))):
   print(".",end='')
   time.sleep(.5)
  print()

def SaveScreen(fname):
    x = webcontrolGetGui()
    i=PIL.Image.frombuffer("1",(256,64),x)
    i.save(fname)





def cali(step,val,needPause=False):
    cal.setVoltage(val)
    cal.voltageOn()
    #cal.write("out {0}".format(val))
    #if (val == '0 OHM'):
    #    cal.write('ZCOMP 4WIRE')
    #cal.write('oper')

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

def readback(lst,range=1):
    engineering_notation.engineering_notation._exponent_lookup_scaled['-9']="E"
    dmm.range=range
    time.sleep(1) #life is to short to wait for the output to stabilize while testing this crap
    for x in lst:
        #cal.write('out {0}'.format(x))
        cal.setVoltage(x)
        #if (x == '0 OHM'):
        #    cal.write('ZCOMP 4WIRE')
        cal.voltageOn()
        #cal.write('oper')
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


def webcontrolGetGui():
    dmm.write("WEBcontrol:GUI:GET?",deep=False)
    return dmm.inst.read_raw()


def testDCVoltsShort(tSettle=5):
    return shortTest(VDC_SHORT,':MEAS:VOLT:DC',':MEAS:VOLT:DC?',tSettle)


def testDCAmpsShort(tSettle=5):
    return shortTest(ADC_SHORT,':MEAS:CURR:DC',':MEAS:CURR:DC?',tSettle)

def testResShort(tSettle=5):
    return shortTest(FRES_SHORT,':MEAS:FRES',':MEAS:FRES?',tSettle)

def fullVReadback(stabilize=5):
    engineering_notation.engineering_notation._exponent_lookup_scaled['-9']="E"
    for d in vFull:
        readback(d['vals'],":MEAS:VOLT:DC {0}".format(d['range']))
    cal.write('out 0V')

vals=np.linspace(0,.200,num=61)
def readBack(rng,fileName,unit):
    oldRate=dmm.rate
    dmm.rate='F'
    res=[]
    for i in rng:
        cal.setVoltage(i)
        cal.voltageOn()
        cal.write("*WAI")
        #cal.out="{0}{1}".format(i,unit)
        try:
          res.append(getAverage(10))
        except VisaIOError:
          res.append(None)
    fig=plt.figure()
    plt.plot(rng,res,marker='x')
    rangeMin = min([x for x in res if x is not None])
    rangeMax = max([x for x in res if x is not None])
    rangemin = rangeMin - rangeMax*.1
    rangeMax = rangeMax*1.1
    srcMin = rng[0]-rng[-1]*.1
    srcMax = rng[-1]*1.1

    plt.axis([srcMin,srcMax,rangemin,rangeMax])
    plt.text(srcMax*.6,rangeMax*.1,unit, family="monospace")
    plt.grid(True)
    plt.show(block=0)
    #plt.savefig(fileName)
    dmm.rate=oldRate
    return plt

def getAverage(itemCount=10):
    t=getVal()
    if t is None: return None
    for i in range(itemCount-1):
        x=getVal(1)
        if x is None: return None
        t+=x
    return t/itemCount

def getVal(maxTries=10):
  for i in range(maxTries):
    try:
      t = float(dmm.getVal())
      if (abs(t)>1000000):
        continue
      return t
    except VisaIOError:
      res.append(None)
  return None
