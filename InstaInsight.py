import instaloader
import os
import json
import time
import random
from datetime import datetime

class InstaInsight:
    def __init__(self):
        self.bot = instaloader.Instaloader()
        self.current_profile = None
        self.data_folder = "instagram_data"
        self.request_count = 0
        self.last_request_time = time.time()
        
        # Rate limiting settings
        self.MIN_DELAY = 5
        self.MAX_DELAY = 10
        
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
    
    def safe_request(self):
        """Add delay between all requests to avoid rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.MIN_DELAY:
            wait_time = self.MIN_DELAY - time_since_last
            print(f"⏳ Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        if self.request_count % 10 == 0:
            long_wait = random.uniform(15, 30)
            print(f"⏳ Longer delay after {self.request_count} requests: {long_wait:.1f} seconds...")
            time.sleep(long_wait)
    
    def can_access_followers(self, profile):
        """Check if we can access followers for a profile"""
        print(f"🔍 Checking follower access for @{profile.username}...")
        
        # Check if profile is private
        if profile.is_private:
            print("❌ Cannot access followers - Profile is private")
            return False
        
        # Check if we're logged in (required for some access)
        try:
            # Try to get just 1 follower to test access
            test_follower = None
            for follower in profile.get_followers():
                test_follower = follower
                break
            
            if test_follower:
                print("✅ Can access followers!")
                return True
            else:
                print("❌ No followers accessible")
                return False
                
        except Exception as e:
            print(f"❌ Cannot access followers: {e}")
            return False
    
    def login(self, username=None):
        """Login to Instagram"""
        try:
            if username:
                print(f"🔐 Attempting to log in as @{username}...")
                self.bot.interactive_login(username)
                print("✅ Login successful!")
                return True
            else:
                print("⚠️  No username provided. Using public access (limited features).")
                return False
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def load_profile(self, username):
        """Load an Instagram profile"""
        try:
            self.safe_request()
            self.current_profile = instaloader.Profile.from_username(self.bot.context, username)
            print(f"✅ Loaded profile: @{username}")
            
            # Check if we can access followers
            self.can_access_followers(self.current_profile)
            
            time.sleep(random.uniform(3, 6))
            return True
        except Exception as e:
            print(f"❌ Failed to load profile: {e}")
            return False
    
    def basic_profile_info(self):
        """Display basic profile information"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        print("\n" + "="*50)
        print(f"📊 PROFILE INFO: @{self.current_profile.username}")
        print("="*50)
        
        print(f"Username: {self.current_profile.username}")
        print(f"User ID: {self.current_profile.userid}")
        print(f"Number of Posts: {self.current_profile.mediacount}")
        print(f"Followers: {self.current_profile.followers}")
        print(f"Following: {self.current_profile.followees}")
        print(f"Bio: {self.current_profile.biography}")
        print(f"External URL: {self.current_profile.external_url}")
        print(f"Private Account: {'Yes' if self.current_profile.is_private else 'No'}")
        print(f"Verified: {'Yes' if self.current_profile.is_verified else 'No'}")
        
        # Show follower access status
        can_access = self.can_access_followers(self.current_profile)
        print(f"Follower Access: {'✅ Available' if can_access else '❌ Restricted'}")
    
    def get_followers_list(self, limit=20):
        """Get list of followers with access checks"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return []
        
        # Check if we can access followers first
        if not self.can_access_followers(self.current_profile):
            print("❌ Cannot get followers - access restricted")
            return []
        
        print(f"\n📥 Getting followers (first {limit})...")
        followers = []
        
        try:
            for i, follower in enumerate(self.current_profile.get_followers()):
                if i >= limit:
                    break
                followers.append(follower.username)
                if (i + 1) % 5 == 0:
                    print(f"  - Collected {i + 1} followers...")
                time.sleep(2)  # Increased delay for follower access
            
            print(f"✅ Successfully collected {len(followers)} followers")
            return followers
            
        except Exception as e:
            print(f"❌ Error getting followers: {e}")
            return []
    
    def get_following_list(self, limit=20):
        """Get list of people you follow with access checks"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return []
        
        # Check if we can access following first
        if not self.can_access_followers(self.current_profile):
            print("❌ Cannot get following - access restricted")
            return []
        
        print(f"\n📥 Getting following (first {limit})...")
        followees = []
        
        try:
            for i, followee in enumerate(self.current_profile.get_followees()):
                if i >= limit:
                    break
                followees.append(followee.username)
                if (i + 1) % 5 == 0:
                    print(f"  - Collected {i + 1} following...")
                time.sleep(2)  # Increased delay for following access
            
            print(f"✅ Successfully collected {len(followees)} following")
            return followees
            
        except Exception as e:
            print(f"❌ Error getting following: {e}")
            return []
    
    def follower_analysis(self):
        """Analyze followers and following with proper access checks"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        print("\n👥 ANALYZING FOLLOWERS...")
        
        # Check access first
        if not self.can_access_followers(self.current_profile):
            print("❌ Cannot perform follower analysis - access restricted")
            print("💡 Try logging in or check if the profile is private")
            return [], []
        
        followers = self.get_followers_list(15)  # Reduced limit
        followees = self.get_following_list(15)  # Reduced limit
        
        if followers and followees:
            not_following_back = set(followees) - set(followers)
            not_followed_back = set(followers) - set(followees)
            
            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"Followers analyzed: {len(followers)}")
            print(f"Following analyzed: {len(followees)}")
            print(f"Not following you back: {len(not_following_back)}")
            print(f"You don't follow back: {len(not_followed_back)}")
            
            if not_following_back:
                print(f"\n❌ Not following you back (first 5):")
                for user in list(not_following_back)[:5]:
                    print(f"  - {user}")
            
            # Save to file
            analysis_data = {
                'timestamp': datetime.now().isoformat(),
                'profile': self.current_profile.username,
                'followers_sample': followers,
                'following_sample': followees,
                'not_following_back_count': len(not_following_back),
                'not_followed_back_count': len(not_followed_back)
            }
            
            self._save_to_json(analysis_data, f"follower_analysis_{self.current_profile.username}")
            
            return followers, followees
        else:
            print("❌ Could not get follower data")
            return [], []
    
    def mutual_friends_finder(self, target_username):
        """Find mutual friends with proper access checks"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        print(f"\n🤝 FINDING MUTUAL FRIENDS WITH @{target_username}...")
        
        try:
            # Load target profile
            target_profile = instaloader.Profile.from_username(self.bot.context, target_username)
            print(f"✅ Loaded target profile: @{target_username}")
            
            # Check access for both profiles
            print("🔍 Checking access to your followers...")
            if not self.can_access_followers(self.current_profile):
                print("❌ Cannot access your followers")
                return []
            
            print("🔍 Checking access to target's followers...")
            if not self.can_access_followers(target_profile):
                print("❌ Cannot access target's followers")
                return []
            
            # Get followers from both profiles
            print("📥 Getting your followers...")
            your_followers = self.get_followers_list(10)  # Reduced limit
            
            print("📥 Getting target's followers...")
            target_followers = []
            for i, follower in enumerate(target_profile.get_followers()):
                if i >= 10:  # Reduced limit
                    break
                target_followers.append(follower.username)
                if (i + 1) % 3 == 0:
                    print(f"  - Collected {i + 1} target followers...")
                time.sleep(2)  # Increased delay
            
            # Find mutual friends
            mutual_friends = set(your_followers) & set(target_followers)
            
            print(f"\n📊 MUTUAL FRIENDS RESULTS:")
            print(f"Your followers checked: {len(your_followers)}")
            print(f"Their followers checked: {len(target_followers)}")
            print(f"Mutual friends found: {len(mutual_friends)}")
            
            if mutual_friends:
                print(f"\n👥 Mutual friends with @{target_username}:")
                for i, friend in enumerate(list(mutual_friends)[:10]):
                    print(f"  {i+1}. {friend}")
            else:
                print("😞 No mutual friends found in the samples checked")
            
            return list(mutual_friends)
            
        except Exception as e:
            print(f"❌ Error finding mutual friends: {e}")
            return []
    
    def simple_follower_check(self):
        """Simple function to just login and check followers"""
        if not self.current_profile:
            print("❌ No profile loaded!")
            return
        
        print(f"\n🔍 SIMPLE FOLLOWER CHECK FOR @{self.current_profile.username}")
        print("="*50)
        
        # Check access first
        if not self.can_access_followers(self.current_profile):
            print("❌ Cannot access followers for this profile")
            print("💡 Possible reasons:")
            print("   - Profile is private")
            print("   - You need to be logged in")
            print("   - You don't follow this private account")
            print("   - Instagram is blocking access")
            return
        
        # Get a small sample of followers
        print("📥 Getting follower sample...")
        followers = self.get_followers_list(10)  # Just 10 followers
        
        if followers:
            print(f"\n👥 First {len(followers)} followers of @{self.current_profile.username}:")
            for i, follower in enumerate(followers, 1):
                print(f"  {i}. {follower}")
        else:
            print("❌ Could not retrieve any followers")
    
    def _save_to_json(self, data, filename):
        """Save data to JSON file"""
        filepath = f"{self.data_folder}/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to: {filepath}")
        return filepath

