import pygame
from pygame import Vector2
import os
import sys
import random
import mutagen

def read_config(filename):
    config = {}
    with open(filename, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key.strip()] = value.strip()
    return config

# Initialize Pygame
pygame.init()

current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, 'config.txt')
config = read_config(config_file_path)


# Set up display
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Image Slideshow")

# Load images
image_folder = config['image_folder']
images = []
current_image = 0

# Set up clock
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()
music_index_time = 0

image_display_time = int(config['image_display_time'])  # Time in milliseconds (3 seconds)
image_pomodoro_sync = int(config['image_pomodoro_sync']) # one image per pomodoro session
image_random = int(config['image_random']) 
pomodoro_time = int(config['pomodoro_time']) 
break_time = int(config['break_time'])  
timer_x = int(config['timer_x'])  
timer_y = int(config['timer_y'])  
particle_x = int(config['particle_x'])  
particle_y = int(config['particle_y'])  
prepare_time = 0.2

screen_size = Vector2(1920, 1080)
ALPHA_MIN = 0
ALPHA_MAX = 255
dust_image_path = os.path.join(current_dir, 'white_ball4.png')

PREPARE = 0
POMODORO = 1
BREAK = 2

# Set up the mixer for audio
pygame.mixer.init()
MUSIC_END = pygame.USEREVENT+1
pygame.mixer.music.set_endevent(MUSIC_END)

# Define the path to your music folder
music_folder = config['music_folder']
music_files = [file for file in os.listdir(music_folder) if file.endswith((".mp3", ".wav"))]
music_title = ''
music_artist = ''

def play_next_music():
    global music_files, music_title, music_artist, base_name

    if not music_files:
        music_files = [file for file in os.listdir(music_folder) if file.endswith((".mp3", ".wav"))]

    if music_files:
        selected_music = random.choice(music_files)
        music_files.remove(selected_music)

        base_name, extension = os.path.splitext(selected_music)
        print(base_name)
        selected_music_path = os.path.join(music_folder, selected_music)
        audio = mutagen.File(selected_music_path)
        try:
            music_title = audio['TIT2']
            music_artist = audio['TPE1']
        except:
            music_title = ''
            music_artist = ''
        
        print(music_artist,': ', music_title)
        pygame.mixer.music.load(selected_music_path)

        current_time = pygame.time.get_ticks()
        print("current_time:", current_time)
        index_time = current_time - start_time
        print("index_time:", index_time)
        hour = int(index_time / (60*60*1000))
        min = int((index_time - hour * 60*60*1000)/(60*1000))
        sec = int((index_time - hour * 60*60*1000 - min*60*1000)/1000)

        if music_title == '' or music_artist == '':
            index_text = f"[{hour:1}:{min:02}:{sec:02}] {base_name}\n"
            #print("[",hour,":",min,":",sec,"]", base_name) 
        else:
            index_text = f"[{hour:1}:{min:02}:{sec:02}] {music_title} - {music_artist}\n"
            #print("[",hour,":",min,":",sec,"]", music_title,"-",music_artist)
            
        print(index_text)
        with open('playlist.txt', 'a') as file:
            file.write(index_text)       

        pygame.mixer.music.play()
    else:
        pygame.quit()
        sys.exit()

def next_image():
    global images, image_path, scaled_image, current_image
    first = False
    id_string = "thumb"

    if not images:
        images = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder) if (filename.endswith(".png") or filename.endswith(".jpg"))]       
        first = True

    if image_random == 1:
        if first:
            # Using a list comprehension to find all files with the specified id_string
            image_path = None
            for filename in images:
                if id_string in filename:
                    image_path = filename
                    break  # Stop the loop once a match is found
            print("first: ", image_path)
            if image_path == None:
                image_path = random.choice(images)
        else:
            image_path = random.choice(images)
    else:
        image_path = images[current_image]
        current_image += 1
        if current_image >= len(images):
            current_image = 0

    image = pygame.image.load(image_path)
    images.remove(image_path)   
    
    scaled_image = pygame.transform.scale(image,(1920, 1080))  # Scale image to fit screen
  
def show_image():
    screen.blit(scaled_image, (0, 0))

def draw_box():
    pygame.draw.rect(screen, (230, 230, 230), (1700, 1000, 200, 50), 5)  # Draw a black frame around the box (x, y, width, height, border_width)

def draw_timer(time, mode):
    font = pygame.font.SysFont('msgothic', 150)

    if mode == POMODORO:
        text = font.render(time, True, (255, 255, 255))
    else:
        text = font.render(time, True, (230, 230, 0))

    shadow = font.render(time, True, (80, 80, 80))
    text_rect = text.get_rect()
    text_rect.topleft = (timer_x, timer_y)
    offset = 3
    screen.blit(shadow, (text_rect.x + offset, text_rect.y + offset))
    screen.blit(text, text_rect)

