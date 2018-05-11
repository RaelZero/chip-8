#!/usr/bin/env python

class Chip8(object):
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

        if operation == 0xA000:
            self.I = self.opcode & 0x0FFF
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
