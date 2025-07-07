from django.core.management.base import BaseCommand
from shopping.models import Game, Genre, Platform
from django.core.files import File
from django.conf import settings
from datetime import datetime, timedelta
import random
import os

def random_recent_date(is_past=True):
    days = random.randint(0, 6)
    if is_past:
        return (datetime.now() - timedelta(days=days)).date()
    else:
        return (datetime.now() + timedelta(days=days)).date()

class Command(BaseCommand):
    help = 'Create sample game data'

    def handle(self, *args, **kwargs):
        currentDate = datetime.now()
        platforms = [
            'PC',
            'MAC',
            'PS4',
            'PS5',
            'XBOX_ONE',
            'XBOX_SERIES',
            'SWITCH',
            'SWITCH2',
        ]
        genres = [
            'ACTION',
            'ADVENTURE',
            'RPG',
            'SHOOTER',
            'SPORTS',
            'RACING',
            'PUZZLE',
            'STRATEGY',
            'SIMULATION',
            'FIGHTING',
            'PLATFORMER',
            'HORROR',
            'MMO',
            'SANDBOX',
            'STEALTH',
            'MUSIC',
            'PARTY',
            'SURVIVAL',
            'VISUAL_NOVEL',
            'INDIE',
        ]

        for platform in platforms:
            Platform.objects.get_or_create(name=platform)

        for genre in genres:
            Genre.objects.get_or_create(name=genre)

        games = [
            {
                'title': 'Donkey Kong Bananza',
                'developer': 'Nintendo',
                'publisher': 'Nintendo',
                'description': 'Join Donkey Kong and friends in this exciting platformer adventure!',
                'price': 119.95,
                'release_date': '2025-07-17',
                'image': './gameImages/donkey_kong_bananza.jpg',
                'platforms': ['SWITCH2'],
                'genres': ['PLATFORMER', 'ADVENTURE'],
                'is_sale': True,
                'sale_price': 99.95,
                'sale_start_date': random_recent_date(is_past=True),
                'sale_end_date': random_recent_date(is_past=False),
            },
            {
                'title': 'Super Mario Odyssey',
                'developer': 'Nintendo',
                'publisher': 'Nintendo',
                'description': 'Embark on a new journey with Mario in this sequel to the beloved Odyssey!',
                'price': 79.99,
                'release_date': '2017-10-27',
                'image': './gameImages/super_mario_odyssey.jpg',
                'platforms': ['SWITCH'],
                'genres': ['PLATFORMER', 'ADVENTURE'],
            },
            {
                'title': 'The Legend of Zelda: Breath of the Wild',
                'developer': 'Nintendo',
                'publisher': 'Nintendo',
                'description': 'Experience a new epic adventure in the world of Hyrule!',
                'price': 89.99,
                'release_date': '2025-12-01',
                'image': './gameImages/zelda_breath_of_the_wild.jpg',
                'platforms': ['SWITCH', 'SWITCH2'],
                'genres': ['ADVENTURE', 'RPG'],
                'is_sale': True,
                'sale_price': 69.99,
                'sale_start_date': random_recent_date(is_past=True),
                'sale_end_date': random_recent_date(is_past=False),
            },
            {
                'title': 'Cyberpunk 2077',
                'developer': 'CD Projekt Red',
                'publisher': 'CD Projekt',
                'description': 'Explore the dystopian Night City in this open-world RPG.',
                'price': 59.99,
                'release_date': '2020-12-10',
                'image': './gameImages/cyberpunk_2077.jpg',
                'platforms': ['PC', 'PS4', 'XBOX_ONE', 'PS5', 'XBOX_SERIES', 'SWITCH2'],
                'genres': ['RPG', 'ACTION', 'ADVENTURE'],
            },
            {
                'title': 'The Witcher 3: Wild Hunt',
                'developer': 'CD Projekt Red',
                'publisher': 'CD Projekt',
                'description': 'Experience the award-winning story of Geralt of Rivia in this open-world RPG.',
                'price': 49.99,
                'release_date': '2015-05-19',
                'image': './gameImages/the_witcher_3.jpg',
                'platforms': ['PC', 'PS4', 'XBOX_ONE', 'SWITCH'],
                'genres': ['RPG', 'ACTION', 'ADVENTURE'],
                'is_sale': True,
                'sale_price': 39.99,
                'sale_start_date': random_recent_date(is_past=True),
                'sale_end_date': random_recent_date(is_past=False),
            },
            {
                'title': 'Elden Ring',
                'developer': 'FromSoftware',
                'publisher': 'Bandai Namco Entertainment',
                'description': 'Explore a vast open world filled with danger and mystery in this action RPG.',
                'price': 59.99,
                'release_date': '2022-02-25',
                'image': './gameImages/elden_ring.jpg',
                'platforms': ['PC', 'PS4', 'XBOX_ONE', 'PS5', 'XBOX_SERIES', 'SWITCH2'],
                'genres': ['RPG', 'ACTION', 'ACTION RPG'],
            },
            {
                'title': 'Astro Bot',
                'developer': 'Team Asobi',
                'publisher': 'Sony Interactive Entertainment',
                'description': 'Join Astro Bot in this charming platformer adventure exclusive to PlayStation.',
                'price': 39.99,
                'release_date': '2024-11-15',
                'image': './gameImages/astro_bot.jpg',
                'platforms': ['PS5'],
                'genres': ['PLATFORMER', 'ADVENTURE'],
                'is_sale': True,
                'sale_price': 29.99,
                'sale_start_date': random_recent_date(is_past=True),
                'sale_end_date': random_recent_date(is_past=False),
            },
            {
                'title': 'Final Fantasy XVI',
                'developer': 'Square Enix',
                'publisher': 'Square Enix',
                'description': 'Experience the next chapter in the legendary RPG series.',
                'price': 69.99,
                'release_date': '2023-06-22',
                'image': './gameImages/final_fantasy_xvi.jpg',
                'platforms': ['PS5'],
                'genres': ['RPG', 'ACTION'],
            },
            {
                'title': 'Spider-Man 2',
                'developer': 'Insomniac Games',
                'publisher': 'Sony Interactive Entertainment',
                'description': 'Swing through the streets of New York in this action-packed sequel.',
                'price': 59.99,
                'release_date': '2023-10-20',
                'image': './gameImages/spider_man_2.jpg',
                'platforms': ['PS5'],
                'genres': ['ACTION', 'ADVENTURE'],
            },
            {
                'title': 'Forza Horizon 5',
                'developer': 'Playground Games',
                'publisher': 'Xbox Game Studios',
                'description': 'Experience the thrill of racing in the beautiful landscapes of Mexico.',
                'price': 59.99,
                'release_date': '2021-11-09',
                'image': './gameImages/forza_horizon_5.jpg',
                'platforms': ['PC', 'XBOX_SERIES', 'PS5'],
                'genres': ['RACING', 'SPORTS'],
                'is_sale': True,
                'sale_price': 49.99,
                'sale_start_date': random_recent_date(is_past=True),
                'sale_end_date': random_recent_date(is_past=False),
            },
            {
                'title': 'Mario Kart World',
                'developer': 'Nintendo',
                'publisher': 'Nintendo',
                'description': 'Race through iconic Mario Kart tracks in this exciting new installment.',
                'price': 59.99,
                'release_date': '2024-03-15',
                'image': './gameImages/mario_kart_world.jpg',
                'platforms': ['SWITCH2'],
                'genres': ['RACING', 'MULTIPLAYER'],
            },
            {
                'title': 'The Legend of Zelda: Tears of the Kingdom',
                'developer': 'Nintendo',
                'publisher': 'Nintendo',
                'description': 'Join Link in a new epic adventure in the world of Hyrule!',
                'price': 69.99,
                'release_date': '2023-05-12',
                'image': './gameImages/zelda_tears_of_the_kingdom.jpg',
                'platforms': ['SWITCH', 'SWITCH2'],
                'genres': ['ADVENTURE', 'RPG'],
            },
            {
                'title': 'Splatoon 3',
                'developer': 'Nintendo',
                'publisher': 'Nintendo',
                'description': 'Dive into the colorful world of Splatoon with new weapons and modes!',
                'price': 59.99,
                'release_date': '2022-09-09',
                'image': './gameImages/splatoon_3.jpg',
                'platforms': ['SWITCH', 'SWITCH2'],
                'genres': ['SHOOTER', 'MULTIPLAYER'],
            },
            {
                'title': 'Super Mario Bros. Wonder',
                'developer': 'Nintendo',
                'publisher': 'Nintendo',
                'description': 'Experience a new adventure with Mario and friends in this whimsical platformer!',
                'price': 59.99,
                'release_date': '2023-10-20',
                'image': './gameImages/super_mario_bros_wonder.jpg',
                'platforms': ['SWITCH'],
                'genres': ['PLATFORMER', 'ADVENTURE'],
            },
            {
                'title': 'Batman: Arkham Origins',
                'developer': 'WB Games Montreal',
                'publisher': 'Warner Bros. Interactive Entertainment',
                'description': 'Uncover the origins of the Dark Knight in this action-packed prequel to the Arkham series.',
                'price': 39.99,
                'release_date': '2013-10-25',
                'image': './gameImages/batman_arkham_origins.jpg',
                'platforms': ['PC', 'PS4', 'XBOX_ONE', 'PS5', 'XBOX_SERIES'],
                'genres': ['ACTION', 'ADVENTURE'],
                'is_sale': True,
                'sale_price': 29.99,
                'sale_start_date': random_recent_date(is_past=True),
                'sale_end_date': random_recent_date(is_past=False),
            },
            {
                'title': 'The Last of Us Part II',
                'developer': 'Naughty Dog',
                'publisher': 'Sony Interactive Entertainment',
                'description': 'Experience the emotional journey of Ellie in this critically acclaimed sequel.',
                'price': 59.99,
                'release_date': '2020-06-19',
                'image': './gameImages/the_last_of_us_part_ii.jpg',
                'platforms': ['PS4', 'PS5'],
                'genres': ['ACTION', 'ADVENTURE', 'SURVIVAL'],
            }
        ]

        for game_data in games:
            image_path = os.path.join(settings.BASE_DIR, 'gameImages', os.path.basename(game_data['image']))
            with open(image_path, 'rb') as img_file:
                game, created = Game.objects.get_or_create(
                    title=game_data['title'],
                    defaults={
                        'developer': game_data['developer'],
                        'publisher': game_data['publisher'],
                        'description': game_data['description'],
                        'price': game_data['price'],
                        'release_date': game_data['release_date'],
                        'is_sale': game_data.get('is_sale', False),
                        'sale_price': game_data.get('sale_price', game_data['price']),
                        'sale_start_date': game_data.get('sale_start_date'),
                        'sale_end_date': game_data.get('sale_end_date'),
                    }
                )
                if created:
                    game.image.save(os.path.basename(image_path), File(img_file), save=True)
                    game.genres.set(Genre.objects.filter(name__in=game_data['genres']))
                    game.platforms.set(Platform.objects.filter(name__in=game_data['platforms']))
                    game.save()
                    self.stdout.write(self.style.SUCCESS(f'Successfully created game: {game.title}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Game already exists: {game.title}'))