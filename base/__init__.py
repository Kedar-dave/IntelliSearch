import torch
torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

from .document_processor import *
from .video_processor import *
from .vectorizer import *
from .database import *
from .util import *
from .constants import *
__version__ = 1.1