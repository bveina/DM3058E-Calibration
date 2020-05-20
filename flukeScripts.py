              

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
                
