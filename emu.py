#!/usr/bin/env python

from core.Chip8 import Chip8

if __name__ == "__main__":
    vm = Chip8()
    #vm.loadProgram("pong.rom")
    #print(vm.memory[512:1024])
    vm.beep()
