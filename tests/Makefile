SIM ?= icarus
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../hdl/dut.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO1.v
VERILOG_SOURCES += $(PWD)/../hdl/FIFO2.v
VERILOG_SOURCES += $(PWD)/../wrapper/wrapper.v
TOPLEVEL = wrapper
MODULE = dut_test
include $(shell cocotb-config --makefiles)/Makefile.sim
