import pygame
import math

pygame.init()
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('props/font/myFont.ttf', 32)
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])
bgs = []
banners = []
guns = []
target_list = [[], [], []]
# we need a way to dictate how many of the targets to display in each level
targets = {1: [10, 5, 3],
           2: [12, 8, 5],
           3: [15, 12, 8, 3]}
# The first thing the user sees is the menu
menu = True
write_values = False
best_free_play = 0
best_ammo = 0
best_time = 0
game_over = False
pause = False
level = 0
points = 0
shots_fired = False
total_shots = 0
# 0 free_play, 1 accuracy, 2 timed
mode = 0
ammo = 0
time_elapsed = 0
time_remaining = 0
counter = 1
clicked = False


def load_images_and_scores(backgrounds, banners_list, guns_list, target_list):
    # load each of the images
    for i in range(1, 4):
        backgrounds.append(pygame.image.load(f'props/bgs/{i}.png'))
        banners_list.append(pygame.image.load(f'props/banners/{i}.png'))
        guns_list.append(pygame.transform.scale(pygame.image.load(f'props/guns/{i}.png'), (110, 110)))
        if i < 3:
            for j in range(1, 4):
                # creating progressively smaller enemies to increase difficulty
                target_list[i - 1].append(pygame.transform.scale(
                    pygame.image.load(f'props/targets/{i}/{j}.png'), (120 - (j * 18), 80 - (j * 12))))
        else:
            # load the hardest level too.
            for j in range(1, 5):
                # creating progressively smaller enemies to increase difficulty
                target_list[i - 1].append(pygame.transform.scale(
                    pygame.image.load(f'props/targets/{i}/{j}.png'), (120 - (j * 18), 80 - (j * 12))))
    global best_free_play, best_ammo, best_time
    stored_file = open('high_scores.txt', 'r')
    line = stored_file.readlines()
    stored_file.close()
    if len(line) > 0:
        best_free_play = int(line[0])
        best_ammo = int(line[1])
        best_time = int(line[2])


def get_sound():

    bird_sound = pygame.mixer.Sound('props/sounds/Drill Gear.mp3')
    bird_sound.set_volume(.4)

    plate_sound = pygame.mixer.Sound('props/sounds/Broken plates.wav')
    plate_sound.set_volume(.4)

    laser_sound = pygame.mixer.Sound('props/sounds/3.mp3')
    laser_sound.set_volume(.5)

    yee_haw_sound = pygame.mixer.Sound('props/sounds/yee-haw.mp3')
    yee_haw_sound.set_volume(1)

    return {1: bird_sound, 2: plate_sound, 3: laser_sound, 4: yee_haw_sound}


def set_to_nth_level(parm_level, parm_menu):
    global level, time_elapsed, total_shots, points, menu
    level = parm_level
    time_elapsed = 0
    total_shots = 0
    points = 0
    menu = parm_menu


def reset_best_scores():
    global best_free_play, best_ammo, best_time
    best_free_play = 0
    best_ammo = 0
    best_time = 0


def draw_menu():
    # make sure to refer to the variables in the outer scope
    global ammo, mode, time_remaining, write_values, clicked, pause, game_over

    pause = False
    game_over = False

    screen.blit(pygame.image.load(f'props/menus/mainMenu.png'), (0, 0))

    # render the fonts
    screen.blit(font.render(f'{best_free_play}', True, 'black'), (340, 580))
    screen.blit(font.render(f'{best_ammo}', True, 'black'), (650, 580))
    screen.blit(font.render(f'{best_time}', True, 'black'), (350, 710))

    # create Rects for collision detection
    free_play_button = pygame.Rect((170, 524), (260, 100))
    ammo_button = pygame.Rect((475, 524), (260, 100))
    timed_button = pygame.Rect((170, 661), (260, 100))
    reset_button = pygame.Rect((475, 661), (260, 100))

    # event handling
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    # the user must let go of the button before selecting the other menu options
    if not clicked:
        # the user must click one of the four buttons to begin
        if free_play_button.collidepoint(mouse_pos) and clicks[0]:
            mode = 0
            set_to_nth_level(1, False)
            clicked = True
            # yeeeee-hawwww
            sound_dict[4].play()

        if ammo_button.collidepoint(mouse_pos) and clicks[0]:
            mode = 1
            ammo = 81
            set_to_nth_level(1, False)
            clicked = True
            # yeeeee-hawwww
            sound_dict[4].play()
        if timed_button.collidepoint(mouse_pos) and clicks[0]:
            mode = 2
            time_remaining = 40
            set_to_nth_level(1, False)
            clicked = True
            # yeeeee-hawwww
            sound_dict[4].play()
        if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
            reset_best_scores()
            write_values = True
            clicked = True


