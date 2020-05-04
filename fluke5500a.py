import time
from visa import VisaIOError 
 
class Fluke5500A():

  def __init__(self,mySuper):
    self.inst = mySuper
  
  def write(self,s):
    if self.inst is not None:
      return self.inst.write(s)
    return None
  
  def read(self):
    if self.inst is not None:
      return self.inst.read()
    return None
   
  def query(self,s):
    if self.inst is not None:
      return self.inst.query(s)
    return None
  
  def setVoltsDC(self,val,wait=True,forceOn=False):
    self.out('{0}V'.format(val),wait,forceOn)
  
  
  @property
  def out(self):
    tmp = self.query('out?')
    tmp = tmp.strip().split(',')
    tmp[0]=float(tmp[0])
    tmp[2]=float(tmp[2])
    tmp[4]=float(tmp[4])
    return tmp
    
  @out.setter            
  def out(self,s,wait=True,forceOn=True):
    self.write("out {0}".format(s))
    while forceOn and not self.oper:
      self.clearErrorList()
      self.write("oper")
      time.sleep(1)
    
    while wait and not self.outputSettled:
      time.sleep(.1)
    
      
    
  def clearErrorList(self):
    t= self.err
    while t[0]!=0:
      print(t)
      t= self.err
        
  
  @property            
  def oper(self):
    result = self.query('OPER?')
    if (result is None): return True 
    return int(result)==1
  
  @oper.setter
  def oper(self,val):
    if val:
      return self.write('oper')
    else:
      return self.write('stby')
  @property
  def err(self):
    result = self.query("ERR?") 
    if (result is None): return [0]
    tmp = result.strip().split(',')
    tmp[0]=int(tmp[0])
    return tmp
  
  @property
  def isr(self):
    result = self.query("ISR?")
    if result is None: #fake a settled output
      return Fluke5500A.parseISR(1<<12)
    tmp = int(result)
    return Fluke5500A.parseISR(tmp)
    
  @property
  def esr(self):
    result = self.query("ESR?")
    if result is None: return Fluke5500A.parseESR(0)
    tmp = int(result)
    return Fluke5500A.parseESR(tmp)
  
  @property
  def stb(self):
    result = self.query("ESR?")
    if result is None: return Fluke5500A.parseESR(0)
    tmp = int(result)
    return Fluke5500A.parseSTB(tmp)
  
  @property  
  def stby(self):
    self.write('STBY')
  
  @property  
  def outputSettled(self):
    return "SETTLED" in self.isr
  
  def parseGeneric(val,data):
    res=[]
    for b,s in data.items():
      if val&(1<<b)!=0:
        res.append(s)
    return res
    
  def parseISR(val):
    bits = {
      13:'RPTBUSY', 12:'SETTLED', 11:'REMOTE', 9:'UUTBFUL',
      8:'UUTDATA', 7:'HIVOLT', 6:'MAGCHG', 5:'TMPCAL',
      3:'IBOOST', 2:'VBOOST', 0:'OPER'
    }
    return Fluke5500A.parseGeneric(val,bits)

  def parseESR(val):
    bits = {
        7:'PON',5:'CME',4:'EXE',3:'DDE',2:'QYE',0:'OPC'
    }
    return Fluke5500A.parseGeneric(val,bits)

  
  def parseSTB(val):
    bits = {
        6:'RQS/MSS',5:'ESB',4:'MAV',3:'EAV',2:'ISCB'
    }
    return Fluke5500A.parseGeneric(val,bits)
