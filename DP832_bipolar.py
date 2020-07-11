from abc import ABC, abstractmethod
from engineering_notation import EngNumber
from RigolSCPIDevice import RigolSCPIDevice
import visa

class VoltageSource(ABC):
  def __init__(self):
    super(VoltageSource,self).__init__()
  
  @abstractmethod
  def setVoltage(self,val):
    pass
  
  @abstractmethod	
  def voltageOn(self):
    pass
  @abstractmethod	
  def voltageOff(self):
    pass


class DP832Bipolar(RigolSCPIDevice,VoltageSource):
  # create a bipolar supply by connecting the positve lead to channel 1+ and the negative lead to channel 2+.
  #short gnd on ch1 and ch2

  def __init__(self,mySuper):
    super(DP832Bipolar,self).__init__(mySuper)
    self.oldCh1=None
    self.oldCh2=None
    
  def setVoltage(self,val):
    v1=v2 = 0
    if (val >0):
      v1 = abs(val)
      v2 = 0
    else:
      v1 = 0
      v2 = val
    if (self.oldCh1 !=v1):  
      self.write("SOURCE1:CURR .2")
      self.write("SOURCE1:VOLT {0}".format(v1))
    if (self.oldCh2 !=v2):  
      self.write("SOURCE2:CURR .2")
      self.write("SOURCE2:VOLT {0}".format(v2))
    self.oldCh1=v1
    self.oldCh2=v2
    
          
  
  def voltageOn(self):
    if self.query("OUTP? CH1",deep=False) != "ON":
      self.write("OUTP CH1,ON",deep=False)
    if self.query("OUTP? CH2",deep=False) != "ON":
      self.write("OUTP CH2,ON",deep=False)
  def voltageOff(self):
    self.write("OUTP CH1,OFF")
    self.write("OUTP CH2,OFF")
    
    
  