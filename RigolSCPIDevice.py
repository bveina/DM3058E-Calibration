
from visa import VisaIOError

class RigolSCPIDevice:
  qsrBits = {0:'VOLT', 1:'CURR', 2:'TIME', 4:'TEMP', 5:'FREQ', 8:'CAL', 9:'RES', 10:'CAP', 11:'LLIM', 12:'ULIM', 14:'MEM'}
  osrBits = {4:'MEAS', 5:'TRIG', 8:'CONF', 9:'MTHR', 10:'LOCK'}
  esrBits = {0:'OPC', 2:'QYE', 3:'DDE', 4:'EXE', 5:'CME', 7:'PON'}
 

  def __init__(self,scpiHandle):
    self.inst = scpiHandle
    # default timeout is a little short for resets and other things
    self.inst.timeout=10000 

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
  
  def reset(self):
    self.write("*RST",deep=False)
  
  @property
  def err(self):
    tmp = self.query(":SYSTEM:ERROR?",deep=False).strip()
    tmp = tmp.split(',')
    tmp[0]=int(tmp[0])
    return tmp
    
  @property
  def qsrC(self):
    tmp = int(self.query(":STATUS:QUES:COND?",deep=False))
    return RigolSCPIDevice.parseQSR(tmp)
    
  @property
  def qsrEV(self):
    tmp = int(self.query(":STATUS:QUES:EVENT?",deep=False))
    return Rigol3058E.parseQSR(tmp) 

  @property
  def qsrEN(self):
    tmp = int(self.query(":STATUS:QUES:ENABLE?",deep=False))
    return RigolSCPIDevice.parseQSR(tmp)
  
  @property
  def esrEN(self):
    tmp = int(self.query(":STATUS:QUES:ENABLE?",deep=False))
    return RigolSCPIDevice.parseQSR(tmp)
  
  @property
  def esrEV(self):
    tmp = int(self.query(":STATUS:QUES:ENABLE?",deep=False))
    return RigolSCPIDevice.parseQSR(tmp)
  
  @property
  def osrC(self):
    tmp = int(self.query(":STATUS:OPER:COND?",deep=False))
    return RigolSCPIDevice.parseOSR(tmp)
  
  @property
  def osrEV(self):
    tmp = int(self.query(":STATUS:OPER:EVENT?",deep=False))
    return RigolSCPIDevice.parseOSR(tmp)
  
  @property
  def osrEN(self):
    tmp = int(self.query(":STATUS:OPER:ENABLE?",deep=False))
    return RigolSCPIDevice.parseOSR(tmp)
  
  def parseQSR(val):    
    return RigolSCPIDevice.parseGeneric(val,sqrBits)

  def parseOSR(val):
    return RigolSCPIDevice.parseGeneric(val,osrBits)

  def parseESR(val):    
    return RigolSCPIDevice.parseGeneric(val,esrBits)
  
  def parseGeneric(val,data):
    res=[]
    for b,s in data.items():
      if val&(1<<b)!=0:
        res.append(s)
    return res
  