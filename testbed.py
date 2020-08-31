import visa
import time
from engineering_notation import EngNumber
import engineering_notation
from fluke5500a import Fluke5500A
from Rigol3058E import *
from DP832_bipolar import *
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

def getMSO5000Res():
    rm = visa.ResourceManager()
    for dev in rm.list_resources():
      if "MS5" in dev:
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





def ScopeScreen(scope,name,blockSize=4096):
    # TODO: write a generic SCPI get raw TMC response.

    scope.write("DISP:DATA?",deep=False)
    # need to parse the TMC header to find out how many bytes need to be ready
    # this is a candidate for refactoring. this will hardly be the last time i
    # find a TMC header (TMC stands fro Test Measurment and Control)
    # format '#Nxxxxxxxxx'
    # '#' is the start indicator for a TMC header
    # N is the number of bytes in the TMC header left to read
    # xxxx is a decimal number giving the length of the data to follow.
    tmcSizeStr = scope.inst.read_bytes(2)
    #todo: throw an exception if the first character is not a '#'
    tmcSize=int(tmcSizeStr[1:])
    byteCount = int(scope.inst.read_bytes(tmcSize))
    x=scope.inst.read_bytes(byteCount,blockSize)
    with open(name,'wb') as f:
     f.write(x)


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


def main():
  global rm,dmm,cal,scope
  rm = visa.ResourceManager()
  print( 'got RM')
  time.sleep(1)
  print('getting DMM')
  
  dmm = None
  try:
    dmmConnect()
  except:
    print("Cant get the DMM")
  
  

  print('getting calibrator')
  cal=None
  try:
    cal = Fluke5500A(rm.open_resource('GPIB0::5::INSTR'))
    print("got fluke5500a")
  except:
    print("cant get the Fluke Calibrator ")
  
  if cal is None:
    try:
      cal = DP832Bipolar(rm.open_resource(  getDP832Res()))
      print("got DP832")
    except:
      print("cant find a calibrator.")
  
  if cal is None:
    print("couldent find any calibrators. giving up on that.")
    
  
  print('getting Scope')
  scope = None
  try:
    scope = RigolSCPIDevice(rm.open_resource(getMSO5000Res()))
    print("got MSO5000")
  except:
    print("couldent find any scopes. giving up on that.")
    scope = RigolSCPIDevice(None)



if __name__ == "__main__":
  main()
