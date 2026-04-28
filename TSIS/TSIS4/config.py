WINDOW_WIDTH  = 600
WINDOW_HEIGHT = 620   
GRID_SIZE     = 25    
CELL_SIZE     = WINDOW_WIDTH // GRID_SIZE   

FPS           = 500   
BASE_SPEED    = 30 
SPEED_FLOOR   = 3     
SPEED_STEP    = 1     
LEVEL_UP_FOOD = 5     

BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
DARK_GREEN = ( 20,  80,  20)
GREEN      = ( 60, 200,  60)
RED        = (220,  30,  30)
DARK_RED   = (120,   0,   0)
ORANGE     = (255, 140,   0)
PURPLE     = (150,  50, 220)
CYAN       = (  0, 220, 220)
YELLOW     = (240, 220,   0)
GRAY       = (100, 100, 100)
DARK_GRAY  = ( 40,  40,  40)
LIGHT_GRAY = (180, 180, 180)
BROWN      = (100,  60,  20)


FOOD_NORMAL  = "normal"
FOOD_GOLD    = "gold"
FOOD_POISON  = "poison"

FOOD_WEIGHTS = {FOOD_NORMAL: 1, FOOD_GOLD: 3}
FOOD_COLORS  = {FOOD_NORMAL: RED, FOOD_GOLD: YELLOW, FOOD_POISON: DARK_RED}
FOOD_TIMER   = 8_000   

PU_SPEED  = "speed_boost"
PU_SLOW   = "slow_motion"
PU_SHIELD = "shield"

PU_COLORS    = {PU_SPEED: ORANGE, PU_SLOW: CYAN, PU_SHIELD: PURPLE}
PU_DURATION  = 5_000   
PU_FIELD_TTL = 8_000   


OBSTACLE_COLOR       = GRAY
OBSTACLE_START_LEVEL = 3
OBSTACLES_PER_LEVEL  = 5   


DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "snake_game"
DB_USER = "postgres"
DB_PASS = "den1488"