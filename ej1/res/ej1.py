from nmigen import *
from nmigen_cocotb import run
import cocotb
from cocotb.triggers import RisingEdge, Timer
from cocotb.clock import Clock
from random import getrandbits


class Stream(Record):
    def __init__(self, width, **kwargs):
        Record.__init__(self, [('data', width), ('valid', 1), ('ready', 1)], **kwargs)

    def accepted(self):
        return self.valid & self.ready

    class Driver:
        def __init__(self, clk, dut, prefix):
            self.clk = clk
            self.data = getattr(dut, prefix + 'data')
            self.valid = getattr(dut, prefix + 'valid')
            self.ready = getattr(dut, prefix + 'ready')

        async def send(self, data):
            self.valid <= 1
            for d in data:
                self.data <= d
                await RisingEdge(self.clk)
                while self.ready.value == 0:
                    await RisingEdge(self.clk)
            self.valid <= 0

        async def recv(self, count):
            self.ready <= 1
            data = []
            for _ in range(count):
                await RisingEdge(self.clk)
                while self.valid.value == 0:
                    await RisingEdge(self.clk)
                data.append(self.data.value.integer)
            self.ready <= 0
            return data


class Sumador(Elaboratable):
    def __init__(self, width):
        self.a = Stream(width, name='a')
        self.b = Stream(width, name='b')
        self.r = Stream(width+1, name='r')
        self.rst = Signal(1)

    def elaborate(self, platform):
        m = Module()
        sync = m.d.sync
        comb = m.d.comb

        with m.If(self.a.accepted() & self.b.accepted()):
            sync += [
                self.r.valid.eq(1),
                self.r.data.eq(self.a.data + self.b.data)
            ]

        with m.If(self.rst == 1):
            sync += self.r.data.eq(0)
            sync += self.r.data.eq(0)

        comb += self.a.ready.eq(self.r.ready)
        comb += self.b.ready.eq(self.r.ready)
        return m


async def init_test(dut):
    cocotb.fork(Clock(dut.clk, 10, 'ns').start())
    dut.rst <= 1
    for _ in range(3):
        await RisingEdge(dut.clk)
    dut.rst <= 0


@cocotb.test()
async def random(dut):
    """ Verfica la suma de 100 pares de numeros aleatorios en condiciones normales """
    await init_test(dut)

    stream_inputa = Stream.Driver(dut.clk, dut, 'a__')
    stream_inputb = Stream.Driver(dut.clk, dut, 'b__')
    stream_output = Stream.Driver(dut.clk, dut, 'r__')

    N = 100
    width = len(dut.a__data)
    mask = int('1' * (width+1), 2)

    data_a = [getrandbits(width) for _ in range(N)]
    data_b = [getrandbits(width) for _ in range(N)]
    expected = [(data_a[i]+data_b[i]) & mask for i in range(N)]
    cocotb.fork(stream_inputa.send(data_a))
    cocotb.fork(stream_inputb.send(data_b))
    

    recved = await stream_output.recv(N)
    assert recved == expected
    

@cocotb.test()
async def reset(dut):
    """ Verfica que las señales data y valid sean 0 en caso de que la entrada sea 0 """
    await init_test(dut)

    stream_inputa = Stream.Driver(dut.clk, dut, 'a__')
    stream_inputb = Stream.Driver(dut.clk, dut, 'b__')
    stream_output = Stream.Driver(dut.clk, dut, 'r__')

    N = 20
    width = len(dut.a__data)
    mask = int('1' * (width+1), 2)


    stream_inputa.valid <= 1
    stream_inputb.valid <= 1
    for _ in range(N):
        dut.rst <= 1
        await RisingEdge(dut.clk)
        assert stream_output.valid.value == 0
        assert stream_output.data.value.integer == 0
    dut.rst <= 0
    
@cocotb.test()
async def notReady(dut):
    """ Verfica que las señales data y valid sean 0 en caso de que la señal ready de la salida no esté en 1 """
    await init_test(dut)

    stream_inputa = Stream.Driver(dut.clk, dut, 'a__')
    stream_inputb = Stream.Driver(dut.clk, dut, 'b__')
    stream_output = Stream.Driver(dut.clk, dut, 'r__')

    N = 20
    width = len(dut.a__data)
    mask = int('1' * (width+1), 2)


    data_a = [getrandbits(width) for _ in range(N)]
    data_b = [getrandbits(width) for _ in range(N)]
    stream_inputa.valid <= 1
    stream_inputb.valid <= 1
    for i in range(N):
        dut.rst <= 0
        stream_inputa.data <= data_a[i]
        stream_inputb.data <= data_b[i]
        stream_output.ready <= 0
        await RisingEdge(dut.clk)
        assert stream_output.valid.value == 0
        assert stream_output.data.value.integer == 0


@cocotb.coroutine
async def feedInputs(driver, data, dut):
    for d in data:
        driver.data <= d
        await RisingEdge(dut.clk)


@cocotb.test()
async def notValid(dut):
    """ Verfica que las señales data y valid de la salida sean 0 en caso de que alguna de las entradas no sea valida """
    await init_test(dut)

    stream_inputa = Stream.Driver(dut.clk, dut, 'a__')
    stream_inputb = Stream.Driver(dut.clk, dut, 'b__')
    stream_output = Stream.Driver(dut.clk, dut, 'r__')

    N = 20
    width = len(dut.a__data)
    mask = int('1' * (width+1), 2)


    data_a = [getrandbits(width) for _ in range(N)]
    data_b = [getrandbits(width) for _ in range(N)]
    stream_inputa.valid <= 0
    stream_inputb.valid <= 1
    stream_output.ready <= 1
    for i in range(N):
        dut.rst <= 0
        stream_inputa.data <= data_a[i]
        stream_inputb.data <= data_b[i]
        await RisingEdge(dut.clk)
        assert stream_output.valid.value == 0
        assert stream_output.data.value.integer == 0


    stream_inputa.valid <= 1
    stream_inputb.valid <= 0
    stream_output.ready <= 1
    for i in range(N):
        dut.rst <= 0
        stream_inputa.data <= data_a[i]
        stream_inputb.data <= data_b[i]
        await RisingEdge(dut.clk)
        assert stream_output.valid.value == 0
        assert stream_output.data.value.integer == 0
    

    stream_inputa.valid <= 1
    stream_inputb.valid <= 1
    stream_output.ready <= 1
    dut.rst <= 0
    expected=[]
    expected = [(data_a[i]+data_b[i]) & mask for i in range(N)]
    cocotb.fork(feedInputs(stream_inputa,data_a,dut))
    cocotb.fork(feedInputs(stream_inputb,data_b,dut))
    output = await stream_output.recv(N)
    assert output == expected

if __name__ == '__main__':
    core = Sumador(16)
    run(
        core, 'ej1',
        ports=
        [
            *list(core.a.fields.values()),
            *list(core.b.fields.values()),
            *list(core.r.fields.values())
        ],
        vcd_file='sumador.vcd'
    )
