import random
import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# User class to define the behavior and attributes of users in the simulation
class User:
    def __init__(self, user_id, name, quality, x, y, user_type):
        self.user_id = user_id
        self.name = name
        self.quality = quality  # A float representing user quality (0 to 1)
        self.x = x  # Initial x-coordinate, limited to -5 to 5
        self.y = y  # Initial y-coordinate, limited to -5 to 5
        self.experiment_x = random.uniform(-2, 2)  # Experimental x-coordinate starts near the center
        self.experiment_y = random.uniform(-2, 2)  # Experimental y-coordinate starts near the center
        self.experiment_quality = 5000  # Default quality score, ranges from 0 to 10000
        self.user_type = user_type  # User behavior type: 'random', 'agree', 'quality', or 'extremist'
        self.liked_posts_x = []  # Tracks x-coordinates of liked posts
        self.liked_posts_y = []  # Tracks y-coordinates of liked posts

    # Method for creating posts associated with this user
    def create_post(self, posts):
        quality = random.random()
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        post_id = len(posts) + 1
        post = Post(post_id, self.user_id, quality, x, y)
        posts.append(post)

    # Determines how the user interacts with a given post
    def decide_interaction(self, post):
        distance = ((self.experiment_x - post.experiment_x) ** 2 + (self.experiment_y - post.experiment_y) ** 2) ** 0.5
        quality_factor = post.experiment_quality / 10000

        if self.user_type == 'random':
            # Random users interact with no clear pattern
            return random.choices(['like', 'dislike', 'none'], [0.15, 0.15, 0.7])[0]
        elif self.user_type == 'agree':
            # Users tend to like posts closer to them and with high quality
            prob_like = 0.4 * (1 - distance / 10) + 0.3 * quality_factor
            prob_dislike = 0.3 * (distance / 10) + 0.2 * (1 - quality_factor)
            return random.choices(['like', 'dislike', 'none'], [prob_like, prob_dislike, 1 - prob_like - prob_dislike])[0]
        elif self.user_type == 'quality':
            # Users interact based more on quality than proximity
            prob_like = 0.5 * quality_factor + 0.2 * (1 - distance / 10)
            prob_dislike = 0.4 * (distance / 10) + 0.3 * (1 - quality_factor)
            return random.choices(['like', 'dislike', 'none'], [prob_like, prob_dislike, 1 - prob_like - prob_dislike])[0]
        elif self.user_type == 'extremist':
            # Users only like posts far from the origin in both x and y
            if abs(post.experiment_x) >= 3.5 and abs(post.experiment_y) >= 3.5:
                return 'like'
            else:
                return 'none'

    # Adjusts user's experimental coordinates slightly toward a post they liked
    def rubber_band_adjustment(self, post, pull_strength=0.1):
        delta_x = pull_strength * (post.experiment_x - self.experiment_x)
        delta_y = pull_strength * (post.experiment_y - self.experiment_y)
        self.experiment_x = max(-5, min(5, self.experiment_x + delta_x))
        self.experiment_y = max(-5, min(5, self.experiment_y + delta_y))

    def __repr__(self):
        return f"User({self.user_id}, {self.name}, {self.quality}, {self.x}, {self.y}, {self.experiment_x}, {self.experiment_y}, {self.experiment_quality}, {self.user_type})"


# Post class to define posts created by users
class Post:
    def __init__(self, post_id, user_id, quality, x, y):
        self.post_id = post_id
        self.user_id = user_id
        self.quality = quality  # Post quality (0 to 1)
        self.x = max(-5, min(5, x))  # x-coordinate, constrained to -5 to 5
        self.y = max(-5, min(5, y))  # y-coordinate, constrained to -5 to 5
        self.experiment_x = self.x  # Experimental x-coordinate matches initial x
        self.experiment_y = self.y  # Experimental y-coordinate matches initial y
        self.experiment_quality = 5000  # Default experimental quality score
        self.likes = 0  # Number of likes received
        self.dislikes = 0  # Number of dislikes received

    # Handle interactions from users and update post attributes
    def interact(self, user, pull_strength=0.1):
        action = user.decide_interaction(self)
        distance = ((user.experiment_x - self.experiment_x) ** 2 + (user.experiment_y - self.experiment_y) ** 2) ** 0.5

        if action == 'like':
            self.likes += 1
            user.rubber_band_adjustment(self, pull_strength)
            self.rubber_band_adjustment(user, pull_strength)
            # Improve quality if liked by users
            quality_boost = (1 - distance / 10) * user.experiment_quality / 10000
            self.experiment_quality = min(10000, self.experiment_quality + quality_boost * 100)
        elif action == 'dislike':
            self.dislikes += 1
            # Reduce quality if disliked by users
            quality_drop = (1 - distance / 10) * user.experiment_quality / 10000
            self.experiment_quality = max(0, self.experiment_quality - quality_drop * 100)

    # Adjusts post's experimental coordinates slightly toward a user who interacted
    def rubber_band_adjustment(self, user, pull_strength=0.1):
        delta_x = pull_strength * (user.experiment_x - self.experiment_x)
        delta_y = pull_strength * (user.experiment_y - self.experiment_y)
        self.experiment_x = max(-5, min(5, self.experiment_x + delta_x))
        self.experiment_y = max(-5, min(5, self.experiment_y + delta_y))

    def __repr__(self):
        return f"Post({self.post_id}, User {self.user_id}, {self.quality}, {self.x}, {self.y}, {self.experiment_x}, {self.experiment_y}, {self.experiment_quality}, Likes: {self.likes}, Dislikes: {self.dislikes})"


# Generate a random value within a range
def generate_distribution_value(range_start=-2, range_end=2):
    return random.uniform(range_start, range_end)

