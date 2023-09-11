import pygame
import random
from multiprocessing import Process, Pipe
from controller import controller
from math import pi
from time import sleep



def game():
    receiver, sender = Pipe(duplex=False)
    process = Process(target=controller, args=(sender,))
    # process.daemon = True
    process.start()

    
    
    # Initialize Pygame
    pygame.init()

    # Set up the game window
    width = 500
    height = int(width*pi/2.5)
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Brain Pong")

    # Set up colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    # Set up the paddle
    paddle_width = 100
    paddle_height = 10
    paddle_speed = 25
    paddle_x = width // 2 - paddle_width // 2
    paddle_y = height - paddle_height - 10

    # Set up the ball
    ball_radius = 10
    ball_x = random.randint(ball_radius, width - ball_radius)
    ball_y = ball_radius
    speed = 1.5
    ball_speed_x = random.choice([-speed, speed])
    ball_speed_y = speed
    # Game loop
    EEG_MOVE_EVENT = pygame.USEREVENT + 1
    print('Please Wait, Connecting to MUSE...')
    running = False
    while not(receiver.poll()):
        pass
    if receiver.recv() == 'go':
        running = True
    clock = pygame.time.Clock()
    print('GO Signal recieved, Game Clock Started')
    sleep(5)
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if receiver.poll():
            s = receiver.recv()
            custom_event = pygame.event.Event(EEG_MOVE_EVENT, val=s)
            pygame.event.post(custom_event)
                
        # Move the paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle_x < width - paddle_width:
            paddle_x += paddle_speed
        
        for event in pygame.event.get():
            if event.type == EEG_MOVE_EVENT:
                if event.val < 0 and paddle_x > 0:
                    paddle_x += paddle_speed * 4 * event.val
                    paddle_x = max(0, paddle_x)
                elif event.val > 0 and paddle_x < width - paddle_width:
                    paddle_x += paddle_speed * 4 * event.val
                    paddle_x = min(width, paddle_x)


        # Move the ball
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Check for collision with side walls
        if ball_x > width - ball_radius or ball_x < ball_radius:
            ball_speed_x *= -1

        # Check for collision with paddle
        if (ball_y + ball_radius >= paddle_y and (ball_x+ball_radius >= paddle_x and ball_x-ball_radius <= paddle_x+paddle_width)):
            ball_speed_y *= -1

        # Check if the ball hits the bottom wall
        if ball_y > height - ball_radius:
            ball_speed_y *= -1
            # running = False  # Game over
        elif ball_y < ball_radius:
            ball_speed_y *= -1
        # Clear the screen
        window.fill(BLACK)

        # Draw the paddle
        pygame.draw.rect(window, WHITE, (paddle_x, paddle_y, paddle_width, paddle_height))

        # Draw the ball
        pygame.draw.circle(window, WHITE, (ball_x, ball_y), ball_radius)

        # Update the display
        pygame.display.flip()
        
        # Limit the frame rate
        clock.tick(60)

    # Quit the game
    pygame.quit()
    process.terminate()
    game()
