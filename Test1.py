import random
import math
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Define the User class to represent individual users in the simulation
class User:
    def __init__(self, user_id, name, quality, x, y, user_type):
        self.user_id = user_id
        self.name = name
        self.quality = quality  # User quality score between 0 and 1
        self.x = x  # Initial x-coordinate, constrained between -5 and 5
        self.y = y  # Initial y-coordinate, constrained between -5 and 5
        self.experiment_x = random.uniform(-2, 2)  # Experimental x-coordinate starts within a narrower range
        self.experiment_y = random.uniform(-2, 2)  # Experimental y-coordinate starts within a narrower range
        self.experiment_quality = 5000  # Default experimental quality, ranges between 0 and 10000
        self.user_type = user_type  # Determines interaction preferences ('random', 'agree', or 'quality')
        self.liked_posts_x = []
        self.liked_posts_y = []

    # Function to create a new post by the user
    def create_post(self, posts):
        quality = random.random()
        x = random.uniform(-5, 5)
        y = random.uniform(-5, 5)
        post_id = len(posts) + 1
        post = Post(post_id, self.user_id, quality, x, y)
        posts.append(post)

    # Decide whether to like, dislike, or ignore a post based on user type and various factors
    def decide_interaction(self, post):
        distance = ((self.experiment_x - post.experiment_x) ** 2 + (self.experiment_y - post.experiment_y) ** 2) ** 0.5
        quality_factor = post.experiment_quality / 10000

        if self.user_type == 'random':
            # Random interaction type
            return random.choices(['like', 'dislike', 'none'], [0.15, 0.15, 0.7])[0]
        elif self.user_type == 'agree':
            # Tends to interact positively if close in space or if quality is high
            prob_like = 0.4 * (1 - distance / 10) + 0.3 * quality_factor
            prob_dislike = 0.3 * (distance / 10) + 0.2 * (1 - quality_factor)
            return random.choices(['like', 'dislike', 'none'], [prob_like, prob_dislike, 1 - prob_like - prob_dislike])[0]
        elif self.user_type == 'quality':
            # Interaction is more influenced by quality
            prob_like = 0.5 * quality_factor + 0.2 * (1 - distance / 10)
            prob_dislike = 0.4 * (distance / 10) + 0.3 * (1 - quality_factor)
            return random.choices(['like', 'dislike', 'none'], [prob_like, prob_dislike, 1 - prob_like - prob_dislike])[0]

    # Adjust experimental coordinates based on liked posts
    def update_experiment_x_y(self, post):
        self.liked_posts_x.append(post.experiment_x)
        self.liked_posts_y.append(post.experiment_y)
        self.experiment_x = max(-5, min(5, sum(self.liked_posts_x) / len(self.liked_posts_x)))
        self.experiment_y = max(-5, min(5, sum(self.liked_posts_y) / len(self.liked_posts_y)))

    def __repr__(self):
        return f"User({self.user_id}, {self.name}, {self.quality}, {self.x}, {self.y}, {self.experiment_x}, {self.experiment_y}, {self.experiment_quality}, {self.user_type})"


# Define the Post class to represent posts created by users
class Post:
    def __init__(self, post_id, user_id, quality, x, y):
        self.post_id = post_id
        self.user_id = user_id
        self.quality = quality  # Post quality score between 0 and 1
        self.x = max(-5, min(5, x))  # Ensure x is within the range
        self.y = max(-5, min(5, y))  # Ensure y is within the range
        self.experiment_x = self.x  # Experimental x-coordinate
        self.experiment_y = self.y  # Experimental y-coordinate
        self.experiment_quality = 5000  # Default experimental quality, ranges between 0 and 10000
        self.likes = 0
        self.dislikes = 0
        self.total_likers_x = 0
        self.total_likers_y = 0
        self.num_likes = 0

    # Handle interaction from a user (like or dislike) and adjust metrics accordingly
    def interact(self, user):
        action = user.decide_interaction(self)
        distance = ((user.experiment_x - self.experiment_x) ** 2 + (user.experiment_y - self.experiment_y) ** 2) ** 0.5
        if action == 'like':
            self.likes += 1
            self.num_likes += 1
            self.total_likers_x += user.experiment_x
            self.total_likers_y += user.experiment_y

            # Adjust experimental coordinates based on likers
            self.experiment_x = max(-5, min(5, self.total_likers_x / self.num_likes))
            self.experiment_y = max(-5, min(5, self.total_likers_y / self.num_likes))

            # Boost experimental quality based on user interaction
            quality_boost = (1 - distance / 10) * user.experiment_quality / 10000
            self.experiment_quality = min(10000, self.experiment_quality + quality_boost * 100)

            # Update user's experimental coordinates
            user.update_experiment_x_y(self)

        elif action == 'dislike':
            self.dislikes += 1
            # Reduce experimental quality if disliked
            quality_drop = (1 - distance / 10) * user.experiment_quality / 10000
            self.experiment_quality = max(0, self.experiment_quality - quality_drop * 100)

    def __repr__(self):
        return f"Post({self.post_id}, User {self.user_id}, {self.quality}, {self.x}, {self.y}, {self.experiment_x}, {self.experiment_y}, {self.experiment_quality}, Likes: {self.likes}, Dislikes: {self.dislikes})"


# Generate a random value within a given range
def generate_distribution_value(range_start=-2, range_end=2):
    return random.uniform(range_start, range_end)

# Create a set of users with varied attributes
def create_users(num_users):
    users = []
    for user_id in range(1, num_users + 1):
        name = f"User{user_id}"
        quality = round(random.uniform(0, 1), 2)
        x = generate_distribution_value(-5, 5)
        y = generate_distribution_value(-5, 5)
        user_type = random.choices(['random', 'agree', 'quality'], [0.3, 0.4, 0.3])[0]
        users.append(User(user_id, name, quality, x, y, user_type))
    return users

# Simulate interactions between users and posts
def run_simulation(num_users, num_posts_per_user):
    users = create_users(num_users)
    posts = []
    interaction_count = 0
    total_interactions = 0

    # Each user creates multiple posts
    for user in users:
        for _ in range(num_posts_per_user):
            user.create_post(posts)

    # Users interact with each post
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

# Test the simulation and visualize results
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
    plt.savefig("user_distributions.png")

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
    plt.savefig("post_distributions.png")

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
    plt.savefig("post_quality_comparison.png")

if __name__ == "__main__":
    test_simulation()
