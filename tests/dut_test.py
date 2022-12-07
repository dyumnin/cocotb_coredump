import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ReadOnly, NextTimeStep
from cocotb_bus.drivers import BusDriver
from random import randint
from cocotb_coverage.coverage import CoverCross, CoverPoint, coverage_db
from cocotb_bus.monitors import BusMonitor
import os

def sb_fn(actual_value):
    global expected_value
    # print(actual_value)
    # expected_value.pop()
    assert actual_value==expected_value.pop(0),"Error arrived"

@CoverPoint("top.a",
            xf=lambda x,y:x,
            bins=[0,1]
            )
@CoverPoint("top.b",
            xf=lambda x,y:y,
            bins=[0,1]
            )
@CoverCross("top.cross.ab",
            items=["top.a",
                   "top.b"
                   ]
            )
def xy_cover(a,b):
    pass


@CoverPoint("top.prot.a.current",  # noqa F405
            xf=lambda x: x['current'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverPoint("top.prot.a.previous",  # noqa F405
            xf=lambda x: x['previous'],
            bins=['Idle', 'Rdy', 'Txn'],
            )
@CoverCross("top.cross.a_prot.cross",
            items=["top.prot.a.previous",
                   "top.prot.a.current"
                   ],
            ign_bins=[('Rdy', 'Idle')]
            )
def x_prot_cover(txn):
    pass

@cocotb.test()
async def dut_test(dut):
    global expected_value
    expected_value=[]
    a = (0,0,1,1)
    b = (0,1,0,1)
    dut.RST_N.value = 1
    await Timer(1,'ns')
    dut.RST_N.value = 0
    await Timer(1,'ns')
    await RisingEdge(dut.CLK)
    await RisingEdge(dut.CLK)
    dut.RST_N.value = 1
    drv = InputDriver(dut,'write',dut.CLK)
    IO_Monitor(dut, 'write', dut.CLK, callback=x_prot_cover)
    drv_o=OutputDriver(dut,'read',dut.CLK,sb_fn)
    for i in range(4):
        drv.append(4,value=a[i])
        drv.append(5,value=b[i])
        drv_o.append(3)
        xy_cover(a,b)
        expected_value.append(a[i]|b[i])

    for i in range(20):
        x=randint(0,1)
        y=randint(0,1)
        drv.append(4,value=x)
        drv.append(5,value=y)
        drv_o.append(3)
        xy_cover(x,y)
        expected_value.append(x|y)
    while len(expected_value)>0:
        await Timer(2,'ns')
    
    coverage_db.report_coverage(cocotb.log.info, bins=True)
    coverage_file = os.path.join(
        os.getenv('RESULT_PATH', "./"), 'coverage.xml')
    coverage_db.export_to_xml(filename=coverage_file)

class IO_Monitor(BusMonitor):
    _signals = ['address','data','en','rdy']
    # _signals = ['rdy', 'en', 'data']

    async def _monitor_recv(self):
        fallingedge = FallingEdge(self.clock)
        rdonly = ReadOnly()
        phases = {
            0: 'Idle',
            1: 'Rdy',
            3: 'Txn'
        }
        prev = 'Idle'
        while True:
            await fallingedge
            await rdonly
            txn = (self.bus.en.value << 1) | self.bus.rdy.value
            self._recv({'previous': prev, 'current': phases[txn]})
            prev = phases[txn]

class InputDriver(BusDriver):
    _signals = ['address','data','en','rdy']

    def __init__(self, dut, name, clk):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk
    
    async def _driver_send(self, address, value, sync=True):
        if self.bus.rdy.value != 1:
            await RisingEdge(self.bus.rdy)
        self.bus.en.value = 1
        self.bus.address.value = address
        self.bus.data.value = value
        await ReadOnly()
        await RisingEdge(self.clk)
        self.bus.en.value = 0
        await NextTimeStep()

class OutputDriver(BusDriver):
    _signals = ['address','data','en','rdy']

    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.en.value = 0
        self.clk = clk
        self.callback = sb_callback
        self.append(0)
    
    async def _driver_send(self, address, sync=True):
        await RisingEdge(self.clk)
        await RisingEdge(self.clk)
        await RisingEdge(self.clk)
        while True:
            if self.bus.rdy.value != 1:
                await RisingEdge(self.bus.rdy)
            self.bus.en.value = 1
            self.bus.address.value = 3
            await ReadOnly()
            self.callback(self.bus.data.value)
            await RisingEdge(self.clk)
            await RisingEdge(self.clk)
            self.bus.en.value = 0

    # async def _driver_send(self, address, sync=True):
    #     while True:
    #         await RisingEdge(self.clk)
    #         if self.bus.rdy.value != 1:
    #             await RisingEdge(self.bus.rdy)
    #         self.bus.en.value = 1
    #         self.bus.address.value = 3
    #         await ReadOnly()
    #         self.callback(self.bus.data.value)
    #         await RisingEdge(self.clk)
    #         await NextTimeStep()
    #         self.bus.en.value = 0