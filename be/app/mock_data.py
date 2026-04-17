from datetime import datetime, timedelta

MOCK_USERS = [
    {
        'id': 1,
        'username': 'dungeon_master',
        'email': 'dm@example.com',
        'created_at': (datetime.utcnow() - timedelta(days=30)).isoformat()
    },
    {
        'id': 2,
        'username': 'player_one',
        'email': 'player1@example.com',
        'created_at': (datetime.utcnow() - timedelta(days=20)).isoformat()
    }
]

MOCK_CAMPAIGNS = [
    {
        'id': 1,
        'name': 'The Lost Mines of Phandelver',
        'description': 'A classic D&D adventure for new players',
        'owner_id': 1,
        'created_at': (datetime.utcnow() - timedelta(days=25)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=2)).isoformat(),
        'post_count': 5
    },
    {
        'id': 2,
        'name': 'Curse of Strahd',
        'description': 'A gothic horror adventure in Barovia',
        'owner_id': 1,
        'created_at': (datetime.utcnow() - timedelta(days=15)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
        'post_count': 3
    },
    {
        'id': 3,
        'name': 'Waterdeep: Dragon Heist',
        'description': 'Urban adventure in the City of Splendors',
        'owner_id': 1,
        'created_at': (datetime.utcnow() - timedelta(days=10)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=5)).isoformat(),
        'post_count': 2
    }
]

MOCK_POSTS = [
    {
        'id': 1,
        'campaign_id': 1,
        'author_id': 1,
        'title': 'Session 1: The Adventure Begins',
        'content': 'The party met in Neverwinter and accepted a quest to escort supplies to Phandalin. Along the way, they encountered a goblin ambush!',
        'created_at': (datetime.utcnow() - timedelta(days=20)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=20)).isoformat(),
        'images': []
    },
    {
        'id': 2,
        'campaign_id': 1,
        'author_id': 1,
        'title': 'Session 2: The Goblin Hideout',
        'content': 'Following the goblin trail, the party discovered a cave hideout. They rescued Sildar Hallwinter and learned about the missing Gundren Rockseeker.',
        'created_at': (datetime.utcnow() - timedelta(days=18)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=18)).isoformat(),
        'images': [
            {'id': 1, 'post_id': 2, 'file_path': 'mock_cave.jpg', 'order_index': 0}
        ]
    },
    {
        'id': 3,
        'campaign_id': 1,
        'author_id': 1,
        'title': 'Session 3: Phandalin Politics',
        'content': 'The party arrived in Phandalin and discovered the town is being terrorized by the Redbrands. They met several important NPCs including Sister Garaele and Halia Thornton.',
        'created_at': (datetime.utcnow() - timedelta(days=15)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=10)).isoformat(),
        'images': []
    },
    {
        'id': 4,
        'campaign_id': 1,
        'author_id': 1,
        'title': 'Session 4: Redbrand Hideout',
        'content': 'The party infiltrated the Redbrand hideout beneath Tresendar Manor. Epic battle with the bugbear Glasstaff!',
        'created_at': (datetime.utcnow() - timedelta(days=12)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=12)).isoformat(),
        'images': [
            {'id': 2, 'post_id': 4, 'file_path': 'mock_battle1.jpg', 'order_index': 0},
            {'id': 3, 'post_id': 4, 'file_path': 'mock_battle2.jpg', 'order_index': 1}
        ]
    },
    {
        'id': 5,
        'campaign_id': 1,
        'author_id': 1,
        'title': 'Session 5: The Wave Echo Cave',
        'content': 'Finally, the party ventured into Wave Echo Cave searching for the Forge of Spells. They encountered many dangers including a spectator and a flameskull.',
        'created_at': (datetime.utcnow() - timedelta(days=8)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=2)).isoformat(),
        'images': []
    },
    {
        'id': 6,
        'campaign_id': 2,
        'author_id': 1,
        'title': 'Welcome to Barovia',
        'content': 'The mists closed in around the party as they entered the cursed land of Barovia. The village of Barovia greeted them with an eerie silence.',
        'created_at': (datetime.utcnow() - timedelta(days=10)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=10)).isoformat(),
        'images': [
            {'id': 4, 'post_id': 6, 'file_path': 'mock_barovia.jpg', 'order_index': 0}
        ]
    },
    {
        'id': 7,
        'campaign_id': 2,
        'author_id': 1,
        'title': 'Death House',
        'content': 'The party explored the haunted Death House. Rose and Thorn led them into a nightmare of cultists and dark rituals.',
        'created_at': (datetime.utcnow() - timedelta(days=7)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=7)).isoformat(),
        'images': []
    },
    {
        'id': 8,
        'campaign_id': 2,
        'author_id': 1,
        'title': 'Meeting Strahd',
        'content': 'Count Strahd von Zarovich himself appeared before the party. His presence was both terrifying and mesmerizing.',
        'created_at': (datetime.utcnow() - timedelta(days=3)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=1)).isoformat(),
        'images': [
            {'id': 5, 'post_id': 8, 'file_path': 'mock_strahd1.jpg', 'order_index': 0},
            {'id': 6, 'post_id': 8, 'file_path': 'mock_strahd2.jpg', 'order_index': 1},
            {'id': 7, 'post_id': 8, 'file_path': 'mock_strahd3.jpg', 'order_index': 2}
        ]
    },
    {
        'id': 9,
        'campaign_id': 3,
        'author_id': 1,
        'title': 'Arrival in Waterdeep',
        'content': 'The party arrived in the magnificent City of Splendors. The bustling streets and towering buildings were overwhelming.',
        'created_at': (datetime.utcnow() - timedelta(days=6)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=6)).isoformat(),
        'images': []
    },
    {
        'id': 10,
        'campaign_id': 3,
        'author_id': 1,
        'title': 'The Yawning Portal',
        'content': 'At the famous Yawning Portal tavern, the party witnessed a troll climb out of the well. Durnan handled it with ease.',
        'created_at': (datetime.utcnow() - timedelta(days=5)).isoformat(),
        'updated_at': (datetime.utcnow() - timedelta(days=5)).isoformat(),
        'images': [
            {'id': 8, 'post_id': 10, 'file_path': 'mock_tavern.jpg', 'order_index': 0}
        ]
    }
]

def get_mock_user(user_id):
    return next((u for u in MOCK_USERS if u['id'] == user_id), None)

def get_mock_user_by_username(username):
    return next((u for u in MOCK_USERS if u['username'] == username), None)

def get_mock_campaigns(owner_id):
    return [c for c in MOCK_CAMPAIGNS if c['owner_id'] == owner_id]

def get_mock_campaign(campaign_id):
    return next((c for c in MOCK_CAMPAIGNS if c['id'] == campaign_id), None)

def get_mock_posts(campaign_id, page=1, per_page=10, sort_by='created'):
    campaign_posts = [p for p in MOCK_POSTS if p['campaign_id'] == campaign_id]
    
    if sort_by == 'updated':
        campaign_posts.sort(key=lambda x: x['updated_at'])
    else:
        campaign_posts.sort(key=lambda x: x['created_at'])
    
    start = (page - 1) * per_page
    end = start + per_page
    
    total = len(campaign_posts)
    posts = campaign_posts[start:end]
    
    return {
        'posts': posts,
        'total': total,
        'page': page,
        'pages': (total + per_page - 1) // per_page,
        'has_next': end < total,
        'has_prev': page > 1
    }

def get_mock_post(post_id):
    return next((p for p in MOCK_POSTS if p['id'] == post_id), None)
