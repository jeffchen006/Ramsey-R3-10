from hashlib import sha256
from pathlib import Path
import json
import shutil
import subprocess
import sys
from orbit_extend import ROOT,parse_graph6,to_graph6

K39=ROOT/'scratch/F/build/k39_exact'

def gate(path,size):
    checked=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',path,str(size),'10'],capture_output=True,text=True,check=True)
    verdict=json.loads(checked.stdout)['graphs'];assert verdict and all(entry['ok'] for entry in verdict)
    path.with_suffix('.gate').write_text(checked.stdout)

def calibrate():
    seed=Path(__file__).with_name('round1_seed39.g6');graph=parse_graph6(seed.read_text().strip());gate_seed=Path('positive39.g6');shutil.copyfile(seed,gate_seed);gate(gate_seed,39)
    Path('positive38.g6').write_text(to_graph6([row&((1<<38)-1) for row in graph[:38]])+'\n')
    subprocess.run([K39,'extall','positive38.g6','restored39.g6'],check=True)
    canon=subprocess.run([K39,'canon',seed],capture_output=True,text=True,check=True).stdout.strip();assert canon in Path('restored39.g6').read_text().splitlines();gate(Path('restored39.g6'),39)
    print('withheld known 39 restored among',len(Path('restored39.g6').read_text().splitlines()))

def run(tag):
    path=Path('../ext')/(tag+'-p1.g6')
    for order in (38,39,40):
        output=Path(tag+f'-concrete{order}.g6');subprocess.run([K39,'extall',path,output],check=True);models=output.read_text().splitlines();print(tag,order,len(models),flush=True)
        if not models:break
        gate(output,order);path=output
        if order==40:
            for model in models:
                filename=ROOT/'ralph/found'/('F_exception_'+sha256(model.encode()).hexdigest()[:16]+'.g6');filename.write_text(model+'\n')

if __name__=='__main__':calibrate() if sys.argv[1]=='control' else run(sys.argv[1])
