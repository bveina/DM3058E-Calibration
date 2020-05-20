import visa 
from visa import VisaIOError
#from visa import VI_ERROR_TMO
import time
from engineering_notation import EngNumber
import engineering_notation
from enum import Enum
from RigolSCPIDevice import RigolSCPIDevice

class Rigol3058E(RigolSCPIDevice):

  dmmModes={'DCV':'VOLTage:DC','ACV':
    'VOLTage:AC','DCI':'CURRent:DC','ACI':
    'CURRent:AC','2WR':'RESistance',
    'CAP':'CAPacitance','CONT':'CONTinuity','4WR':'FRESistance',
    'DIODE':'Diode','FREQ':'FREQuency','PERI':'PERiod'}
    
  def __init__(self,scpiHande):
    engineering_notation.engineering_notation._exponent_lookup_scaled['-9']="E"
    
    super(Rigol3058E,self).__init__(scpiHande)
    try:
      self.func=RigolDmmFunc.VDC
    except VisaIOError:
      print("cant set function")
  
  def reset(self):
    super(Rigol3058E,self).reset()
    self.write('CMDSET RIGOL')
    time.sleep(2)
    self.func=RigolDmmFunc.VDC
    time.sleep(1)
    # default to 200mV scale
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