def draw_game_over():
    global clicked, pause, game_over, time_remaining
    game_over_font = pygame.font.Font('props/font/myFont.ttf', 64)
    if mode == 0:
        display_score = time_elapsed
    else:
        display_score = points
    screen.blit(pygame.image.load(f'props/menus/gameOver.png'), (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    exit_button = pygame.Rect((170, 661), (260, 100))
    menu_button = pygame.Rect((475, 661), (260, 100))
    screen.blit(game_over_font.render(f'{display_score}', True, 'black'), (650, 570))

    if not clicked:
        if menu_button.collidepoint(mouse_pos) and clicks[0]:
            clicked = True
            set_to_nth_level(0, True)
            pause = False
            game_over = False
            time_remaining = 0
            # yeeeee-hawwww
            sound_dict[4].play()
        if exit_button.collidepoint(mouse_pos) and clicks[0]:
            global run
            run = False


def draw_pause():
    global clicked, level, pause, time_remaining, init_flag
    screen.blit(pygame.image.load(f'props/menus/pause.png'), (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()

    resume_button = pygame.Rect((170, 661), (260, 100))
    menu_button = pygame.Rect((475, 661), (260, 100))

    if not clicked:
        if resume_button.collidepoint(mouse_pos) and clicks[0]:
            level = resume_level
            pause = False
            clicked = True
            # yeeeee-hawwww
            sound_dict[4].play()
        if menu_button.collidepoint(mouse_pos) and clicks[0]:
            pause = False
            clicked = True
            time_remaining = 0
            pygame.mixer.music.play()
            set_to_nth_level(0, True)
            init_flag = True


def draw_gun():
    # get the mouse position
    mouse_pos = pygame.mouse.get_pos()
    # gun points to the center of the screen
    gun_point = (WIDTH / 2, HEIGHT - 200)
    lasers = ['red', 'purple', 'green']
    clicks = pygame.mouse.get_pressed()

    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])
    else:
        slope = 100000000
    angle = math.atan(slope)
    rotation = math.degrees(angle)

    # if the mouse is on the left side of the screen
    if mouse_pos[0] < WIDTH / 2:
        # flip the gun by the x-axis
        gun = pygame.transform.flip(guns[level - 1], True, False)
        # we only want the gun to show up if we aren't in the menu
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH / 2 - 90, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
    else:
        gun = guns[level - 1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH / 2 - 30, HEIGHT - 250))
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)


def get_hit_zones(coordinates):
    if level == 1 or level == 2:
        # creating invisible rectangles for collision detection
        target_rects = [[], [], []]
    else:
        target_rects = [[], [], [], []]
        # get enemy from each category
    for enemy_category in range(len(coordinates)):
        # the list contains the enemy of same category repeated.
        for enemy_number in range(len(coordinates[enemy_category])):
            # create a smaller target_rec for each enemy
            left_top = (coordinates[enemy_category][enemy_number][0] + 20,
                        coordinates[enemy_category][enemy_number][1])
            width_height = (60 - enemy_category * 12, 60 - enemy_category * 12)
            target_rects[enemy_category].append(pygame.Rect(left_top, width_height))
            # display each enemy of same category
            screen.blit(target_list[level - 1][enemy_category], coordinates[enemy_category][enemy_number])
    return target_rects


def move_level(coordinates):
    # smaller targets move faster
    # which means greater the value of i the faster the target
    if level == 1 or level == 2:
        max_val = 3
    else:
        max_val = 4
    for target_category in range(max_val):
        for target_num in range(len(coordinates[target_category])):
            my_coords = coordinates[target_category][target_num]
            # if the target is all the way to the left, we move it to the right
            if my_coords[0] < -150:
                coordinates[target_category][target_num] = (WIDTH, my_coords[1])
            else:
                # moving the target faster with proportion to its category
                coordinates[target_category][target_num] = (my_coords[0] - 2 ** target_category, my_coords[1])


def check_shot(target_box_list, coordinates, score):
    mouse_pos = pygame.mouse.get_pos()
    for target_category in range(len(target_box_list)):
        for target_num in range(len(target_box_list[target_category])):
            if target_box_list[target_category][target_num].collidepoint(mouse_pos):
                # remove the target that was hit
                coordinates[target_category].pop(target_num)
                # for each increasing tier of enemy hits , the points increase
                score += 10 + 10 * (target_category ** 2)
                sound_dict[level].play()
    return score


