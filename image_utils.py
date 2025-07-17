import random

def get_image_url():
    images = [
        "https://placekitten.com/640/360",
        "https://placebear.com/640/360",
        "https://picsum.photos/640/360"
    ]
    return random.choice(images)