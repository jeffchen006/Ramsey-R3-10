"""One-time, host-weighted expansion check, including replay and archive overhead."""
from collections import Counter
from middle17 import DATA, FROZEN, HOSTS, digest, read_frozen, rows, tag


def price():
    roster=read_frozen(); prior={tag(rec) for rec in rows(DATA/'prior.jsonl')}
    checkpoint={tag(rec):rec for rec in roster if rec['phase']=='checkpoint'}
    dirs=[DATA/f'checkpoint-{worker}' for worker in range(4)]
    assert all((directory/'done').exists() for directory in dirs) and not (DATA/'STOP').exists()
    receipts=[item for directory in dirs for path in directory.glob('*.ok') for item in rows(path)]
    assert len(checkpoint)==len(receipts)==384 and set(checkpoint)=={item['key'] for item in receipts} and prior<=set(checkpoint)
    total_cpu=sum(sum(map(float,(DATA/f'checkpoint-{worker}.time').read_text().split()[:2])) for worker in range(4))
    total_cpu+=sum(map(float,(DATA/'controls.time').read_text().split()[:2]))
    own_cpu=sum(item['production']+item['replay'] for item in receipts)
    packed=sum(path.stat().st_size for directory in dirs for path in directory.glob('*.zip'))
    print('CHECKPOINT',len(receipts),'weight',sum(item['weight'] for item in receipts),'canonicalized old',len(prior),'cpu_total',total_cpu,'direct',own_cpu,'packed',packed)
    production=replay=storage=0
    for host in HOSTS:
        fresh=[item for item in receipts if item['key'] not in prior and checkpoint[item['key']]['host']==host]; assert len(fresh)==52
        count=sum(rec['host']==host and rec['phase']=='rest' for rec in roster)
        prod=sum(item['production'] for item in fresh)/len(fresh); rep=sum(item['replay'] for item in fresh)/len(fresh)
        size=sum(item['zbytes'] for item in fresh)/len(fresh)
        production+=count*prod; replay+=count*rep; storage+=count*size
        print('host',host,'remaining',count,'fresh_only_prod/replay/packed_means',round(prod,4),round(rep,4),round(size,1))
    add=production+replay; cpu_forecast=total_cpu+add*total_cpu/own_cpu+90
    zip_forecast=packed+storage*packed/sum(item['zbytes'] for item in receipts)
    scratch_forecast=zip_forecast+128*2**20
    for item in sorted(receipts,key=lambda rec:-(rec['production']+rec['replay']))[:5]:
        print('slow',item['key'],round(item['production'],4),round(item['replay'],4),item['proof_bytes'])
    print('max raw LRAT',max(item['proof_bytes'] for item in receipts),'max cnf+lrat compressed',max(item['zbytes'] for item in receipts))
    print('remaining direct CPU s prod/replay',round(production,2), round(replay,2),'full estimate core-h, packed GiB, peak GiB incl 128 MiB metadata+staging',round(cpu_forecast/3600,4),round(zip_forecast/2**30,4),round(scratch_forecast/2**30,4))
    assert cpu_forecast<4*3600 and scratch_forecast<3*2**30
    (DATA/'APPROVE').write_text(digest((FROZEN/'SHA256SUMS').read_bytes())+'\n')
    print('GO: all CP proofs twice, combined budget includes replay, no exclusions beyond individually checked IDs yet')


if __name__=='__main__':price()
