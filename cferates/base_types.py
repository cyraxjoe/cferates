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


RATE_NAME_MAP = {
    '1': Rate.ONE,
    '1A': Rate.ONE_A,
    '1B': Rate.ONE_B,
    '1C': Rate.ONE_C,
    '1D': Rate.ONE_D,
    '1E': Rate.ONE_E,
    '1F': Rate.ONE_F,
    'DAC': Rate.DAC,
    'GDMTO': Rate.GDMTO,
    'RAMT': Rate.RAMT,
    'APMT': Rate.APMT,
    'GDMTH': Rate.GDMTH,
    'DIST': Rate.DIST,
    'DIT': Rate.DIT,
}

DOMESTIC_RATE_NAMES = {'1', '1A', '1B', '1C', '1D', '1E', '1F', 'DAC'}
SUMMER_RATE_NAMES = {'1A', '1B', '1C', '1D', '1E', '1F'}
