from tkinter import Tk, Canvas

# This is an emulated display with the same API interface as for the Unicorn HAT/pHAT hardware.
# Thus, it relies upon (in part) code from: https://github.com/pimoroni/unicorn-hat/blob/master/library/UnicornHat/unicornhat.py

# Note that only the pHAT is supported, and rotation of the display is not supported.

class EmulatedGUI():
    def __init__(self, master):
        
        self.master = master
        master.title("Emulated")
        
        self.map = []
        self.pixels = [None for x in range(64)]
        self.pixel_colours = ["#000000" for x in range(64)]
        self.brightness = 1.0
        
    def setup(self, pxmap):
        self.map = pxmap
        
        # Add GUI elements in a grid
        row = 0
        col = 0
        for list in self.map:
            col = 0
            for index in list:
                
                pixel = Canvas(self.master, width=30, height=30)
                pixel.grid(row=row, column=col)
                pixel.configure(background="black", highlightbackground="black", bd=1)
                self.pixels[index] = pixel
                
                col = col + 1
                
            row = row + 1
            
    def set_pixel(self, idx, r, g, b):        
        colour = '#%02x%02x%02x' % (r, g, b)
        
        self.pixel_colours[idx] = colour
        
    def set_brightness(self, brightness):
        self.brightness = brightness
        
    def update(self):
        try:
            index = 0
            for pixel in self.pixels:
                pixel.configure(background=self.pixel_colours[index])
                index = index + 1
        except:
            pass

class EmulatedDisplay():
    def __init__(self):
        self.wx = 8
        self.wy = 8
        self.map = self.PHAT
        self.pixels = [(0,0,0) for x in range(64)]
        self.brightness_val = 0.2
        self.is_setup = False
        self.gui = None

    # Modifed from the UnicornHAT Python library
    # Available: https://github.com/pimoroni/unicorn-hat/blob/master/library/UnicornHat/unicornhat.py
    @property
    def PHAT(self):
        return [[24, 16, 8,  0],
                [25, 17, 9,  1],
                [26, 18, 10, 2],
                [27, 19, 11, 3],
                [28, 20, 12, 4],
                [29, 21, 13, 5],
                [30, 22, 14, 6],
                [31, 23, 15, 7]]
    
    def set_layout(self, pixel_map):
        self.map = self.PHAT
        
    def setup(self):
        if self.is_setup == True:
            return
        
        # Start the GUI loop
        self.root = Tk()  
        
        # Ensure we stay above other windows  
        self.root.attributes("-topmost", True)
        self.root.configure(background='black')
        self.root.lift()
        
        self.gui = EmulatedGUI(self.root)
        self.gui.setup(self.map)
        
        self.is_setup = True
                
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
       
    def get_shape(self): 
        return (len(self.map), len(self.map[0]))
        
    def rotation(self, r=0):
        pass
            
    def get_rotation(self):
        return 0

    def brightness(self, b=0.2):
        self.brightness_val = b
        
        if self.gui is not None:
            self.gui.set_brightness(b)

    def get_brightness():
        return self.brightness_val
        
    def clear():
        for x in range(64):
            self.pixels[x] = (0, 0, 0)

    def off():
        self.clear()
        self.show()
        
    def get_index_from_xy(self, x, y):
        self.wx = len(self.map) - 1
        self.wy = len(self.map[0]) - 1

        y = (self.wy)-y

        if self.rotation == 90 and self.wx == self.wy:
            x, y = y, (self.wx)-x
        elif self.rotation == 180:
            x, y = (self.wx)-x, (self.wy)-y
        elif self.rotation == 270 and self.wx == self.wy:
            x, y = (self.wy)-y, x

        try:
            index = self.map[x][y]
        except IndexError:
            index = None

        return index
    
    def set_pixel(self, x, y, r=None, g=None, b=None):
        if self.is_setup is False:
            return
        
        if type(r) is tuple:
            r, g, b = r
    
        elif type(r) is str:
            try:
                r, g, b = COLORS[r.lower()]
        
            except KeyError:
                raise ValueError('Invalid color!')

        index = self.get_index_from_xy(x, y)

        if index is not None:
            self.pixels[index] = (r, g, b)
            self.gui.set_pixel(index, r, g, b)
            
    def get_pixel(self, x, y):
        index = self.get_index_from_xy(x, y)
        if index is not None:
            return self.pixels[index]
            
    def set_all(self, r, g=None, b=None):
        shade_pixels(lambda x, y: (r, g, b))
        
    def shade_pixels(self, shader):
        width, height = self.get_shape()
        for x in range(width):
            for y in range(height):
                r, g, b = shader(x, y)
                self.set_pixel(x, y, r, g, b)

    def set_pixels(self, pixels):
        self.shade_pixels(lambda x, y: pixels[y][x])

    def get_pixels(self):
        width, height = self.get_shape()
        return [[self.get_pixel(x, y) for x in range(width)] for y in range(height)]

    def show(self):
        if self.is_setup is False:
            return
            
        self.gui.update()  