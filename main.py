import pygame
import random
import threading
import pyttsx3 # how to install: pip install pyttsx3
import json

#load the texts ffrom level_up_text.json
level_texts = json.load(open("level_up_text.json", "r"))

# Initialize Pygame
pygame.init()

# Initialize pyttsx3
# In english please no more spanish or german or what the user has set as their default language
engine = pyttsx3.init()
engine.setProperty('rate', 150) # 150 words per minute
engine.setProperty('volume', 0.9) # 90% volume
voices = engine.getProperty('voices')
for voice in voices:
    print(voice)
    if 'EN' or 'English' in voice.name:
        engine.setProperty('voice', voice.id)

# Set up the game window
window_width = 800
window_height = 600
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Snake Game")

# Set up the colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
gray = (128, 128, 128)  # New color for the grid

# Set up the snake and food
snake_block_size = 20
snake_speed = 5
snake_list = []
snake_length = 1
snake_head = [window_width / 2, window_height / 2]
food_pos = [random.randrange(1, (window_width // snake_block_size)) * snake_block_size,
            random.randrange(1, (window_height // snake_block_size)) * snake_block_size]

# RPG mechanics
snake_xp = 0
snake_level = 1
required_xp = 50

# Set up the game loop
game_over = False
clock = pygame.time.Clock()

# Load the sound
game_over_sound_wall_collision = pygame.mixer.Sound("bruh.mp3")
game_over_sound_self_collision = pygame.mixer.Sound("huh.mp3")  # New sound for game over
level_up_sound = pygame.mixer.Sound("levelup.mp3")  # New sound for level up

# Set up the microtransaction button
button_width = 100
button_height = 50
button_pos = (window_width - button_width, 0)
last_direction = [0, 0]

# Animation variables
level_up_animation = False
animation_counter = 0
animation_duration = 30
animation_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Flashy colors for the animation

subtitle = ""

def speakAfterTime(text, time):
    def speak():
        global subtitle
        subtitle = "You have reached level " + str(snake_level) + "!"
        pygame.time.wait(time)
        for text in level_texts[str(snake_level)]:
            print(text)
            subtitle = text["text"]
            engine.say(text["text"])
            engine.runAndWait()
            pygame.time.wait(100) # wait 100ms between each text
        subtitle = ""

    threading.Thread(target=speak).start()

# Game loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and last_direction != [snake_block_size, 0]:
                last_direction = [-snake_block_size, 0]
            elif event.key == pygame.K_RIGHT and last_direction != [-snake_block_size, 0]:
                last_direction = [snake_block_size, 0]
            elif event.key == pygame.K_UP and last_direction != [0, snake_block_size]:
                last_direction = [0, -snake_block_size]
            elif event.key == pygame.K_DOWN and last_direction != [0, -snake_block_size]:
                last_direction = [0, snake_block_size]

    # Move the snake
    snake_head[0] += last_direction[0]
    snake_head[1] += last_direction[1]

    # Check for collision with the food
    if abs(snake_head[0] - food_pos[0]) <= snake_block_size and abs(snake_head[1] - food_pos[1]) <= snake_block_size:
        food_pos = [random.randrange(1, (window_width // snake_block_size)) * snake_block_size,
                    random.randrange(1, (window_height // snake_block_size)) * snake_block_size]
        snake_length += 1
        snake_xp += 10

    # Level up the snake if it reaches the required amount of XP
    if snake_xp >= required_xp:
        snake_level += 1
        snake_xp = 0
        snake_speed += 1
        required_xp += 10  # Increase the required XP for the next level
        level_up_sound.play()  # Play the level up sound
        level_up_animation = True  # Start the animation
        speakAfterTime(f"{int(snake_level)}", 6000)
        # Update the snake's body
    snake_list.append(list(snake_head))
    if len(snake_list) > snake_length:
        del snake_list[0]

    # Check for collision with the snake's body
    for segment in snake_list[:-1]:
        if segment == snake_head:
            game_over = True
            game_over_sound_self_collision.play()  # Play the new sound when the snake dies

    # Check for collision with the window's edges
    if snake_head[0] < 0 or snake_head[0] > window_width - snake_block_size or snake_head[1] < 0 or snake_head[1] > window_height - snake_block_size:
        game_over = True
        game_over_sound_wall_collision.play()

    # Draw the grid
    for x in range(0, window_width, snake_block_size):
        pygame.draw.line(window, gray, (x, 0), (x, window_height))
    for y in range(0, window_height, snake_block_size):
        pygame.draw.line(window, gray, (0, y), (window_width, y))

    # Draw the microtransaction button
    pygame.draw.rect(window, black, (button_pos[0], button_pos[1], button_width, button_height))

    # Draw the snake and food
    window.fill(black)
    for segment in snake_list:
        pygame.draw.rect(window, white, [segment[0], segment[1], snake_block_size, snake_block_size])
    pygame.draw.rect(window, red, [food_pos[0], food_pos[1], snake_block_size, snake_block_size])

# Draw the XP and level
    font = pygame.font.Font(None, 36)
    xp_text = font.render(f"XP: {snake_xp} / {required_xp}", True, white)
    level_text = font.render(f"Level: {snake_level}", True, white)
    window.blit(xp_text, (10, 10))
    window.blit(level_text, (10, 50))

    # Draw the subtitle and center it on the bottom half of the screen
    font = pygame.font.Font(None, 36)
    subtitle_text = font.render(subtitle, True, white)
    subtitle_text_rect = subtitle_text.get_rect()
    subtitle_text_rect.center = (window_width / 2, window_height / 2 + window_height / 4)
    window.blit(subtitle_text, subtitle_text_rect)

    # Level up animation
    if level_up_animation:
        animation_counter += 1
        if animation_counter <= animation_duration:
            # Shitty animation
            for segment in snake_list:
                pygame.draw.rect(window, random.choice(animation_colors), [segment[0], segment[1], snake_block_size, snake_block_size])
        else:
            level_up_animation = False
            animation_counter = 0

    # Update the display
    pygame.display.update()

    # Set the game speed
    clock.tick(snake_speed)

# Wait for sound to finish
pygame.time.wait(1000)

# Quit the game
pygame.quit()
