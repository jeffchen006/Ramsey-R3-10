import fcntl
import json
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];NEW=ROOT/'scratch/D/m14r23';WING=ROOT/'scratch/D/c6r23/wing';DEPOSIT=4100000000;LIMIT=11500000000


def transfer():
    while True:
        with (NEW/'staging.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);saved=int((NEW/'accounted.bytes').read_text());pending=sum(int(path.read_text()) for path in NEW.glob('reserve.*'))
            if saved+pending+DEPOSIT<=LIMIT:
                (NEW/'reserve.ALLOWANCE_TRANSFER_ONLY').write_text(str(DEPOSIT));note=dict(old_new_slot_envelope=LIMIT,virtual_transfer=DEPOSIT,physical_main_cap=LIMIT-DEPOSIT,charged_at_grant=saved,outstanding_at_grant=pending,wing_cap=4800000000,prior_wing_cap=740000000);(WING/'go_large').write_text(json.dumps(note)+'\n');print(note,flush=True);return
        time.sleep(1)


if __name__=='__main__':transfer()