def draw_music_title(x, y, font_size):
    global music_title, music_artist, base_name

    if music_title == '' or music_artist == '':
        text = str(base_name)
    else:
        text = str(music_title) + ' - ' + str(music_artist)
    font = pygame.font.SysFont('arial', font_size)  # Use default system font, or specify a font path
    text_surface = font.render(text, True, (255, 255, 255))  # Render the text with anti-aliasing in white color
    shadow = font.render(text, True, (80, 80, 80))  # Render the text with anti-aliasing in white color
    offset = 2
    screen.blit(shadow, (x + offset, y + offset))
    screen.blit(text_surface, (x, y))

def draw_message(x, y, msg):
    font = pygame.font.SysFont('arial', 36)  # Use default system font, or specify a font path
    #text = music_title + music_artist
    text_surface = font.render(msg, True, (255, 255, 255))  # Render the text with anti-aliasing in white color
    shadow = font.render(msg, True, (80, 80, 80))  # Render the text with anti-aliasing in white color
    offset = 2
    screen.blit(shadow, (x + offset, y + offset))
    screen.blit(text_surface, (x, y))


class Particle:
    cached_images = {}
    def __init__(self, pos, vel, size, alpha):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)        
        self.size = size
        self.alpha = alpha
        if self.vel.x > 0: 
            self.alpha_dir = 1
        else: 
            self.alpha_dir = -1
        self.update_image()

    def update(self, dt):
        self.pos += self.vel * dt
        
        if self.pos.x < 0:
            self.pos.x = 0
            self.vel.x *= -1
            
        elif self.pos.x > screen_size.x:
            self.pos.x = screen_size.x
            self.vel.x *= -1
            
        if self.pos.y < 0:
            self.pos.y = 0
            self.vel.y *= -1
            
        elif self.pos.y > screen_size.y:
            self.pos.y = screen_size.y
            self.vel.y *= -1
        
        self.alpha += self.alpha_dir
        if self.alpha < ALPHA_MIN:
            self.alpha = ALPHA_MIN
            self.alpha_dir = 1
        if self.alpha > ALPHA_MAX:
            self.alpha = ALPHA_MAX
            self.alpha_dir = -1

        return 1
        
    def update_image(self):       
        cache_lookup = (self.size, self.alpha)
        
        if not (cached_image := self.cached_images.get(cache_lookup, None)):
            cached_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            scaled_image = pygame.transform.scale(pygame.image.load(dust_image_path),(self.size, self.size)) 
            cached_image.blit(scaled_image, (0,0))       
            self.cached_images[cache_lookup] = cached_image
           
        self.image = cached_image


class ParticleManager:
    def __init__(self):
        self.particles = []
        
    def update(self, dt):
        self.particles = [particle for particle in self.particles if particle.update(dt)]
    
    def add(self, particles):
        self.particles.append(particles)

    def draw(self, surface):
        for particle in self.particles:
            particle.image.set_alpha(particle.alpha)
            surface.blit(particle.image, particle.pos)

    def __len__(self):
        return len(self.particles)

def update_pm(dt):
    global pm      
    pm.update(dt)

def main():
    global pm

    next_image()
    play_next_music()
    mode = PREPARE
    tcounter = pygame.time.get_ticks()
    session = 1

    running = True

    pm = ParticleManager()    
    for _ in range(60): # until it slow down under 60Hz    
        pm.add(Particle((random.randint(0, screen_size.x), random.randint(0, screen_size.y)), #position
                            (random.uniform(-10, 10), random.uniform(-10, 10)), #velocity
                            random.randint(6, 60), #size
                            random.randint(ALPHA_MIN, ALPHA_MAX))) #alpha
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == MUSIC_END:
                if image_pomodoro_sync == 0:
                    next_image()
                play_next_music()

        show_image()
        draw_music_title(50, 950, 32)  # Replace with your text and desired position

        if mode == PREPARE:
            mode_time = prepare_time
            msg = "Are you ready?"
        elif mode == POMODORO:
            mode_time = pomodoro_time
            msg = "Session: " + f"{session}"
        elif mode == BREAK:
            mode_time = break_time
            msg = "Break Time, Session: " + f"{session}"

        elapsed_time = (pygame.time.get_ticks() - tcounter)
        remaining_time = (mode_time * 60 * 1000 - elapsed_time) // 1000
        if remaining_time < 0:
            mode += 1
            tcounter = pygame.time.get_ticks()
            if mode > BREAK:
                mode = POMODORO
                if image_pomodoro_sync == 1:
                    next_image()
                session += 1 
        else:                
            timer_text = f"{int(remaining_time // 60):02}:{int(remaining_time % 60):02}"
        draw_timer(timer_text, mode)
        draw_message(timer_x + 10, timer_y - 50, msg)

        dt = clock.tick() * .01
        update_pm(dt)
        pm.draw(screen)
        
        pygame.display.update()
        clock.tick(30)  # Set frame rate (adjust as needed)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
