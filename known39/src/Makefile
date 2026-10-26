NAUTY = ../opt/nauty2_8_9
NSRC = $(NAUTY)/nauty.c $(NAUTY)/nautil.c $(NAUTY)/naugraph.c $(NAUTY)/schreier.c $(NAUTY)/naurng.c
CFLAGS = -O3 -march=native -fopenmp -DWORDSIZE=64 -DMAXN=WORDSIZE -DUSE_TLS -I$(NAUTY)
../bin/k39: k39.c
	mkdir -p ../bin
	gcc $(CFLAGS) -o $@.new k39.c $(NSRC) -lm && mv -f $@.new $@

