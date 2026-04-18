const MOCK_USER = {
  id: 1,
  username: 'admin',
  email: 'dm@example.com',
  created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString()
};

const MOCK_CAMPAIGNS = [
  {
    id: 1,
    name: 'The Lost Mines of Phandelver',
    description: 'A classic D&D adventure for new players',
    owner_id: 1,
    created_at: new Date(Date.now() - 25 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    post_count: 5
  },
  {
    id: 2,
    name: 'Curse of Strahd',
    description: 'A gothic horror adventure in Barovia',
    owner_id: 1,
    created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    post_count: 3
  },
  {
    id: 3,
    name: 'Waterdeep: Dragon Heist',
    description: 'Urban adventure in the City of Splendors',
    owner_id: 1,
    created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    post_count: 2
  }
];

const MOCK_POSTS = [
  {
    id: 1,
    campaign_id: 1,
    author_id: 1,
    author: 'admin',
    title: 'Session 1: The Adventure Begins',
    content: 'The party met in Neverwinter and accepted a quest to escort supplies to Phandalin. Along the way, they encountered a goblin ambush!',
    created_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 2,
    campaign_id: 1,
    author_id: 1,
    author: 'admin',
    title: 'Session 2: The Goblin Hideout',
    content: 'Following the goblin trail, the party discovered a cave hideout. They rescued Sildar Hallwinter and learned about the missing Gundren Rockseeker.',
    created_at: new Date(Date.now() - 18 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 18 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 3,
    campaign_id: 1,
    author_id: 1,
    author: 'admin',
    title: 'Session 3: Phandalin Politics',
    content: 'The party arrived in Phandalin and discovered the town is being terrorized by the Redbrands. They met several important NPCs including Sister Garaele and Halia Thornton.',
    created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 4,
    campaign_id: 1,
    author_id: 1,
    author: 'admin',
    title: 'Session 4: Redbrand Hideout',
    content: 'The party infiltrated the Redbrand hideout beneath Tresendar Manor. Epic battle with the bugbear Glasstaff!',
    created_at: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 5,
    campaign_id: 1,
    author_id: 1,
    author: 'admin',
    title: 'Session 5: The Wave Echo Cave',
    content: 'Finally, the party ventured into Wave Echo Cave searching for the Forge of Spells. They encountered many dangers including a spectator and a flameskull.',
    created_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 6,
    campaign_id: 2,
    author_id: 1,
    author: 'admin',
    title: 'Welcome to Barovia',
    content: 'The mists closed in around the party as they entered the cursed land of Barovia. The village of Barovia greeted them with an eerie silence.',
    created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 7,
    campaign_id: 2,
    author_id: 1,
    author: 'admin',
    title: 'Death House',
    content: 'The party explored the haunted Death House. Rose and Thorn led them into a nightmare of cultists and dark rituals.',
    created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 8,
    campaign_id: 2,
    author_id: 1,
    author: 'admin',
    title: 'Meeting Strahd',
    content: 'Count Strahd von Zarovich himself appeared before the party. His presence was both terrifying and mesmerizing.',
    created_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 9,
    campaign_id: 3,
    author_id: 1,
    author: 'admin',
    title: 'Arrival in Waterdeep',
    content: 'The party arrived in the magnificent City of Splendors. The bustling streets and towering buildings were overwhelming.',
    created_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  },
  {
    id: 10,
    campaign_id: 3,
    author_id: 1,
    author: 'admin',
    title: 'The Yawning Portal',
    content: 'At the famous Yawning Portal tavern, the party witnessed a troll climb out of the well. Durnan handled it with ease.',
    created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    images: []
  }
];

export const mockApi = {
  async login(username, password) {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    if (username === MOCK_USER.username) {
      return {
        data: {
          message: 'Login successful',
          token: 'mock-jwt-token-' + Date.now(),
          user: MOCK_USER
        }
      };
    }
    
    throw { response: { data: { error: 'Invalid credentials' }, status: 401 } };
  },

  async register(username, email, password) {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const newUser = {
      id: 2,
      username,
      email,
      created_at: new Date().toISOString()
    };
    
    return {
      data: {
        message: 'User created successfully',
        token: 'mock-jwt-token-' + Date.now(),
        user: newUser
      }
    };
  },

  async getCampaigns() {
    await new Promise(resolve => setTimeout(resolve, 300));
    return { data: MOCK_CAMPAIGNS };
  },

  async createCampaign(data) {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const newCampaign = {
      id: MOCK_CAMPAIGNS.length + 1,
      name: data.name,
      description: data.description || '',
      owner_id: 1,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      post_count: 0
    };
    
    MOCK_CAMPAIGNS.push(newCampaign);
    return { data: newCampaign };
  },

  async getCampaignPosts(campaignId, params) {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    let posts = MOCK_POSTS.filter(p => p.campaign_id === campaignId);
    
    if (params.sort === 'updated') {
      posts.sort((a, b) => new Date(a.updated_at) - new Date(b.updated_at));
    } else {
      posts.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    }
    
    const page = params.page || 1;
    const perPage = params.per_page || 10;
    const start = (page - 1) * perPage;
    const end = start + perPage;
    
    return {
      data: {
        posts: posts.slice(start, end),
        total: posts.length,
        page,
        pages: Math.ceil(posts.length / perPage),
        has_next: end < posts.length,
        has_prev: page > 1
      }
    };
  },

  async createPost(data) {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const newPost = {
      id: MOCK_POSTS.length + 1,
      campaign_id: data.campaign_id,
      author_id: 1,
      author: MOCK_USER.username,
      title: data.title,
      content: data.content,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      images: []
    };
    
    MOCK_POSTS.unshift(newPost);
    return { data: newPost };
  },

  async uploadImage(postId, formData) {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const post = MOCK_POSTS.find(p => p.id === postId);
    if (!post) {
      throw { response: { data: { error: 'Post not found' }, status: 404 } };
    }
    
    const file = formData.get('file');
    const mockImage = {
      id: Date.now(),
      post_id: postId,
      file_path: `mock_${file.name}`,
      order_index: post.images.length
    };
    
    post.images.push(mockImage);
    return { data: mockImage };
  }
};
