import ctypes
import ctypes.util
import sys
import argparse
from typing import Optional

# Load the required libraries
x11_path = ctypes.util.find_library('X11')
xfixes_path = ctypes.util.find_library('Xfixes')
if not x11_path or not xfixes_path:
   sys.exit("Can't find required libraries")

libX11 = ctypes.CDLL(x11_path)
libXfixes = ctypes.CDLL(xfixes_path)

# Define required X11 structures and constants
class XEvent(ctypes.Union):
   _fields_ = [("type", ctypes.c_int),
               ("pad", ctypes.c_long * 24)]

class Display(ctypes.Structure):
   pass

DisplayPtr = ctypes.POINTER(Display)

# Define X11 atoms (these values are from X11/Xatom.h)
XA_PRIMARY = 1
XA_SECONDARY = 2

# Set function argument types
libX11.XOpenDisplay.argtypes = [ctypes.c_char_p]
libX11.XOpenDisplay.restype = DisplayPtr
libX11.XDefaultRootWindow.argtypes = [DisplayPtr]
libX11.XDefaultRootWindow.restype = ctypes.c_ulong
libX11.XInternAtom.argtypes = [DisplayPtr, ctypes.c_char_p, ctypes.c_int]
libX11.XInternAtom.restype = ctypes.c_ulong
libX11.XNextEvent.argtypes = [DisplayPtr, ctypes.POINTER(XEvent)]
libX11.XCloseDisplay.argtypes = [DisplayPtr]

# XFixes constants
XFixesSetSelectionOwnerNotifyMask = 1

class ClipboardMonitor:
   def __init__(self):
       self.display = libX11.XOpenDisplay(None)
       if not self.display:
           raise RuntimeError("Cannot open display")
       
       self.root = libX11.XDefaultRootWindow(self.display)
       self.clipboard = libX11.XInternAtom(self.display, b"CLIPBOARD", False)
       self.primary = XA_PRIMARY
       self.secondary = XA_SECONDARY

   def monitor(self, selections: Optional[list] = None, loop: bool = False):
       if selections is None:
           selections = ["clipboard", "primary"]

       # Set up selection monitoring
       for sel in selections:
           atom = {
               "clipboard": self.clipboard,
               "primary": self.primary,
               "secondary": self.secondary
           }.get(sel)
           
           if atom:
               libXfixes.XFixesSelectSelectionInput(
                   self.display, 
                   self.root,
                   atom,
                   XFixesSetSelectionOwnerNotifyMask
               )

       event = XEvent()
       try:
           while True:
               libX11.XNextEvent(self.display, ctypes.byref(event))
               print()  # Print newline on selection change
               if not loop:
                   break
       finally:
           libX11.XCloseDisplay(self.display)

def main():
   parser = argparse.ArgumentParser(description='Monitor X11 selections')
   parser.add_argument('-l', '--loop', action='store_true',
                     help='Print newline when new selection is available')
   parser.add_argument('-s', '--selections', type=str,
                     help='Comma-separated list of selections to monitor')

   args = parser.parse_args()
   selections = args.selections.split(',') if args.selections else None
   
   try:
       monitor = ClipboardMonitor()
       monitor.monitor(selections=selections, loop=args.loop)
   except KeyboardInterrupt:
       sys.exit(0)
   except Exception as e:
       print(f"Error: {e}", file=sys.stderr)
       sys.exit(1)

if __name__ == '__main__':
   main()
