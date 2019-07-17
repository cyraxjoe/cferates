import enum

class Rate(enum.Enum):
    # domestic
    ONE = enum.auto()
    ONE_A = enum.auto()
    ONE_B = enum.auto()
    ONE_C = enum.auto()
    ONE_D = enum.auto()
    ONE_E = enum.auto()
    ONE_F = enum.auto()
    DAC = enum.auto()
    # general
    PDBT = enum.auto()
    GDBT = enum.auto()
    GDMTO = enum.auto()
    GDMTH = enum.auto()
    DIST = enum.auto()
    DIT = enum.auto()
    # special
    APBT = enum.auto()
    APMT = enum.auto()
    RABT = enum.auto()
    RAMT = enum.auto()
    ###################################
    # we're missing EA, 9CU, 9N
    # EA has  nothing to scrape
    # and 9X is very simple and
    # most likely irrelevant
    # (it only chages every year)
    ##################################