# Create a list of users with diverse attributes
def create_users(num_users):
    users = []
    for user_id in range(1, num_users + 1):
        name = f"User{user_id}"
        quality = round(random.uniform(0, 1), 2)
        x = generate_distribution_value(-5, 5)
        y = generate_distribution_value(-5, 5)
        user_type = random.choices(['random', 'agree', 'quality', 'extremist'], [0.25, 0.25, 0.25, 0.25])[0]
        users.append(User(user_id, name, quality, x, y, user_type))
    return users

# Simulate interactions between users and posts
def run_simulation(num_users, num_posts_per_user):
    users = create_users(num_users)
    posts = []
    interaction_count = 0
    total_interactions = 0

    # Let each user create a set number of posts
    for user in users:
        for _ in range(num_posts_per_user):
            user.create_post(posts)

    # Have each user interact with all posts
    for user in users:
        for post in posts:
            action = user.decide_interaction(post)
            if action != 'none':
                interaction_count += 1
            total_interactions += 1
            post.interact(user)

    interaction_rate = interaction_count / total_interactions
    print(f"Interaction Rate: {interaction_rate:.2%}")

    return users, posts

# Test simulation and visualize results
def test_simulation():
    num_users = 100
    num_posts_per_user = 5

    users, posts = run_simulation(num_users, num_posts_per_user)

    # Load users and posts into dataframes
    user_df = pd.DataFrame([vars(user) for user in users])
    post_df = pd.DataFrame([vars(post) for post in posts])

    # Print the start of each dataframe
    print("Users DataFrame:")
    print(user_df.head())

    print("\nPosts DataFrame:")
    print(post_df.head())

    # Standard deviation calculations for differences between actual and experimental
    user_std_x = ((user_df['x'] - user_df['experiment_x']) ** 2).mean() ** 0.5
    user_std_y = ((user_df['y'] - user_df['experiment_y']) ** 2).mean() ** 0.5
    post_std_x = ((post_df['x'] - post_df['experiment_x']) ** 2).mean() ** 0.5
    post_std_y = ((post_df['y'] - post_df['experiment_y']) ** 2).mean() ** 0.5
    quality_std = ((post_df['quality'] * 10000 - post_df['experiment_quality']) ** 2).mean() ** 0.5

    print("\nStandard Deviations:")
    print(f"User X: {user_std_x:.2f}")
    print(f"User Y: {user_std_y:.2f}")
    print(f"Post X: {post_std_x:.2f}")
    print(f"Post Y: {post_std_y:.2f}")
    print(f"Quality: {quality_std:.2f}")

    # Visualizations
    # Heatmap for Users (Actual vs Experimental)
    plt.figure(figsize=(10, 8))

    plt.subplot(2, 1, 1)
    sns.kdeplot(
        x=user_df['x'],
        y=user_df['y'],
        cmap="Blues",
        fill=True,
        cbar=True,
        thresh=0
    )
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.title("User Distribution (Actual)")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")

    plt.subplot(2, 1, 2)
    sns.kdeplot(
        x=user_df['experiment_x'],
        y=user_df['experiment_y'],
        cmap="Greens",
        fill=True,
        cbar=True,
        thresh=0
    )
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.title("User Distribution (Experimental)")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")

    plt.tight_layout()
    plt.savefig("user_distributions_test2.png")

    # Heatmap for Posts (Actual vs Experimental)
    plt.figure(figsize=(10, 8))

    plt.subplot(2, 1, 1)
    sns.kdeplot(
        x=post_df['x'],
        y=post_df['y'],
        cmap="Reds",
        fill=True,
        cbar=True,
        thresh=0
    )
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.title("Post Distribution (Actual)")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")

    plt.subplot(2, 1, 2)
    sns.kdeplot(
        x=post_df['experiment_x'],
        y=post_df['experiment_y'],
        cmap="Purples",
        fill=True,
        cbar=True,
        thresh=0
    )
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    plt.title("Post Distribution (Experimental)")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")

    plt.tight_layout()
    plt.savefig("post_distributions_test2.png")

    # Bar chart for Top and Bottom 10 Posts (Quality)
    plt.figure(figsize=(12, 10))

    # Top 10 Posts by Actual Quality
    top_posts = post_df.sort_values(by='quality', ascending=False).head(10)
    bar_width = 0.4
    index = range(len(top_posts))

    plt.subplot(2, 1, 1)
    plt.bar(index, top_posts['experiment_quality'], bar_width, label='Experimental Quality', color='purple')
    plt.bar([i + bar_width for i in index], top_posts['quality'] * 10000, bar_width, label='Actual Quality', color='orange')

    plt.xlabel("Post ID")
    plt.ylabel("Quality")
    plt.title("Top 10 Posts by Experimental and Actual Quality")
    plt.xticks([i + bar_width / 2 for i in index], top_posts['post_id'].astype(str))
    plt.legend()

    # Bottom 10 Posts by Actual Quality
    bottom_posts = post_df.sort_values(by='quality').head(10)
    index = range(len(bottom_posts))

    plt.subplot(2, 1, 2)
    plt.bar(index, bottom_posts['experiment_quality'], bar_width, label='Experimental Quality', color='purple')
    plt.bar([i + bar_width for i in index], bottom_posts['quality'] * 10000, bar_width, label='Actual Quality', color='orange')

    plt.xlabel("Post ID")
    plt.ylabel("Quality")
    plt.title("Bottom 10 Posts by Experimental and Actual Quality")
    plt.xticks([i + bar_width / 2 for i in index], bottom_posts['post_id'].astype(str))
    plt.legend()

    plt.tight_layout()
    plt.savefig("post_quality_comparison_test2.png")

if __name__ == "__main__":
    test_simulation()