def main():
    """Main function to run the InstaInsight dashboard"""
    analyzer = InstaInsight()
    
    print("🚀 INSTAINSIGHT - FOLLOWER ACCESS CHECKER")
    print("="*50)
    print("Focus: Login and check follower access")
    print("="*50)
    
    while True:
        print("\n📋 MAIN MENU:")
        print("1. Load Profile")
        print("2. Login to Instagram") 
        print("3. Show Profile Info + Access Check")
        print("4. Simple Follower Check")
        print("5. Follower Analysis")
        print("6. Find Mutual Friends")
        print("7. Exit")
        
        choice = input("\nChoose an option (1-7): ").strip()
        
        if choice == '1':
            username = input("Enter Instagram username: ").strip()
            analyzer.load_profile(username)
            
        elif choice == '2':
            username = input("Enter your Instagram username: ").strip()
            analyzer.login(username)
            
        elif choice == '3':
            analyzer.basic_profile_info()
            
        elif choice == '4':
            analyzer.simple_follower_check()
            
        elif choice == '5':
            analyzer.follower_analysis()
            
        elif choice == '6':
            if not analyzer.current_profile:
                print("❌ Please load a profile first!")
            else:
                target = input("Enter target username: ").strip()
                if target:
                    analyzer.mutual_friends_finder(target)
                else:
                    print("❌ Please enter a username")
            
        elif choice == '7':
            print("👋 Thank you for using InstaInsight!")
            break
            
        else:
            print("❌ Invalid choice")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
