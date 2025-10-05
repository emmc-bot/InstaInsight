import instaloader
import os
import json
import time
import random
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import pandas as pd

class InstaInsight:
    def __init__(self):
        self.bot = instaloader.Instaloader()
        self.current_profile = None
        self.data_folder = "instagram_data"
        
        # Create data folder if it doesn't exist
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
    
    def login(self, username=None):
        """Login to Instagram"""
        try:
            if username:
                self.bot.interactive_login(username)
            else:
                print("⚠️  No username provided. Some features may be limited.")
            return True
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def load_profile(self, username):
        """Load an Instagram profile"""
        try:
            self.current_profile = instaloader.Profile.from_username(self.bot.context, username)
            print(f"✅ Loaded profile: @{username}")
            return True
        except Exception as e:
            print(f"❌ Failed to load profile: {e}")
            return False
    
    def basic_profile_info(self):
        """Display basic profile information"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        print("\n" + "="*60)
        print(f"📊 PROFILE ANALYSIS: @{self.current_profile.username}")
        print("="*60)
        
        info = {
            "User ID": self.current_profile.userid,
            "Posts": f"{self.current_profile.mediacount:,}",
            "Followers": f"{self.current_profile.followers:,}",
            "Following": f"{self.current_profile.followees:,}",
            "Follow Ratio": f"{self.current_profile.followers/self.current_profile.followees:.2f}" if self.current_profile.followees > 0 else "N/A",
            "Bio": self.current_profile.biography[:100] + "..." if len(self.current_profile.biography) > 100 else self.current_profile.biography,
            "External URL": self.current_profile.external_url or "None",
            "Private Account": "Yes" if self.current_profile.is_private else "No",
            "Verified": "Yes" if self.current_profile.is_verified else "No"
        }
        
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    def follower_analysis(self, max_followers=100):
        """Analyze followers and following"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        print(f"\n👥 ANALYZING FOLLOWERS (first {max_followers})...")
        
        try:
            # Get followers and followees with safety limits
            followers = []
            followees = []
            
            for i, follower in enumerate(self.current_profile.get_followers()):
                if i >= max_followers:
                    break
                followers.append(follower.username)
                time.sleep(random.uniform(0.5, 1.5))
            
            for i, followee in enumerate(self.current_profile.get_followees()):
                if i >= max_followers:
                    break
                followees.append(followee.username)
                time.sleep(random.uniform(0.5, 1.5))
            
            # Analysis
            not_following_back = set(followees) - set(followers)
            not_followed_back = set(followers) - set(followees)
            
            print(f"✅ Followers analyzed: {len(followers)}")
            print(f"✅ Following analyzed: {len(followees)}")
            print(f"❌ You don't follow back: {len(not_followed_back)}")
            print(f"❌ Don't follow you back: {len(not_following_back)}")
            
            # Save to file
            analysis_data = {
                'timestamp': datetime.now().isoformat(),
                'profile': self.current_profile.username,
                'followers_count': len(followers),
                'following_count': len(followees),
                'not_following_back': list(not_following_back)[:20],  # First 20
                'not_followed_back': list(not_followed_back)[:20]
            }
            
            self._save_to_json(analysis_data, f"follower_analysis_{self.current_profile.username}")
            
            return followers, followees, not_following_back, not_followed_back
            
        except Exception as e:
            print(f"❌ Error in follower analysis: {e}")
            return [], [], [], []
    
    def mutual_friends_finder(self, target_username):
        """Find mutual friends between current profile and target profile"""
        print(f"\n🤝 FINDING MUTUAL FRIENDS WITH @{target_username}...")
        
        try:
            target_profile = instaloader.Profile.from_username(self.bot.context, target_username)
            
            # Get limited followers from both profiles
            current_followers = set()
            target_followers = set()
            
            for i, follower in enumerate(self.current_profile.get_followers()):
                if i >= 50:  # Limit for performance
                    break
                current_followers.add(follower.username)
                time.sleep(0.5)
            
            for i, follower in enumerate(target_profile.get_followers()):
                if i >= 50:  # Limit for performance
                    break
                target_followers.add(follower.username)
                time.sleep(0.5)
            
            mutual_friends = current_followers.intersection(target_followers)
            
            print(f"✅ Found {len(mutual_friends)} mutual friends:")
            for friend in list(mutual_friends)[:10]:  # Show first 10
                print(f"  👤 {friend}")
            
            return mutual_friends
            
        except Exception as e:
            print(f"❌ Error finding mutual friends: {e}")
            return set()
    
    def post_performance_analyzer(self, post_limit=10):
        """Analyze post performance"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        print(f"\n📈 ANALYZING LAST {post_limit} POSTS...")
        
        posts_data = []
        
        try:
            for i, post in enumerate(self.current_profile.get_posts()):
                if i >= post_limit:
                    break
                
                engagement_rate = (post.likes + post.comments) / self.current_profile.followers * 100 if self.current_profile.followers > 0 else 0
                
                posts_data.append({
                    'post_number': i + 1,
                    'date': post.date.strftime("%Y-%m-%d"),
                    'likes': post.likes,
                    'comments': post.comments,
                    'engagement_rate': engagement_rate,
                    'caption_preview': post.caption[:30] + '...' if post.caption else 'No caption',
                    'is_video': post.is_video
                })
                
                time.sleep(0.5)
            
            # Sort by engagement rate
            posts_data.sort(key=lambda x: x['engagement_rate'], reverse=True)
            
            print("🏆 TOP PERFORMING POSTS:")
            for i, post in enumerate(posts_data[:5]):
                print(f"  {i+1}. Engagement: {post['engagement_rate']:.2f}% | "
                      f"Likes: {post['likes']} | Date: {post['date']}")
            
            # Save analysis
            self._save_to_json(posts_data, f"post_analysis_{self.current_profile.username}")
            
            return posts_data
            
        except Exception as e:
            print(f"❌ Error analyzing posts: {e}")
            return []
    
    def download_content(self, content_type="posts", limit=5):
        """Download posts or stories"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        target_folder = f"{self.data_folder}/{self.current_profile.username}_{content_type}"
        
        try:
            if content_type == "posts":
                print(f"\n📥 DOWNLOADING LAST {limit} POSTS...")
                posts = self.current_profile.get_posts()
                
                for i, post in enumerate(posts):
                    if i >= limit:
                        break
                    self.bot.download_post(post, target=target_folder)
                    print(f"  ✅ Downloaded post {i+1}")
                    time.sleep(1)
                    
            elif content_type == "stories":
                print(f"\n📖 DOWNLOADING STORIES...")
                # Note: Stories download requires login
                for story in self.bot.get_stories([self.current_profile.userid]):
                    for item in story.get_items():
                        self.bot.download_storyitem(item, target=target_folder)
                        print(f"  ✅ Downloaded story from {item.date}")
            
            print(f"✅ Content saved to: {target_folder}")
            
        except Exception as e:
            print(f"❌ Error downloading content: {e}")
    
    def generate_report(self):
        """Generate a comprehensive report"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        print(f"\n📋 GENERATING COMPREHENSIVE REPORT FOR @{self.current_profile.username}...")
        
        # Basic info
        self.basic_profile_info()
        
        # Follower analysis
        followers, followees, not_following_back, not_followed_back = self.follower_analysis(50)
        
        # Post analysis
        posts_data = self.post_performance_analyzer(10)
        
        # Save comprehensive report
        report = {
            'generated_at': datetime.now().isoformat(),
            'profile': self.current_profile.username,
            'basic_info': {
                'user_id': self.current_profile.userid,
                'posts': self.current_profile.mediacount,
                'followers': self.current_profile.followers,
                'following': self.current_profile.followees,
                'is_private': self.current_profile.is_private,
                'is_verified': self.current_profile.is_verified
            },
            'follower_analysis': {
                'followers_analyzed': len(followers),
                'following_analyzed': len(followees),
                'not_following_back_count': len(not_following_back),
                'not_followed_back_count': len(not_followed_back)
            },
            'post_analysis': {
                'posts_analyzed': len(posts_data),
                'average_engagement': sum(p['engagement_rate'] for p in posts_data) / len(posts_data) if posts_data else 0,
                'top_posts': posts_data[:3] if posts_data else []
            }
        }
        
        self._save_to_json(report, f"comprehensive_report_{self.current_profile.username}")
        print(f"✅ Comprehensive report generated and saved!")
    
    def _save_to_json(self, data, filename):
        """Save data to JSON file"""
        filepath = f"{self.data_folder}/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

def main():
    """Main function to run the InstaInsight dashboard"""
    analyzer = InstaInsight()
    
    print("🚀 WELCOME TO INSTAINSIGHT - INSTAGRAM ANALYTICS DASHBOARD")
    print("="*60)
    
    while True:
        print("\n📋 MAIN MENU:")
        print("1. Load Profile")
        print("2. Login to Instagram")
        print("3. Basic Profile Info")
        print("4. Follower Analysis")
        print("5. Find Mutual Friends")
        print("6. Post Performance Analysis")
        print("7. Download Content")
        print("8. Generate Comprehensive Report")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            username = input("Enter Instagram username: ").strip()
            analyzer.load_profile(username)
            
        elif choice == '2':
            username = input("Enter your Instagram username: ").strip()
            analyzer.login(username)
            
        elif choice == '3':
            analyzer.basic_profile_info()
            
        elif choice == '4':
            analyzer.follower_analysis()
            
        elif choice == '5':
            target_user = input("Enter target username to find mutual friends: ").strip()
            analyzer.mutual_friends_finder(target_user)
            
        elif choice == '6':
            analyzer.post_performance_analyzer()
            
        elif choice == '7':
            print("Download options:")
            print("1. Posts")
            print("2. Stories (requires login)")
            dl_choice = input("Choose content type (1-2): ").strip()
            if dl_choice == '1':
                analyzer.download_content("posts", 5)
            elif dl_choice == '2':
                analyzer.download_content("stories", 5)
            
        elif choice == '8':
            analyzer.generate_report()
            
        elif choice == '9':
            print("👋 Thank you for using InstaInsight!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()