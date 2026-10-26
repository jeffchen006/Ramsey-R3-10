# satcore build. CaDiCaL from tools/ (commit c60730422e75, rel-3.0.1).
CAD ?= ../tools/opt/cadical
CXXFLAGS ?= -O3 -march=native -std=c++17 -Wall -DNDEBUG
all: bin/satcore bin/test_core
bin/satcore: src/satcore.cpp src/ramsey.hpp src/core.hpp
	mkdir -p bin
	$(CXX) $(CXXFLAGS) -I$(CAD)/include -o $@ src/satcore.cpp $(CAD)/lib/libcadical.a
bin/test_core: src/test_core.cpp src/core.hpp
	mkdir -p bin
	$(CXX) -O2 -g -std=c++17 -Wall -o $@ src/test_core.cpp
test: bin/test_core
	bin/test_core
clean:
	rm -f bin/satcore bin/test_core
