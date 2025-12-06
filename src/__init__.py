import sys
import os

# Append the library to sys.path
library_folder = os.path.dirname(os.path.abspath(__file__))
if library_folder not in sys.path:
    sys.path.insert(0, library_folder)

# DEBUG
#print(f"sys.path: {sys.path}")
