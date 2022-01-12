from helpers import *

def test_qafiro():
    row, timelines = read_single('950_qafiro.log')
    root = timelines['rootlp']  
    t = type(root)
    barrier = root.to_dict(orient='records')
    
    assert len(barrier) == 13
    
    line = barrier[0]
    assert line['PObj'] == 3.04762508e+05
    assert line['DObj'] == -6.19194374e+05
    assert line['PRes'] == 3.78e+03
    assert line['DRes'] == 3.64e+02
    assert line['Compl'] == 1.01e+06
    assert line['Time'] == 0
        
    line = barrier[12]
    assert line['PObj'] == -1.59078179e+00
    assert line['DObj'] == -1.59078179e+00
    assert line['PRes'] == 3.89e-16
    assert line['DRes'] == 1.17e-15
    assert line['Compl'] == 8.66e-12
    assert line['Time'] == 0
