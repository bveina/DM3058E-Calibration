import visa 
from visa import VisaIOError
#from visa import VI_ERROR_TMO
import time
from engineering_notation import EngNumber
import engineering_notation
from enum import Enum

class Rigol3058E():

  dmmModes={'DCV':'VOLTage:DC','ACV':
    'VOLTage:AC','DCI':'CURRent:DC','ACI':
    'CURRent:AC','2WR':'RESistance',
    'CAP':'CAPacitance','CONT':'CONTinuity','4WR':'FRESistance',
    'DIODE':'Diode','FREQ':'FREQuency','PERI':'PERiod'}
  def __init__(self,mySuper):
    engineering_notation.engineering_notation._exponent_lookup_scaled['-9']="E"
    self.inst = mySuper
    try:
      self.func=RigolDmmFunc.VDC
    except VisaIOError:
      print("cant set function")
    
    
  def write(self,s,deep=True):
    if deep:
      return self.brvWrite(s)
    else:
      return self.inst.write(s)
  
  def read(self):
    try:
      return self.inst.read()
    except:
      return None
      
  def query(self,s,deep=True):
    if deep:
      return self.brvQuery(s)
    else:
      return self.inst.query(s)
  
  def reset(self):
    self.write('*RST',deep=False)
    self.write('CMDSET RIGOL')
    time.sleep(2)
    self.func=RigolDmmFunc.VDC
    time.sleep(1)
    self.write(':MEAS:VOLT:DC 0')
  
  @property
  def range(self):
    tmp = self.query(
    ":MEAS:{0}:RANGE?".format(Rigol3058E.dmmModes[self.internalFunction]),deep=False)
    return tmp
    
  @range.setter
  def range(self,val):
    self.write(
    ":MEAS:{0} {1}".format(Rigol3058E.dmmModes[self.internalFunction],val),deep=False)
    
  
  @property
  def err(self):
    tmp = self.query(":SYSTEM:ERROR?",deep=False).strip()
    tmp = tmp.split(',')
    tmp[0]=int(tmp[0])
    return tmp
  
  def brvWrite(self,val):
    t=""
    try:
      t=self.write(val,deep=False)
    except VisaIOError:
      print("VISAIOERROR")
    x = self.err
    if (x[0] !=0): print("ERROR:",x)
    self.write("*CLS",deep=False)
    return t
    
  def brvQuery(self,val):
    t=""
    try:
        t=self.query(val,deep=False)
    except VisaIOError:
      print("VISAIOERROR")
    print("ERROR:",self.err)    
    self.write("*CLS",deep=False)
    return t
    
  
  def getVal(self):
    tmp = self.query(":MEASure:{0}?".format(Rigol3058E.dmmModes[self.internalFunction]),deep=False)
    return tmp
    
  @property
  def func(self):
    return self.query(":FUNC?")
   
  @func.setter
  def func(self,val):
    #is enum?
    if isinstance(val, Enum):
      val=val.value
    
    if val not in Rigol3058E.dmmModes.keys():
      raise ValueError("cant find DMM mode: {0}".format(val))
    
    tmp = self.write(':FUNCtion:{0}'.format(Rigol3058E.dmmModes[val]))
    if tmp[1] == visa.constants.StatusCode.success: self.internalFunction=val
    return tmp
    
  @property
  def qsrC(self):
    tmp = int(self.query(":STATUS:QUES:COND?",deep=False))
    return Rigol3058E.parseQSR(tmp)
    
  @property
  def qsrEV(self):
    tmp = int(self.query(":STATUS:QUES:EVENT?",deep=False))
    return Rigol3058E.parseQSR(tmp) 

  @property
  def qsrEN(self):
    tmp = int(self.query(":STATUS:QUES:ENABLE?",deep=False))
    return Rigol3058E.parseQSR(tmp)
  
  @property
  def esrEN(self):
    tmp = int(self.query(":STATUS:QUES:ENABLE?",deep=False))
    return Rigol3058E.parseQSR(tmp)
  
  
  @property
  def esrEV(self):
    tmp = int(self.query(":STATUS:QUES:ENABLE?",deep=False))
    return Rigol3058E.parseQSR(tmp)
  
  
  
  @property
  def osrC(self):
    tmp = int(self.query(":STATUS:OPER:COND?",deep=False))
    return Rigol3058E.parseOSR(tmp)
  
  @property
  def osrEV(self):
    tmp = int(self.query(":STATUS:OPER:EVENT?",deep=False))
    return Rigol3058E.parseOSR(tmp)
  
  @property
  def osrEN(self):
    tmp = int(self.query(":STATUS:OPER:ENABLE?",deep=False))
    return Rigol3058E.parseOSR(tmp)
  
  def calibrate(self,step):
    try:
      if ("step" in step):
        tmp = self.query(':CALI:{0}'.format(step),deep=False)
      else:
        tmp = self.write(':CALI:{0}'.format(step))
      print(tmp)
    except VisaIOError:
      print("im sorry dave, im afraid i cant do that")
      return

    while (int(self.query(":CALI:STATUS?",deep=False))):
      print('.',end='')
      time.sleep(.5)
      
    
    
  
  def parseQSR(val):
    bits = {
        0:'VOLT',1:'CURR',2:'TIME',4:'TEMP',5:'FREQ',8:'CAL',9:'RES',10:'CAP',11:'LLIM',12:'ULIM',14:'MEM'
    }
    return Rigol3058E.parseGeneric(val,bits)

  def parseOSR(val):
    bits = {
        4:'MEAS',5:'TRIG',8:'CONF',9:'MTHR',10:'LOCK'
    }
    return Rigol3058E.parseGeneric(val,bits)


  def parseESR(val):
    bits = {0:'OPC',2:'QYE',3:'DDE',4:'EXE',5:'CME',7:'PON'}
    return Rigol3058E.parseGeneric(val,bits)

  
  def parseGeneric(val,data):
    res=[]
    for b,s in data.items():
      if val&(1<<b)!=0:
        res.append(s)
    return res
    
class RigolDmmFunc(Enum):
  VDC = 'DCV'
  VAC = 'ACV'
  ADC = 'DCI'
  AAC = 'ACI'
  RES = '2WR'
  FRES= '4WR'
  CAP = 'CAP'
  CONT= 'CONT'
  DIODE='DIODE'
  FREQ='FREQ'
  PER='PERI'

def testFunc(dmm):
  for f in RigolDmmFunc:
    dmm.func=f
    time.sleep(1)
    print("set:{0:20} rec:{1:20}".format(f.value,dmm.func))