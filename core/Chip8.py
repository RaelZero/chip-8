class Chip8(object):
    def __init__(self):
        # Initialize registers
        self.registers = {
                'V0': 0, 'V1': 0,
                'V2': 0, 'V3': 0,
                'V4': 0, 'V5': 0,
                'V6': 0, 'V7': 0,
                'V8': 0, 'V9': 0,
                'VA': 0, 'VB': 0,
                'VC': 0, 'VD': 0,
                'VE': 0, 'VF': 0
        }

        # Initialize memory
        self.memory = [0] * 4096

        # Current opcode
        self.opcode = 0

        # Index and program counter
        self.I = 0
        self.pc = 0

        # Screen
        self.screen = [[0 for x in range(64)] for x in range (32)]

        # Timers
        self.delayTimer = 0
        self.soundTimer = 0
