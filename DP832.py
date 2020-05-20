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
  
class DP832Single(RigolSCPIDevice,VoltageSource):
  def __init__(self,mySuper):
    super(DP832Single,self).__init__(mySuper)
    
  def setVoltage(self,val):
    self.write("INST CH1")
    self.write("CURR 1")
    self.write("VOLT {0}".format(val))
  
  def voltageOn(self):
    self.write("OUTP CH1,ON")
  def voltageOff(self):
    self.write("OUTP CH1,OFF")
    
    
def test():
  rm=visa.ResourceManager()
  x = rm.open_resource('USB0::0x1AB1::0x0E11::DP8C172502696::INSTR')
  return DP832Single(x) 
  