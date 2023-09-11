import numpy as np
import matplotlib.pyplot as plt
import muse_lib
from time import sleep, time
from multiprocessing import Process, Pipe, freeze_support
from buffer import buffer
from EEGprocessing import preprocess_func, processing_func
import sounddevice as sd
import soundfile as sf

from tqdm import tqdm

import pygame
from math import pi
import random
from time import time


def scenario(mode, movement_time):
    global width, height, paddle_width, paddle_height, framerate

    if mode == -1:
        paddle_x = np.random.uniform(3*width/4, width-paddle_width)
        target_x = np.random.uniform(ball_radius, width/4-ball_radius)
    elif mode == 1:
        paddle_x = np.random.uniform(0, width/4-paddle_width)
        target_x = np.random.uniform(3*width/4+ball_radius, width-ball_radius)
    elif mode == 0:
        target_x = np.random.uniform(ball_radius, width-ball_radius)
        paddle_x = np.clip(target_x-paddle_width/2, 0, width-paddle_width)

    ball_speed_x = random.choice([-speed, speed])
    ball_speed_y = -speed

    ball_x = target_x
    ball_y = height-(paddle_height+ball_radius)

    frames = int(framerate * movement_time)
    for i in range(frames):
        # Move the ball
        ball_x += ball_speed_x
        ball_y += ball_speed_y

        # Check for collision with walls
        if ball_x > width - ball_radius or ball_x < ball_radius:
            ball_speed_x *= -1

        # Check for collision with paddle
        if (ball_y > paddle_y - ball_radius and paddle_x - ball_radius < ball_x < paddle_x + paddle_width + ball_radius) or (ball_y < ball_radius):
            ball_speed_y *= -1
            ball_y -= paddle_height

        # Check if the ball hits the bottom wall
        if ball_y > height:
            ball_speed_y *= -1
            # running = False  # Game over

    ball_speed_x = ball_speed_x*-1
    ball_speed_y = ball_speed_y*-1

    paddle_speed_x = (target_x-(paddle_x+paddle_width/2))/frames

    # print(np.round_(paddle_x, 1), np.round_(target_x, 1))

    return paddle_x, paddle_speed_x, ball_x, ball_y, ball_speed_x, ball_speed_y


def musicplayer():
    # Load the stereo audio file
    audio_file = "media\\Mus.wav"
    data, sample_rate = sf.read(audio_file)
    while True:
        sd.play(data, sample_rate)
        sd.wait()