def draw_score():
    points_text = font.render(f'Points: {points}', True, 'black')
    screen.blit(points_text, (330, 657))
    shots_text = font.render(f'Total Shots: {total_shots}', True, 'black')
    screen.blit(shots_text, (330, 684))
    time_text = font.render(f'Time elapsed: {time_elapsed}', True, 'black')
    screen.blit(time_text, (320, 711))
    if mode == 0:
        mode_text = font.render(f'FreePlay!', True, 'black')
    elif mode == 1:
        mode_text = font.render(f'Ammo Remaining: {ammo}', True, 'black')
    else:
        mode_text = font.render(f'Time Remaining: {time_remaining}', True, 'black')
    screen.blit(mode_text, (320, 739))


def initialize_coords():
    # load the images
    load_images_and_scores(bgs, banners, guns, target_list)

    # initialize the enemy coordinates
    level_one_coords = [[], [], []]
    level_two_coords = [[], [], []]
    level_three_coords = [[], [], [], []]

    coordinate_dict = {1: level_one_coords, 2: level_two_coords, 3: level_three_coords}
    for key, coords in coordinate_dict.items():
        if key == 3:
            size = 4
            factor = 100
        else:
            size = 3
            factor = 150

        nums = targets[key]
        for i in range(size):
            for j in range(nums[i]):
                hit_zone = (WIDTH // (nums[i]) * j, 300 - (i * factor) + 30 * (j % 2))
                coords[i].append(hit_zone)
    return coordinate_dict


if __name__ == '__main__':

    run = True
    # get the coordinate dictionary
    coords_dict = initialize_coords()
    init_flag = False

    pygame.mixer.init()
    pygame.mixer.music.load('props/sounds/bg_music.mp3')
    MUSIC_END = pygame.USEREVENT+1
    pygame.mixer.music.set_endevent(MUSIC_END)
    pygame.mixer.music.play(loops=-1)

    sound_dict = get_sound()

    while run:

        # reinitialize the coordinates everytime the user goes back to main menu
        if init_flag:
            coords_dict = initialize_coords()
            init_flag = False
        # tick must be called once per frame
        timer.tick(fps)
        # 60 frames per second
        if level != 0:
            if counter < 60:
                counter += 1
            else:
                counter = 1
                time_elapsed += 1
                if mode == 2:
                    time_remaining -= 1

        # create the menu for the user
        if menu:
            level = 0
            draw_menu()
        # game over screen
        elif game_over:
            level = 0
            draw_game_over()
        # pause menu
        elif pause:
            level = 0
            draw_pause()
        else:
            screen.blit(bgs[level - 1], (0, 0))
            screen.blit(banners[level - 1], (0, HEIGHT - 200))

        if level > 0:
            hit_zone_areas = get_hit_zones(coords_dict[level])
            # create illusion of movement
            move_level(coords_dict[level])
            draw_gun()
            draw_score()
            if shots_fired:
                # check if the shot hit
                points = check_shot(hit_zone_areas, coords_dict[level], points)
                shots_fired = False
            # move to the next level
            if hit_zone_areas == [[], [], []] and level < 3:
                level += 1
            # game over for mode 1
            if (mode == 1 and ammo == 0) or (mode == 2 and time_remaining == 0) or (
                    level == 3 and hit_zone_areas == [[], [], [], []]):
                pygame.mixer.music.play()
                init_flag = True
                if mode == 0:
                    if time_elapsed < best_free_play or best_free_play == 0:
                        best_free_play = time_elapsed
                        write_values = True
                if mode == 1:
                    if points > best_ammo:
                        best_ammo = points
                        write_values = True
                if mode == 2:
                    if points > best_time:
                        best_time = points
                        write_values = True
                game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # if a hit (left mouse button)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_position = pygame.mouse.get_pos()
                if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200):
                    shots_fired = True
                    total_shots += 1
                    if mode == 1:
                        ammo -= 1
                # check if the pause button is clicked
                if (670 < mouse_position[0] < 860) and (660 < mouse_position[1] < 715):
                    resume_level = level
                    pause = True
                    clicked = True
                # check if the restart button has been hit
                if (670 < mouse_position[0] < 860) and (715 < mouse_position[1] < 760):
                    menu = True
                    pygame.mixer.music.play()
                    clicked = True
                    init_flag = True
                # the user must release the button to select other menu options
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                clicked = False
            if event.type == MUSIC_END:
                pygame.mixer.music.play(loops=-1)

        # if new best_scores
        if write_values:
            file = open('high_scores.txt', 'w')
            file.write(f'{best_free_play}\n{best_ammo}\n{best_time}')
            file.close()
            write_values = False
        pygame.display.flip()
pygame.mixer.music.unload()
pygame.quit()
