import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ReadOnly, NextTimeStep
from cocotb_bus.drivers import BusDriver


def sb_fn(actual_value):
    global expected_value
    print(expected_value)
    print(actual_value)
    # expected_value.pop()
    assert actual_value==expected_value.pop(0),"Error arrived"


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
    drv_o=OutputDriver(dut,'read',dut.CLK,sb_fn)
    for i in range(4):
        drv.append(4,value=a[i])
        drv.append(5,value=b[i])
        drv_o.append(3)
        expected_value.append(a[i]|b[i])

    while len(expected_value)>0:
        await Timer(2,'ns')


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
            await NextTimeStep()