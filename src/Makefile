####################################################################
# Build the two custom C-Mod FORTRAN libraries that MDSplus dlopen()s
# while evaluating expressions in C-Mod trees.
#
# Derived from the per-library Makefiles in MIT PSFC's fdp-cmod repo
# (see LICENSE.mit and README.md). Three changes make them portable
# off the author's Ubuntu 24.04 / gfortran 13 box:
#
#   1. `-fallow-argument-mismatch` is dropped. It only exists in
#      gfortran >= 10, where cross-file argument mismatches became a
#      hard error; on gfortran 8/9 it is an unrecognized option and
#      the mismatch is only a warning anyway. Add it back conditionally
#      below rather than unconditionally, so both eras compile.
#   2. The gfortran library directory was hardcoded to
#      /usr/lib/gcc/x86_64-linux-gnu/13, and the libs were linked with bare
#      `ld`. Link through the compiler driver instead, which knows where its
#      own runtime lives on any box.
#   3. The imsl objects were compiled without -fPIC, which happens to
#      work only when the linker can relax the relocations. Everything
#      that goes into a shared object is built -fPIC here.
#
# MDSPLUS_DIR must point at a prefix with include/mdslib.inc and
# lib/libMdsLib.so (i.e. $PREFIX in a conda build, or $CONDA_PREFIX).
####################################################################

# EXTRA_FFLAGS / EXTRA_LDFLAGS exist so a conda build can append its
# --sysroot without this file having to know about conda. FFLAGS itself is
# assigned with `=` (not `?=`) on purpose: these 2002-era sources need this
# exact flag set, so an inherited FFLAGS from the environment must not
# silently replace it.
MDSPLUS_DIR ?= $(CONDA_PREFIX)
PREFIX      ?= $(CONDA_PREFIX)
EXTRA_FFLAGS  ?=
EXTRA_LDFLAGS ?=

# `F77 ?= gfortran` would NOT work: make ships a builtin default of `f77`,
# whose origin is `default` rather than `undefined`, so ?= never fires.
# Guard on the origin instead, which still honours a command-line or
# environment override (conda's build env sets F77 to the pinned gfortran).
ifeq ($(origin F77),default)
F77 := gfortran
endif
BUILD = build

# gfortran >= 10 turns cross-file argument mismatches into errors; the
# 2002-era sources trip that all over. Only pass the flag if supported.
ARGMISMATCH := $(shell $(F77) -fallow-argument-mismatch -fsyntax-only -xf95 /dev/null \
                 >/dev/null 2>&1 && echo -fallow-argument-mismatch)

FFLAGS = -c -g -O3 -ffloat-store -funroll-loops -fPIC -fno-automatic \
         -w -fno-backslash -fno-range-check $(ARGMISMATCH) $(EXTRA_FFLAGS)

# Linking goes through the compiler driver rather than bare `ld` (which is
# what the upstream Makefiles used). The driver pulls in the right
# libgfortran/libquadmath/libgcc_s for whichever gfortran is in use, and in
# a conda build it applies --sysroot -- so the artifact doesn't pick up the
# build machine's glibc and end up over-constrained the way ga-dfl-labeler
# did. Verified that --defsym aliases still land in .dynsym this way.
#
# -rpath $ORIGIN so libHYBEXE.so finds libMdsLib.so sitting beside it in
# $PREFIX/lib. The upstream build relied on the process having already
# loaded libMdsLib, or on LD_LIBRARY_PATH; neither is guaranteed when
# MDSplus dlopen()s us out of an arbitrary process.
LDFLAGS = -shared -Wl,-rpath,'$$ORIGIN' $(EXTRA_LDFLAGS)

IMSL_OBJS   = $(addprefix $(BUILD)/,murrv.o mrrrr.o muzrv.o mrrzz.o imsl_int.o)
HYBEXE_OBJS = $(addprefix $(BUILD)/,hybrid_get_p_to_v.o get_input_p_to_v_int.o)

# MDSplus calls these by their UPPERCASE names (IMAGE->ROUTINE in the tree
# expressions); gfortran emits lowercase-with-underscore. Alias them.
IMSL_ENTRIES   = -Wl,--defsym,MURRV=murrv_ -Wl,--defsym,MRRRR=mrrrr_ \
                 -Wl,--defsym,MUZRV=muzrv_ -Wl,--defsym,MRRZZ=mrrzz_
HYBEXE_ENTRIES = -Wl,--defsym,GET_INPUT_P_TO_V=get_input_p_to_v

.PHONY: all clean install
all: $(BUILD)/libIMSL.so $(BUILD)/libHYBEXE.so $(BUILD)/libMMUL.so

$(BUILD):
	mkdir -p $(BUILD)

# --- IMSL (no MDSplus dependency) ------------------------------------
$(BUILD)/%.o: imsl/%.f | $(BUILD)
	$(F77) $(FFLAGS) -o $@ $<

# imsl_int.f is the uppercase-entry-point shim; it must not be mangled.
$(BUILD)/imsl_int.o: imsl/imsl_int.f | $(BUILD)
	$(F77) $(FFLAGS) -fno-underscoring -o $@ $<

$(BUILD)/libIMSL.so: $(IMSL_OBJS)
	$(F77) $(LDFLAGS) -o $@ $^ $(IMSL_ENTRIES)

# C-Mod expressions reference MMUL more often than IMSL; same library.
$(BUILD)/libMMUL.so: $(BUILD)/libIMSL.so
	ln -sf libIMSL.so $@

# --- HYBEXE (needs mdslib.inc and libMdsLib) --------------------------
$(BUILD)/hybrid_get_p_to_v.o: hybexe/hybrid_get_p_to_v.F | $(BUILD)
	$(F77) $(FFLAGS) -I$(MDSPLUS_DIR)/include -o $@ $<

# Same story as imsl_int.f: this one provides GET_INPUT_P_TO_V.
$(BUILD)/get_input_p_to_v_int.o: hybexe/get_input_p_to_v_int.f | $(BUILD)
	$(F77) $(FFLAGS) -fno-underscoring -I$(MDSPLUS_DIR)/include -o $@ $<

$(BUILD)/libHYBEXE.so: $(HYBEXE_OBJS)
	$(F77) $(LDFLAGS) -o $@ $^ \
	    -L$(MDSPLUS_DIR)/lib -lMdsLib $(HYBEXE_ENTRIES)

# --- install ----------------------------------------------------------
# $PREFIX/tdi is exactly where fdp points MDS_PATH (it hardcodes
# env_dir/"tdi"), and $PREFIX/lib is reachable from MDSplus's bare
# dlopen("libHYBEXE.so") via libMdsShr's RPATH $ORIGIN. So this layout
# needs no environment variables and no changes to fdp.
install: all
	mkdir -p $(PREFIX)/lib $(PREFIX)/tdi
	cp $(BUILD)/libIMSL.so $(BUILD)/libHYBEXE.so $(PREFIX)/lib/
	ln -sf libIMSL.so $(PREFIX)/lib/libMMUL.so
	cp tdi/*.fun tdi/*.py $(PREFIX)/tdi/

clean:
	rm -rf $(BUILD)
