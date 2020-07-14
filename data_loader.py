import nrrd
import matplotlib.pyplot as plt
import numpy as np

def load(fname):
    data, header = nrrd.read(fname)
    return data, header