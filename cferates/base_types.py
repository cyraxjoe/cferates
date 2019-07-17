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
    # special with gov subsidy
    NINE_CU = enum.auto()
    NINE_N = enum.auto()
    # we're only missing EA
    # from which there is nothing to scrape
