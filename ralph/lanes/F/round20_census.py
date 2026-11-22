"""Price verified one-double cuts relative to the post-pilot unsigned roster."""
from collections import defaultdict
from pathlib import Path
import sys

from one_double_pilot import BASE, count, read, reflection, reverse_count, write

OLD = BASE.parent / 'r19'
ADJ = [sum(1 << col for col in range(17) if 6 <= abs(col-site) <= 12) for site in range(17)]


def load(path):
    rows = read(path)
    assert len(set(row[:2] for row in rows)) == len(rows)
    for occ, doubled, weight in rows:
        assert 0 <= doubled <= occ < 1 << 17 and doubled & occ == doubled
        reflected = reflection(occ, 17), reflection(doubled, 17)
        assert (occ, doubled) <= reflected and weight == 1 + ((occ, doubled) != reflected)
    return set(rows)


def totals(rows):
    return len(rows), sum(row[2] for row in rows), sum(row[2] == 1 for row in rows)


def census(price):
    pool, marks = load(BASE/'widepole.left'), load(BASE/'widemark.left')
    prior, pilot, unseen = load(OLD/'pilot.checked'), load(OLD/'pilot.rows'), load('pilot.rows')
    poles, marked = load(OLD/'pole.left'), load(OLD/'mark.left')
    domain = {row for row in pool if row[1].bit_count() == 1}
    assert len(unseen) == 3581 and len(pilot) == 128 and len(prior) == 102
    assert prior <= pilot and not pilot & unseen and pilot | unseen == domain
    assert len(domain & marks) == 1050 and marks <= pool
    assert poles == pool-prior and marked == marks-prior
    print('receipt inputs partition exactly: domain, pilot, prior cuts, unseen', *map(totals,(domain,pilot,prior,unseen)))
    if not price:
        return
    fresh = load('pilot.checked'); assert fresh <= unseen
    for role, rows in [('exterior',pool),('marked',marks)]:
        for tag, bucket in [('domain',domain),('pilot',pilot),('pilot-cut',prior),('fresh',unseen),('fresh-cut',fresh),('fresh-open',unseen-fresh),('all-cut',prior|fresh),('all-open',domain-prior-fresh),('all-strata-left',pool-prior-fresh)]:
            print(role,tag,'reps labels fixed',*totals(rows & bucket))
    for tag, bucket in [('mark.left',marked-fresh),('pole.left',poles-fresh),('one-double.open',domain-prior-fresh),('new.open',unseen-fresh),('one-double.cut',prior|fresh)]:
        write(tag,sorted(bucket))
    strata = defaultdict(set)
    for row in domain:
        occ, doubled, weight = row
        strata[doubled.bit_length(),int(weight==1),occ.bit_count()+1,int(row in marks)].add(row)
    expected = {tuple(row[:4]):tuple(row[4:]) for row in read(OLD/'strata.tsv')}
    assert expected == {key:(len(bucket),len(bucket&pilot)) for key,bucket in strata.items()}
    write('strata.tsv',[(*key,len(bucket),len(bucket&pilot),len(bucket&prior),len(bucket&unseen),len(bucket&fresh),len(bucket-prior-fresh)) for key,bucket in sorted(strata.items())])
    def pairs(left,right): return count(17,10,ADJ,left,right)
    old = pairs(marked,poles); new = pairs(marked-fresh,poles-fresh)
    keys = [(mult,kind) for mult in range(3) for kind in ('labels','fixed','orbits')]
    assert [old[key] for key in keys] == [value for row in read(OLD/'joint.tsv') for value in row[4:]]
    joint = lambda result:sum(result[mult,'orbits'] for mult in range(3))
    assert joint(old) == 15613661
    assert reverse_count('mark.left','pole.left') == [new[mult,'orbits'] for mult in range(3)]
    mark_hits, pole_hits, both = pairs(marked&fresh,poles), pairs(marked,poles&fresh), pairs(marked&fresh,poles&fresh)
    assert all(old[key]-new[key] == mark_hits[key]+pole_hits[key]-both[key] for key in keys)
    fixed_shores = pairs({row for row in marked-fresh if row[2]==1},{row for row in poles-fresh if row[2]==1})
    for mult in range(3):
        assert fixed_shores[mult,'labels'] == new[mult,'fixed']
        assert 2*new[mult,'orbits'] == new[mult,'labels']+new[mult,'fixed']
    write('joint.tsv',[(mult,*[result[mult,kind] for result in (old,new,mark_hits,pole_hits,both) for kind in ('labels','fixed','orbits')]) for mult in range(3)])
    print('net reduction',joint(old)-joint(new),'from',joint(old),'to',joint(new))
    print('marked + exterior - overlap = net',*map(joint,(mark_hits,pole_hits,both)))
    groups = sorted({row[1].bit_count() for row in poles-fresh})
    for doubles in groups:
        print('all-strata-left by double count',doubles,'exterior, marked',*[totals({row for row in role-fresh if row[1].bit_count()==doubles}) for role in (poles,marked)])


if __name__ == '__main__':
    assert sys.argv[1] in ('preflight','price'); census(sys.argv[1]=='price')
