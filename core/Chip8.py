#!/usr/bin/env python

import random
import os
import pygame

class Chip8(object):
    """
        Specification here:
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

        # Initialize keypad
        self.key = [0] * 16

        # Load fontset into memory
        for i in range(80):
            self.memory[i] = Chip8.fontset[i]

        # Initialize timers
        self.delayTimer = 0
        self.soundTimer = 0

        # Initialize screen and screen size
        # CHIP-8 Display is 64x32 - here it will be upscaled with each CHIP-8 pixel becoming an 8x8 emulator screen pixel
        screenWidth = 64
        screenHeight = 32
        screenScaling = 8

        self.screenSize = (
            screenWidth * screenScaling,
            screenHeight * screenScaling,
            screenScaling
        )

        # Clean screen
        self.screen = [0] * screenWidth * screenHeight

        self.drawFlag = False

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

    # Beep for 0.1 seconds through the `play` command
    def beep(self):
        duration = .1  # second
        freq = 2200  # Hz
        os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (duration, freq))

    # Initialize the Pygame window that will be used for the emulator
    def initGFX(self):
        width = self.screenSize[0]
        height = self.screenSize[1]

        pygame.init()

        pygame.display.set_mode((width, height))
        startingFrame = pygame.Surface((width, height))
        pixels = pygame.PixelArray(startingFrame)

        # Draw a gradient effect
        for y in range(height):
            r, g, b = y, y, y
            pixels[:,y] = (r, g, b)
        del(pixels)

        screen = pygame.display.get_surface()
        screen.blit(startingFrame, (0, 0))
        pygame.display.flip()

    # Draw the current screen buffer on the emulator window
    # Called if the drawFlag is up at the beginning fo a cycle
    def draw(self):
        width = self.screenSize[0]
        height = self.screenSize[1]

        # Reset the draw flag
        if self.drawFlag:
            self.drawFlag = False

        # Upscale screen
        nextFrame = upscaleCurrentScreen()

        # Apply it to the window
        window = pygame.display.get_surface()
        window.blit(nextFrame, (0, 0))
        pygame.display.flip()

    # Scale the screen state contained in self.screen to the window size
    # Return the PixelArray for the new frame
    def upscaleCurrentScreen(self):
        width = self.screenSize[0]
        height = self.screenSize[1]
        scalingFactor = self.screenSize[2]

        # Reshape the screen list into a screen matrix
        reshape = lambda flat, width: [flat[i:i+width] for i in range(0, len(flat), width)]
        screenMatrix = reshape(self.screen, 64)

        # Upscale the screen matrix by a factor of scalingFactor
        enlargedMatrix = []
        for row in screenMatrix:
            expandedRow = []
            for c in row:
                for i in range(scalingFactor):
                    expandedRow.append(c)
            for i in range(scalingFactor):
                enlargedMatrix.append(expandedRow)

        # Copy the enlarged matrix into a pygame surface
        upscaledFrame = pygame.Surface((width, height))
        pixels = pygame.PixelArray(upscaledFrame)

        for row in enlargedMatrix:
            for col in row:
                pixels[row, col] = enlargedMatrix[r][c]

        return upscaledFrame

    def runCycle(self):
        # Fetch current opcode
        self.opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

        # Decode opcode
        operation = self.instruction & 0xF000

        # Execute opcode
        if operation == 0x8000: # 0x8XY* operations
            subop = self.opcode & 0x000F
            VX = (self.opcode & 0x0F00) >> 8
            VY = (self.opcode & 0x00F0) >> 4
            if subop == 0x0000: # 0x8XY0
                # VX = VY
                self.registers[VX] = self.registers[VY]
            elif subop == 0x0001: # 0x8XY1
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
            targetReg = (self.opcode & 0x0F00) >> 8
            value = self.opcode & 0x00FF
            registers[targetReg] = random.randint(0.255) & value
            self.pc += 2
        elif operation == 0xD000: # 0xDXYN
            # Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels. Each row of 8 pixels is read as bit-coded starting from memory location I; I value doesn’t change after the execution of this instruction. As described above, VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that doesn’t happen

            # Raise the draw flag
            self.drawFlag = True

            # Extract x, y and height
            xCoord = (self.opcode & 0x0F00) >> 8
            yCoord = (self.opcode & 0x00F0) >> 4
            height = (self.opcode & 0x000F)

            self.registers[0xF] = 0

            # Draw the pixels on the screen
            for yLine in range(height):
                pixel = self.memory[self.I + yLine]
                for xLine in range(8):
                    if ((pixel & (0x80 >> xLine)) != 0):
                        #todo finish implementing screen drawing
                        pass

        else:
            print("Unknown opcode: " + str(operation))

        # Update timers
        if delayTimer > 0:
            delayTimer -= 1
        if soundTimer > 0:
            if soundTimer == 1:
                self.beep()
            soundTimer -= 1

    def run(self):
        self.initGFX()

        while 1:
            event = pygame.event.wait()
            if self.drawFlag:
                self.draw()
            if event.type == pygame.QUIT:
                print("Quitting...")
                raise SystemExit
