import os
import sys

dir_path = os.path.dirname(
    os.path.realpath(__file__)
)  # As a one-file executable, this path is a temporary folder.

if getattr(sys, "frozen", False):
    dir_path = os.path.dirname(os.path.realpath(dir_path))
