"""One pole without the other three: precisely the additional eight-contact case."""
from itertools import combinations
from pathlib import Path
from id8_baskets import orbit


def main():
    seen=set();roster={};windows=orbit(127,18)
    for sites in combinations(range(18),8):
        mask=sum(1<<site for site in sites)
        if mask in seen:continue
        images=orbit(mask,18);seen.update(images)
        if all(mask & window for window in windows):roster[min(images)]=len(images)
    print('eight only, orbit reps',len(roster),'labelled',sum(roster.values()))
    lines=[f'{foot} 1 0 {foot} 0\n' for foot in sorted(roster)]
    Path('eight.request').write_text(''.join(lines));Path('eightpilot.request').write_text(''.join(lines[::59]))


if __name__=='__main__':main()
