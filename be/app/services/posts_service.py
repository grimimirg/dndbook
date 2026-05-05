"""Service for post operations."""

import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.models import Post, Campaign, Image, Comment, Notification


class PostsService:
    """Service for handling post business logic."""

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    @staticmethod
    def allowed_file(filename):
        """
        Check if a filename has an allowed extension.

        Args:
            filename (str): The filename to check

        Returns:
            bool: True if the file extension is allowed, False otherwise
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in PostsService.ALLOWED_EXTENSIONS

    @staticmethod
    def can_access_campaign(campaign, user):
        """
        Check if user can access campaign (owner or member).

        Args:
            campaign: The campaign object to check access for
            user: The user object to verify

        Returns:
            bool: True if user is owner or member, False otherwise
        """
        if campaign.owner_id == user.id:
            return True
        is_member = campaign.members.filter_by(id=user.id).first() is not None
        return is_member

    @staticmethod
    def get_posts(campaign_id, user, page=1, per_page=None, sort_by='updated', order='desc', importance_level=None):
        """
        Get paginated posts for a campaign.

        Supports sorting by created or updated date, and ascending or descending order.
        User must be campaign owner or member to access.

        Args:
            campaign_id (int): The ID of the campaign
            user: The user requesting access
            page (int): Page number (default: 1)
            per_page (int): Items per page (default: from config)
            sort_by (str): Sort field - 'created' or 'updated' (default: 'updated')
            order (str): Sort order - 'asc' or 'desc' (default: 'desc')
            importance_level (int): Filter by importance level (optional)

        Returns:
            dict: Paginated posts with metadata

        Raises:
            ValueError: If user is not authorized or importance_level is invalid
        """
        if per_page is None:
            per_page = current_app.config['POSTS_PER_PAGE']

        campaign = Campaign.query.get_or_404(campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        query = Post.query.filter_by(campaign_id=campaign_id)

        if importance_level is not None:
            if importance_level < 0 or importance_level > 10:
                raise ValueError('importance_level must be between 0 and 10')
            query = query.filter_by(importance_level=importance_level)

        if sort_by == 'order' or sort_by == 'custom':
            order_field = Post.post_order
        elif sort_by == 'created':
            order_field = Post.created_at
        else:
            order_field = Post.updated_at

        if order == 'asc':
            query = query.order_by(order_field.asc())
        else:
            query = query.order_by(order_field.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'posts': [post.to_dict() for post in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    @staticmethod
    def create_post(user, campaign_id, title, content, importance_level=0):
        """
        Create a new post in a campaign.

        User must be campaign owner or member to create posts.

        Args:
            user: The user creating the post
            campaign_id (int): The campaign ID
            title (str): Post title
            content (str): Post content
            importance_level (int): Importance level (0-10)

        Returns:
            Post: The created post

        Raises:
            ValueError: If user is not authorized or importance_level is invalid
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        if not isinstance(importance_level, int) or importance_level < 0 or importance_level > 10:
            raise ValueError('importance_level must be an integer between 0 and 10')

        max_order = db.session.query(db.func.max(Post.post_order)).filter_by(campaign_id=campaign_id).scalar()
        new_order = (max_order + 1) if max_order is not None else 1

        post = Post(
            campaign_id=campaign_id,
            author_id=user.id,
            title=title,
            content=content,
            post_order=new_order,
            importance_level=importance_level
        )

        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)

        PostsService.create_notification_entries(
            user_id=user.id,
            campaign_id=campaign_id,
            notification_type='post_created',
            title=f'New post: {title}',
            message=f'A new post "{title}" was created in the campaign.',
            related_post_id=post.id
        )

        return post

    @staticmethod
    def get_post(post_id, user):
        """
        Get a specific post by ID.

        User must have access to the campaign to view the post.

        Args:
            post_id (int): The ID of the post
            user: The user requesting access

        Returns:
            Post: The post object

        Raises:
            ValueError: If user is not authorized
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        return post

    @staticmethod
    def update_post(post_id, user, title=None, content=None, importance_level=None):
        """
        Update a post.

        User must have access to the campaign to update posts.

        Args:
            post_id (int): The ID of the post
            user: The user requesting the update
            title (str): Updated post title (optional)
            content (str): Updated post content (optional)
            importance_level (int): Updated importance level (optional)

        Returns:
            Post: The updated post

        Raises:
            ValueError: If user is not authorized or importance_level is invalid
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        if title:
            post.title = title
        if content:
            post.content = content
        if importance_level is not None:
            if not isinstance(importance_level, int) or importance_level < 0 or importance_level > 10:
                raise ValueError('importance_level must be an integer between 0 and 10')
            post.importance_level = importance_level

        db.session.commit()

        PostsService.create_notification_entries(
            user_id=user.id,
            campaign_id=post.campaign_id,
            notification_type='post_edited',
            title=f'Post updated: {post.title}',
            message=f'The post "{post.title}" was edited in the campaign.',
            related_post_id=post.id
        )

        return post

    @staticmethod
    def delete_post(post_id, user):
        """
        Delete a post and all associated images.

        User must have access to the campaign to delete posts.
        Deletes all image files from disk and database records.

        Args:
            post_id (int): The ID of the post
            user: The user requesting the deletion

        Raises:
            ValueError: If user is not authorized
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        for image in post.images:
            try:
                os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.file_path))
            except:
                pass

        from app.models.post_viewed_status import PostViewedStatus
        db.session.execute(PostViewedStatus.delete().where(PostViewedStatus.c.post_id == post_id))

        from app.models.notification import Notification
        Notification.query.filter_by(related_post_id=post_id).delete()
        comment_ids = [comment.id for comment in post.comments]
        if comment_ids:
            Notification.query.filter(Notification.related_comment_id.in_(comment_ids)).delete()

        db.session.delete(post)
        db.session.commit()

    @staticmethod
    def upload_image(post_id, user, file, description=None, order_index=None):
        """
        Upload an image to a post.

        User must have access to the campaign to upload images.
        Allowed extensions: png, jpg, jpeg, gif, webp.

        Args:
            post_id (int): The ID of the post
            user: The user uploading the image
            file: File object to upload
            description (str): Image description (optional)
            order_index (int): Image order index (optional)

        Returns:
            Image: The created image

        Raises:
            ValueError: If user is not authorized or file is invalid
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        if not file or file.filename == '':
            raise ValueError('No file selected')

        if not PostsService.allowed_file(file.filename):
            raise ValueError('File type not allowed')

        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"

        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, mode=0o755, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        if order_index is None:
            order_index = len(post.images)

        image = Image(
            post_id=post_id,
            file_path=unique_filename,
            description=description,
            order_index=order_index
        )

        db.session.add(image)
        db.session.commit()

        return image

    @staticmethod
    def delete_image(post_id, image_id, user):
        """
        Delete an image from a post.

        User must have access to the campaign to delete images.
        Removes the image file from disk and database record.

        Args:
            post_id (int): The ID of the post
            image_id (int): The ID of the image
            user: The user requesting the deletion

        Raises:
            ValueError: If user is not authorized
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        image = Image.query.filter_by(id=image_id, post_id=post_id).first_or_404()

        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.file_path))
        except:
            pass

        db.session.delete(image)
        db.session.commit()

    @staticmethod
    def update_image(post_id, image_id, user, description=None, order_index=None):
        """
        Update an image's description and order.

        User must be campaign owner to modify images.

        Args:
            post_id (int): The ID of the post
            image_id (int): The ID of the image
            user: The user requesting the update
            description (str): Updated image description (optional)
            order_index (int): Updated order index (optional)

        Returns:
            Image: The updated image

        Raises:
            ValueError: If user is not authorized
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        image = Image.query.filter_by(id=image_id, post_id=post_id).first_or_404()

        if description is not None:
            image.description = description

        if order_index is not None:
            image.order_index = order_index

        db.session.commit()

        return image

    @staticmethod
    def reorder_images(post_id, user, image_orders):
        """
        Reorder all images for a post.

        User must be campaign owner to reorder images.

        Args:
            post_id (int): The ID of the post
            user: The user requesting the reorder
            image_orders (list): Array of objects with image_id and order_index

        Raises:
            ValueError: If user is not authorized or payload is invalid
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        if not isinstance(image_orders, list):
            raise ValueError('image_orders must be an array')

        for item in image_orders:
            image_id = item.get('image_id')
            order_index = item.get('order_index')

            if image_id is None or order_index is None:
                raise ValueError('Each image_order must have image_id and order_index')

            image = Image.query.filter_by(id=image_id, post_id=post_id).first()
            if image:
                image.order_index = order_index

        db.session.commit()

    @staticmethod
    def create_comment(post_id, user, content, post_title=None, campaign_name=None):
        """
        Create a comment on a post.

        User must have access to the campaign to comment.

        Args:
            post_id (int): The ID of the post
            user: The user creating the comment
            content (str): Comment content
            post_title (str): Post title (optional, for notification optimization)
            campaign_name (str): Campaign name (optional, for notification optimization)

        Returns:
            Comment: The created comment

        Raises:
            ValueError: If user is not authorized or content is missing
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsService.can_access_campaign(campaign, user):
            raise ValueError('Unauthorized')

        if not content:
            raise ValueError('Missing content')

        comment = Comment(
            post_id=post_id,
            author_id=user.id,
            content=content
        )

        db.session.add(comment)
        db.session.commit()
        db.session.refresh(comment)

        post_title = post_title or post.title
        campaign_name = campaign_name or campaign.name

        PostsService.create_comment_notification_entries(
            user_id=user.id,
            campaign_id=post.campaign_id,
            post_id=post_id,
            comment_id=comment.id,
            comment_content=content,
            post_title=post_title,
            campaign_name=campaign_name
        )

        return comment

    @staticmethod
    def update_comment(post_id, comment_id, user, content):
        """
        Update a comment.

        Only the comment author can update their comment.

        Args:
            post_id (int): The ID of the post
            comment_id (int): The ID of the comment
            user: The user requesting the update
            content (str): Updated comment content

        Returns:
            Comment: The updated comment

        Raises:
            ValueError: If user is not the comment author or content is missing
        """
        comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first_or_404()

        if comment.author_id != user.id:
            raise ValueError('Unauthorized')

        if not content:
            raise ValueError('Missing content')

        comment.content = content
        db.session.commit()

        return comment

    @staticmethod
    def delete_comment(post_id, comment_id, user):
        """
        Delete a comment.

        Only the comment author can delete their comment.

        Args:
            post_id (int): The ID of the post
            comment_id (int): The ID of the comment
            user: The user requesting the deletion

        Raises:
            ValueError: If user is not the comment author
        """
        comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first_or_404()

        if comment.author_id != user.id:
            raise ValueError('Unauthorized')

        db.session.delete(comment)
        db.session.commit()

    @staticmethod
    def reorder_posts(post_id, user, post_ids):
        """
        Reorder posts within a campaign.

        Accepts an array of post IDs in the new order and updates the order field
        for each post based on its position in the array.

        User must be the campaign owner to reorder posts.

        Args:
            post_id (int): The ID of a post in the campaign (used to identify the campaign)
            user: The user requesting the reorder
            post_ids (list): Array of post IDs in the desired order

        Raises:
            ValueError: If user is not authorized or payload is invalid
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if campaign.owner_id != user.id:
            raise ValueError('Unauthorized')

        if not isinstance(post_ids, list):
            raise ValueError('post_ids must be an array')

        for idx, pid in enumerate(post_ids, start=1):
            post_to_update = Post.query.get(pid)
            if post_to_update and post_to_update.campaign_id == campaign.id:
                post_to_update.post_order = idx
            else:
                raise ValueError(f'Post {pid} not found or not in campaign')

        db.session.commit()

    @staticmethod
    def create_notification_entries(user_id, campaign_id, notification_type, title, message, related_post_id=None):
        """
        Create notification entries for all campaign members (excluding owner).

        Args:
            user_id (int): The ID of the user who triggered the notification (will be excluded)
            campaign_id (int): The ID of the campaign
            notification_type (str): Type of notification ('post_created', 'post_edited', 'invite')
            title (str): Notification title
            message (str): Notification message
            related_post_id (int, optional): Related post ID for post notifications
        """
        from app.events.socketio_events import send_notification

        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return

        members = campaign.members.filter(Campaign.id != campaign.owner_id).all()

        for member in members:
            if member.id == user_id:
                continue

            notification = Notification(
                user_id=member.id,
                campaign_id=campaign_id,
                notification_type=notification_type,
                title=title,
                message=message,
                related_post_id=related_post_id
            )
            db.session.add(notification)

            send_notification(member.id)

        db.session.commit()

    @staticmethod
    def create_comment_notification_entries(user_id, campaign_id, post_id, comment_id, comment_content, post_title, campaign_name):
        """
        Create notification entries for all campaign members when a comment is added.

        Args:
            user_id (int): The ID of the user who created the comment (will be excluded)
            campaign_id (int): The ID of the campaign
            post_id (int): The ID of the post
            comment_id (int): The ID of the comment
            comment_content (str): The content of the comment (for preview)
            post_title (str): The title of the post (passed from FE to avoid extra query)
            campaign_name (str): The name of the campaign (passed from FE to avoid extra query)
        """
        from app.events.socketio_events import send_notification

        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            return

        members = campaign.members.all()

        for member in members:
            if member.id == user_id:
                continue

            comment_preview = comment_content[:100] + '...' if len(comment_content) > 100 else comment_content

            notification = Notification(
                user_id=member.id,
                campaign_id=campaign_id,
                notification_type='comment_added',
                title='New comment',
                message=f'New comment on "{post_title}" in {campaign_name}: "{comment_preview}"',
                related_post_id=post_id,
                related_comment_id=comment_id
            )
            db.session.add(notification)

            send_notification(member.id)

        db.session.commit()
