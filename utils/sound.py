import pygame

def load_sounds():
    try:
        pygame.mixer.music.load("utils/sounds/music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        return {
            'victory': pygame.mixer.Sound("utils/sounds/victory.wav"),
            'get': pygame.mixer.Sound("utils/sounds/get.wav"),
            'nice': pygame.mixer.Sound("utils/sounds/nice.wav"),
            'hit': pygame.mixer.Sound("utils/sounds/hit.wav")
        }
    except pygame.error:
        print("Warning: Missing sounds file!")
        return {
            'victory': None, 'get': None,
            'nice': None, 'hit': None
        }