if __name__ == '__main__':
    global width, height, paddle_width, paddle_height, framerate


    available_muses = muse_lib.list_muses()
    print('Available MUSEs:', available_muses)

    # Can be also selected by the player
    player_muse = available_muses[0]
    print('Selected MUSE:', player_muse)


    stream_receiver, stream_sender = Pipe(duplex=False)
    stream_process = Process(target=muse_lib.stream, args=(player_muse['address'],), kwargs={
                                'name': player_muse['name'], 'sender_connection': stream_sender})
    stream_process.start()
    print('Please Wait, Connecting to MUSE...')


    sfreq = 256
    decision_time = 0.5
    N_blocks = 1800  # multiplier of 30
    window_time = np.round_(N_blocks*decision_time*sfreq)/sfreq
    N_samples = int(window_time * sfreq)
    buffer_window = window_time

    N_blocks_static = N_blocks_left = N_blocks_right = N_blocks//3

    N_avg_blocks_per_mode = 10

    N_modes = N_blocks//N_avg_blocks_per_mode
    N_modes_static = N_modes_left = N_modes_right = N_blocks_static//N_avg_blocks_per_mode

    modes = N_modes_static*[0] + N_modes_left*[-1] + N_modes_right*[1]
    modes_ix = list(range(N_modes))

    N_blocks_per_mode_static = np.random.randint(
        N_avg_blocks_per_mode-2, N_avg_blocks_per_mode+2, N_modes_static)
    while np.sum(N_blocks_per_mode_static) != N_blocks_static:
        N_blocks_per_mode_static = np.random.randint(
            N_avg_blocks_per_mode-2, N_avg_blocks_per_mode+2, N_modes_static)

    N_blocks_per_mode_left = np.random.randint(
        N_avg_blocks_per_mode-2, N_avg_blocks_per_mode+2, N_modes_left)
    while np.sum(N_blocks_per_mode_left) != N_blocks_left:
        N_blocks_per_mode_left = np.random.randint(
            N_avg_blocks_per_mode-2, N_avg_blocks_per_mode+2, N_modes_left)

    N_blocks_per_mode_right = np.random.randint(
        N_avg_blocks_per_mode-2, N_avg_blocks_per_mode+2, N_modes_right)
    while np.sum(N_blocks_per_mode_right) != N_blocks_right:
        N_blocks_per_mode_right = np.random.randint(
            N_avg_blocks_per_mode-2, N_avg_blocks_per_mode+2, N_modes_right)

    N_blocks_per_mode = np.concatenate(
        (N_blocks_per_mode_static, N_blocks_per_mode_left, N_blocks_per_mode_right))


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
    paddle_speed = 15
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
    

    buffer_receiver, buffer_sender = Pipe(duplex=False)
    buffer_signal_receiver, buffer_signal_sender = Pipe(duplex=False)
    buffer_process = Process(target=buffer, args=(player_muse, buffer_window, buffer_receiver, buffer_sender, buffer_signal_sender))
    buffer_process.start()

    musicplayer_process = Process(target=musicplayer)
    musicplayer_process.start()


    while not (stream_receiver.poll()):
        pass

    while not (buffer_receiver.poll()):
        pass
    n_chan, sfreq = buffer_receiver.recv()


    
    print('GO Signal recieved, Game Clock Started')
    
    

    running = True
    framerate = 60
    clock = pygame.time.Clock()
    

    mode_counter = 1
    p_bar = tqdm(range(N_blocks))
    p_bar.update(mode_counter-1)
    p_bar.refresh()

    t0 = time()
    t00 = time()
    movement_counter = 1
    mode_ix = random.choice(modes_ix)
    modes_ix.remove(mode_ix)
    mode = modes[mode_ix]
    mode_time = N_blocks_per_mode[mode_ix] * decision_time

    # print(mode, N_blocks_per_mode[mode_ix])
    paddle_x, paddle_speed_x, ball_x, ball_y, ball_speed_x, ball_speed_y = scenario(
        mode, mode_time)

    mode_time_cum = mode_time

    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # if receiver.poll():
        #     s = receiver.recv()
        #     custom_event = pygame.event.Event(EEG_MOVE_EVENT, val=s)
        #     pygame.event.post(custom_event)

        # Move the paddle
        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_LEFT] and paddle_x > 0:
        #     paddle_x -= paddle_speed
        # if keys[pygame.K_RIGHT] and paddle_x < width - paddle_width:
        #     paddle_x += paddle_speed

        # for event in pygame.event.get():
        #     if event.type == EEG_MOVE_EVENT:
        #         if event.val < 0 and paddle_x > 0:
        #             paddle_x += paddle_speed * 4 * event.val
        #             paddle_x = max(0, paddle_x)
        #         elif event.val > 0 and paddle_x < width - paddle_width:
        #             paddle_x += paddle_speed * 4 * event.val
        #             paddle_x = min(width, paddle_x)

        if time()-t0 >= mode_time_cum:
            # print(np.round_(ball_x, 1), np.round_(ball_y, 1))
            mode_counter += 1
            p_bar.update(mode_counter-1)
            p_bar.refresh()
            movement_counter = 1

            if mode_counter > N_modes:
                running = False
                break

            t00 = time()
            mode_ix = random.choice(modes_ix)
            modes_ix.remove(mode_ix)
            mode = modes[mode_ix]
            mode_time = N_blocks_per_mode[mode_ix] * decision_time

            # print(mode, N_blocks_per_mode[mode_ix])
            paddle_x, paddle_speed_x, ball_x, ball_y, ball_speed_x, ball_speed_y = scenario(
                mode, mode_time)

            mode_time_cum += mode_time

        # Move the ball
        ball_x += ball_speed_x
        ball_y += ball_speed_y
        if time()-t00>=movement_counter*decision_time:
            paddle_x = np.clip(paddle_x+paddle_speed_x*framerate*decision_time, 0, width-paddle_width) 
            movement_counter += 1

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
        pygame.draw.rect(window, WHITE, (paddle_x, paddle_y,
                         paddle_width, paddle_height))

        # Draw the ball
        pygame.draw.circle(window, WHITE, (ball_x, ball_y), ball_radius)

        # Update the display
        pygame.display.flip()

        # Limit the frame rate

        clock.tick(framerate)

    # Quit the game
    pygame.quit()
    buffer_sender.send(True)
    while not (buffer_signal_receiver.poll()):
        pass
    signal, time_ser = buffer_signal_receiver.recv()
    np.savez('data', time_ser=time_ser, signal=signal, modes=modes, N_blocks_per_mode=N_blocks_per_mode, window_time=window_time, decision_time=decision_time, N_samples=N_samples, N_blocks=N_blocks)

    musicplayer_process.terminate()
    stream_process.terminate()
    buffer_process.terminate()
