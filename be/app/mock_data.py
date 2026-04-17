from datetime import datetime, timedelta


class MockDataProvider:
    """
    Provides hardcoded test data for development when MOCK_DATA=true
    """
    
    USERS = [
        {
            'id': 1,
            'username': 'admin',
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

    CAMPAIGNS = [
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

    POSTS = [
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

    @classmethod
    def get_user(cls, user_id):
        """Get user by ID"""
        return next((u for u in cls.USERS if u['id'] == user_id), None)

    @classmethod
    def get_user_by_username(cls, username):
        """Get user by username"""
        return next((u for u in cls.USERS if u['username'] == username), None)

    @classmethod
    def get_campaigns(cls, owner_id):
        """Get all campaigns for a user"""
        return [c for c in cls.CAMPAIGNS if c['owner_id'] == owner_id]

    @classmethod
    def get_campaign(cls, campaign_id):
        """Get campaign by ID"""
        return next((c for c in cls.CAMPAIGNS if c['id'] == campaign_id), None)

    @classmethod
    def get_posts(cls, campaign_id, page=1, per_page=10, sort_by='created'):
        """Get paginated posts for a campaign"""
        campaign_posts = [p.copy() for p in cls.POSTS if p['campaign_id'] == campaign_id]
        
        for post in campaign_posts:
            author = cls.get_user(post['author_id'])
            post['author'] = author['username'] if author else None
        
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

    @classmethod
    def get_post(cls, post_id):
        """Get post by ID"""
        return next((p for p in cls.POSTS if p['id'] == post_id), None)
    
    @classmethod
    def create_campaign(cls, name, description, owner_id):
        """Create a new mock campaign"""
        new_id = max([c['id'] for c in cls.CAMPAIGNS]) + 1 if cls.CAMPAIGNS else 1
        new_campaign = {
            'id': new_id,
            'name': name,
            'description': description,
            'owner_id': owner_id,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'post_count': 0
        }
        cls.CAMPAIGNS.append(new_campaign)
        return new_campaign
    
    @classmethod
    def create_post(cls, campaign_id, author_id, title, content):
        """Create a new mock post"""
        new_id = max([p['id'] for p in cls.POSTS]) + 1 if cls.POSTS else 1
        author = cls.get_user(author_id)
        new_post = {
            'id': new_id,
            'campaign_id': campaign_id,
            'author_id': author_id,
            'author': author['username'] if author else None,
            'title': title,
            'content': content,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'images': []
        }
        cls.POSTS.append(new_post)
        
        campaign = cls.get_campaign(campaign_id)
        if campaign:
            campaign['post_count'] += 1
            campaign['updated_at'] = datetime.utcnow().isoformat()
        
        return new_post
