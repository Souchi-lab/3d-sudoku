
N_VALUE: int = 3 # Nの値を定義
LENGTH_OF_SIDE: int = N_VALUE # N_VALUEと同じ値を設定

# setting
ATTEMPT_NUM: int = 50
CHOICE_NUM: int = 10
SECTION_PER_NUM: int = 1
CALUCUATE_TIME = 100
NUMBER_OF_PLAYER = 1
CPU_PLAYER_ID = 2

# enviroment
GROUPING_NUMS: list = [[1, 2], [3, 4]]


# TAモード用定数
TA_BASE_TIME_LV1: int = 600
TA_BASE_TIME_LV2: int = 480
TA_BASE_TIME_LV3: int = 900
TA_BASE_TIME_LV4: int = 720
TA_BASE_TIME_LV5: int = 960

TIME_GAIN_LINE_COMPLETE: int = 4
TIME_GAIN_SLICE_COMPLETE: int = 12
TIME_GAIN_5_CONSECUTIVE_SUCCESS: int = 8
TIME_PENALTY_WRONG_PLACEMENT: int = 10

# Initial game setup
INITIAL_FILLED_CELLS = []

# loggin
LOG_FILE_PATH : str = './log/'
LOG_FILE_NAME : str = '4cube.log'
LOG_ENCODE: str = 'utf-8'
APP_LOG_FORMAT: str = '%(asctime)s:%(levelname)s:%(game_id)s:%(message)s'
CONSOLE_LOG_FORMAT: str = '%(asctime)s:%(levelname)s:%(name)s:%(pathname)s:%(lineno)d:%(message)s'
LOG_MAX_BYTES: int = 1024 * 1024 * 10 # 10MB
LOG_BACKUP_COUNT: int = 10

# command
CHECK_CUBE: str = "CC"
DISPLAY_NUMBERS: str = "DN"
DISPLAY_CANDIDATE: str = "DC"
END_GAME: str = "EG"

CAN_CHECK_CUBE_CNT: int = 5
CAN_DISPLAY_NUMBERS_CNT: int = 5
CAN_DISPLAY_CANDIDATE_CNT: int = 5
LIMIT_OF_WRONG: int = 3

# message
START_MESSAGE: str = (
    " GAME_START\n"
    "====================================================================================================================="
    " Please enter the position for the given number."
    f" If you want check cube -> {CHECK_CUBE}"
    f" , display numbers -> {DISPLAY_NUMBERS}, display candidate -> {DISPLAY_CANDIDATE}"
    f" , end game -> {END_GAME}"
)

MAX_SKIP_COUNT: int = 3

CAN_NOT_USE_MESSAGE: str = "    You can't use this command."
ATTEND_USE_MESSAGE: str = "    You can use this command {} more times."
ATTEND_FAILURE_MESSAGE: str = "    The remaining number of failures is {}"

INPUT_MESSAGE_WRONG_FORMAT: str = "    You specified wrong format."
INPUT_MESSAGE_HAS_VALUE: str = "    Your specified point is already fixed."
INPUT_MESSAGE_BAD_SPECIFY: str = "    ... please check cube."

# log part
LOG_PART_000 = "    |-----------------------|-----------------------|-----------------------|\n"
LOG_PART_001 = "    |         [Z={}]         |         [X={}]         |         [Y={}]         |\n"
LOG_PART_002 = r"    | Y\X |  1   2   3   4  | Z\Y |  1   2   3   4  | X\Z |  1   2   3   4  |\n"
LOG_PART_003 = "    |     |                 |     |                 |     |                 |\n"
LOG_PART_004 = "|  {}  |  {}   {}   {}   {}  "
LOG_PART_004_E = "|  {}  |  {}   {}   {}   {}  |\n"
