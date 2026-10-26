// C++ version of sms/lratlog2lrat.py (same outputs, streaming, two passes over the log).
// Usage: lratlog2lrat INPUT.cnf PROOF.log OUT_PREFIX
// OUT.cnf: all original clauses (input + external) in solver order; OUT.lrat: ASCII LRAT over OUT.cnf;
// OUT.ext: "ID lit... 0" for clauses of OUT.cnf not in INPUT.cnf (multiset match).
// Deletions of weakened clauses are skipped (CaDiCaL may restore them).
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>

using std::vector;

struct VecHash {
  size_t operator()(const vector<int> &v) const {
    size_t h = 1469598103934665603ULL;
    for (int x : v) { h ^= (size_t)(int64_t)x; h *= 1099511628211ULL; }
    return h;
  }
};

static char *line = nullptr;
static size_t cap = 0;

static bool readline(FILE *f) { return getline(&line, &cap, f) != -1; }

// fast output: put signed / unsigned decimal with a leading space (or not)
static inline void putu(FILE *f, uint64_t x) {
  char b[24]; int i = 24;
  do { b[--i] = '0' + x % 10; x /= 10; } while (x);
  fwrite_unlocked(b + i, 1, 24 - i, f);
}
static inline void puti(FILE *f, int64_t x) {
  if (x < 0) { fputc_unlocked('-', f); putu(f, (uint64_t)(-x)); } else putu(f, (uint64_t)x);
}
// fast parse: skip spaces, read signed integer; returns false at end of line
static inline bool geti(char *&p, int64_t &x) {
  while (*p == ' ') p++;
  if (*p == '\n' || *p == 0) return false;
  bool neg = false;
  if (*p == '-') { neg = true; p++; }
  uint64_t v = 0;
  while (*p >= '0' && *p <= '9') v = v * 10 + (*p++ - '0');
  x = neg ? -(int64_t)v : (int64_t)v;
  return true;
}

int main(int argc, char **argv) {
  if (argc != 4) { fprintf(stderr, "usage: %s INPUT.cnf PROOF.log OUT_PREFIX\n", argv[0]); return 2; }
  std::string out = argv[3];
  // input multiset
  std::unordered_map<vector<int>, int, VecHash> inputs;
  {
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror("input"); return 2; }
    vector<int> cur;
    while (readline(f)) {
      if (line[0] == 'c' || line[0] == 'p') continue;
      char *p = line, *e;
      while (true) {
        long x = strtol(p, &e, 10);
        if (e == p) break;
        p = e;
        if (x == 0) { std::sort(cur.begin(), cur.end()); inputs[cur]++; cur.clear(); }
        else cur.push_back((int)x);
      }
    }
    fclose(f);
  }
  // pass 1: originals -> OUT.cnf (body to temp, header later), OUT.ext
  FILE *log = fopen(argv[2], "r");
  if (!log) { perror("log"); return 2; }
  std::string cnfBody = out + ".cnf.body";
  FILE *cb = fopen(cnfBody.c_str(), "w");
  FILE *ext = fopen((out + ".ext").c_str(), "w");
  setvbuf(cb, nullptr, _IOFBF, 1 << 24);
  uint64_t N = 0, nExt = 0;
  int maxvar = 0;
  vector<int> lits;
  while (readline(log)) {
    if (line[0] != 'o') continue;
    char *p = line + 2, *e;
    strtoull(p, &e, 10); p = e;
    lits.clear();
    while (true) {
      long x = strtol(p, &e, 10);
      if (e == p || x == 0) break;
      p = e; lits.push_back((int)x); maxvar = std::max(maxvar, abs((int)x));
    }
    N++;
    for (int l : lits) fprintf(cb, "%d ", l);
    fputs("0\n", cb);
    vector<int> key = lits; std::sort(key.begin(), key.end());
    auto it = inputs.find(key);
    if (it != inputs.end() && it->second > 0) it->second--;
    else {
      nExt++;
      fprintf(ext, "%lu", (unsigned long)N);
      for (int l : lits) fprintf(ext, " %d", l);
      fputs(" 0\n", ext);
    }
  }
  fclose(cb); fclose(ext);
  {
    FILE *g = fopen((out + ".cnf").c_str(), "w");
    fprintf(g, "p cnf %d %lu\n", maxvar, (unsigned long)N);
    FILE *b = fopen(cnfBody.c_str(), "r");
    char buf[1 << 16]; size_t r;
    while ((r = fread(buf, 1, sizeof buf, b)) > 0) fwrite(buf, 1, r, g);
    fclose(b); fclose(g); remove(cnfBody.c_str());
  }
  uint64_t unmatched = 0;
  for (auto &kv : inputs) unmatched += kv.second;
  // pass 2: proof
  rewind(log);
  FILE *lr = fopen((out + ".lrat").c_str(), "w");
  setvbuf(lr, nullptr, _IOFBF, 1 << 24);
  std::unordered_map<uint64_t, uint64_t> newid; // live clauses only
  newid.reserve(1 << 22);
  std::unordered_set<uint64_t> weakened;
  uint64_t origCnt = 0, nxt = N, last = N;
  int status = 0;
  while (readline(log)) {
    char c = line[0];
    char *p = line + 2, *e;
    if (c == 'o') {
      uint64_t id = strtoull(p, &e, 10);
      newid[id] = ++origCnt;
    } else if (c == 'a') {
      int64_t x;
      geti(p, x);
      uint64_t id = (uint64_t)x;
      nxt++;
      putu(lr, nxt);
      while (geti(p, x) && x != 0) { fputc_unlocked(' ', lr); puti(lr, x); }
      fputs_unlocked(" 0", lr);
      while (geti(p, x) && x != 0) {
        auto it = newid.find((uint64_t)x);
        if (it == newid.end()) { fprintf(stderr, "hint %lu not live\n", (unsigned long)x); return 1; }
        fputc_unlocked(' ', lr); putu(lr, it->second);
      }
      fputs_unlocked(" 0\n", lr);
      newid[id] = nxt; last = nxt;
    } else if (c == 'd') {
      uint64_t id = strtoull(p, &e, 10);
      if (weakened.count(id)) continue;
      auto it = newid.find(id);
      if (it == newid.end()) { fprintf(stderr, "delete of unknown %lu\n", (unsigned long)id); return 1; }
      putu(lr, last); fputs_unlocked(" d ", lr); putu(lr, it->second); fputs_unlocked(" 0\n", lr);
      newid.erase(it);
    } else if (c == 'w') {
      weakened.insert(strtoull(p, &e, 10));
    } else if (c == 'r') {
      uint64_t id = strtoull(p, &e, 10);
      if (!newid.count(id)) { fprintf(stderr, "restored clause %lu not live\n", (unsigned long)id); return 1; }
    } else if (c == 's') {
      status = atoi(p);
    }
  }
  fclose(lr); fclose(log);
  printf("originals=%lu input_unmatched=%lu external=%lu derived=%lu status=%d\n", (unsigned long)N,
         (unsigned long)unmatched, (unsigned long)nExt, (unsigned long)(nxt - N), status);
  return 0;
}
