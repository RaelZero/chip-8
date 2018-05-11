#!/usr/bin/env python

import random

class Chip8(object):
    """Specification here:
        https://en.wikipedia.org/wiki/CHIP-8#Virtual_machine_description
    """

    fontset = [
    0xF0, 0x90, 0x90, 0x90, 0xF0, #0
    0x20, 0x60, 0x20, 0x20, 0x70, #1
    0xF0, 0x10, 0xF0, 0x80, 0xF0, #2
    0xF0, 0x10, 0xF0, 0x10, 0xF0, #3
    0x90, 0x90, 0xF0, 0x10, 0x10, #4
    0xF0, 0x80, 0xF0, 0x10, 0xF0, #5
    0xF0, 0x80, 0xF0, 0x90, 0xF0, #6
    0xF0, 0x10, 0x20, 0x40, 0x40, #7
    0xF0, 0x90, 0xF0, 0x90, 0xF0, #8
    0xF0, 0x90, 0xF0, 0x10, 0xF0, #9
    0xF0, 0x90, 0xF0, 0x90, 0x90, #A
    0xE0, 0x90, 0xE0, 0x90, 0xE0, #B
    0xF0, 0x80, 0x80, 0x80, 0xF0, #C
    0xE0, 0x90, 0x90, 0x90, 0xE0, #D
    0xF0, 0x80, 0xF0, 0x80, 0xF0, #E
    0xF0, 0x80, 0xF0, 0x80, 0x80  #F
    ]

    def __init__(self):
        # Initialize registers
        self.registers = [0] * 16

        # Initialize memory
        self.memory = [0] * 4096

        # Initialize opcode
        self.opcode = 0

        # Initialize index and program counter
        self.I = 0
        self.pc = 0x200

        # Initialize stack and stack pointer
        self.stack = [0] * 16
        self.sp = 0

        # Clean screen
        self.screen = [[0] * 64] * 32

        # Initialize keypad
        self.key = [0] * 16

        # Load fontset into memory
        for i in range(80):
            self.memory[i] = Chip8.fontset[i]

        # Initialize timers
        self.delayTimer = 0
        self.soundTimer = 0

    # Load ROM passed via name parameter to memory
    def loadProgram(self, name):
        try:
            # Open file as bytes object
            rom = open(name, 'rb')
            position = 0x200 #512

            byte = rom.read(1)
            while byte != b'':
                self.memory[position] = byte
                byte = rom.read(1)
                position += 1
        except OSError:
            raise

    def runCycle(self):
        # Fetch current opcode
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        # Decode opcode
        operation = self.instruction & 0xF000

        if operation == 0x8000: # 0x8XY* operations
            subop = self.opcode & 0x000F
            VX = self.opcode & 0x0F00
            VY = self.opcode & 0x00F0
            if subop == 0x0000: # 0x8XY0
                # VX = VY
            elif subop == 0x0001: # 0x8XY1
            self.registers[VX] = self.registers[VY]
                # VX = VX | VY
                self.registers[VX] = self.registers[VX] | self.registers[VY]
            elif subop == 0x0002: # 0x8XY2
                # VX = VX & VY
                self.registers[VX] = self.registers[VX] & self.registers[VY]
            elif subop == 0x0003: # 0x8XY3
                # VX = VX ^ VY
                self.registers[VX] = self.registers[VX] ^ self.registers[VY]
            elif subop == 0x0004: # 0x8XY4
                # VX += VY
                self.registers[VX] += self.registers[VY]
            elif subop == 0x0005: # 0x8XY5
                # VX -= VY
                self.registers[VX] -= self.registers[VY]
            elif subop == 0x0006: # 0x8XY6
                # VX = VY = VY >> 1
                # Shifts VY right by one and stores the result to VX (VY remains unchanged).
                # VF is set to the value of the least significant bit of VY before the shift.
                self.registers[-1] = self.registers[VY] & 0x0001
                self.registers[VX] = self.registers[VY] >> 1
            elif subop == 0x0007: # 0x8XY7
                # VX = VY - VX
                self.registers[VX] = self.registers[VY] - self.registers[VX]
            elif subop == 0x000E: # 0x8XYE
                # VX = VY = VY << 1
                # Shifts VY left by one and copies the result to VX.
                # VF is set to the value of the most significant bit of VY before the shift.
                self.registers[-1] = (self.registers[VY] & 0x8000) >> 15
                self.registers[VX] = self.registers[VY] << 1
            self.pc += 2
        elif operation == 0xA000: # 0xANNN
            # Set value of I to NNN
            self.I = self.opcode & 0x0FFF
            self.pc += 2
        elif operation == 0xB000: # 0xBNNN
            # Jump to V0+NNN
            address = self.opcode & 0x0FFF
            self.pc = self.registers[0] + address
        elif operation == 0xC000: # 0xCXNN
            # Set VX to rand() & NN
            targetReg = self.opcode & 0x0F00
            value = self.opcode & 0x00FF
            registers[targetReg] = random.randint(0.255) & value
            self.pc += 2
        else:
            print("Unknown opcode: " + str(operation))

        # Update timers
        if delayTimer > 0:
            delayTimer -= 1
        if soundTimer > 0:
            if soundTimer == 1:
                self.beep()
            soundTimer -= 1

    def beep(self):
        print("Beep!")
