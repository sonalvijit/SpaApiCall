from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user

def handle_index():
     return jsonify(msg="Welcome to API"), 200

def handle_restricted_area():
     return jsonify(message="If you are seeing this that means you have cookie man"), 200

def handle_register(User, db, data):
     username = data.get("username")
     email = data.get("email")
     password = data.get("password")

     existing_user = User.query.filter((User.username == username) | (User.email == email)).first()

     if existing_user:
          return jsonify({"error":"Username or email already exists"}), 400
     
     user = User(username=username, email=email, password=generate_password_hash(password))
     db.session.add(user)
     db.session.commit()
     return jsonify({"message":"User registered successfully"}), 201

def handle_login(User, data):
     username = data.get("username")
     password = data.get("password")

     registered_user = User.query.filter_by(username=username).first()
     if registered_user and registered_user.check_hash(password):
          # if check_password_hash(registered_user.password, password):
          login_user(registered_user)
          return jsonify({"message":"User logged in successfully!"}), 200
     
     return jsonify({"error":"Something went wrong!"}), 400

def handle_view_profile(User, username):
     user = User.query.filter_by(username=username).first()
     if user:
          return jsonify({
               "username":user.username,
               "email":user.email
          }), 200
     
     return jsonify({"error":"Unable to find username"}), 400

def handle_create_tweet(Tweet, user_id, data, db):
     tweet = data.get("tweet")
     a_ = Tweet(tweet=tweet, user_id=user_id)
     db.session.add(a_)
     db.session.commit()
     if a_:
          return jsonify({"message":"tweet posted successfully!"}), 201
     
     return jsonify({"error":"Unable to tweet!"}), 400

def handle_like_tweet(LikeTweet, tweet_id, current_user ,db):
     like_ = LikeTweet(user_id=current_user, tweet_id=tweet_id)
     db.session.add(like_)
     db.session.commit()
     if like_:
          return jsonify({"data":[{"liked_tweet":tweet_id,"status_code":201}]}), 201
     
     return jsonify({"error":"Unable to like tweet!"}), 400

def handle_fetch_tweet(Tweet, LikeTweet):
     tweets = Tweet.query.order_by(Tweet.date_created.desc()).all()
     if tweets:
          return jsonify([{"tweet_id":t.id,"tweet":t.tweet,"created_by":t.author.username,"created_at":t.date_created,"likes":LikeTweet.query.filter_by(tweet_id=t.id).count(),"comments":[{"comment_id":c.id,"comment":c.comment,"date_created":c.date_created} for c in t.comments]} for t in tweets]), 200
     return jsonify({"error":"No tweets in database!"}), 400

def handle_fetch_tweet_by_id(Tweet, LikeTweet, tweet_id):
     tweet = Tweet.query.filter_by(id=tweet_id).first()
     if not tweet:
          return jsonify({"error":"Tweet not found!"}), 404
     
     comments = [{"comment_id":c.id,"comment":c.comment,"date_created":c.date_created} for c in tweet.comments]
     likes = LikeTweet.query.filter_by(tweet_id=tweet.id).count()

     return jsonify({
          "tweet_id":tweet.id,
          "tweet":tweet.tweet,
          "created_by":tweet.author.username,
          "created_at":tweet.date_created,
          "likes":likes,
          "comments":comments
     }), 200

def handle_create_comment(Comment, user_id, tweet_id, data, db):
     comments = Comment(comment=data.get("comment"),user_id=user_id,tweet_id=tweet_id)
     db.session.add(comments)
     db.session.commit()
     if comments:
          return jsonify({"message":"Commentted successfully!"}), 201

     return jsonify({"errror":"Something went wrong!"}), 400

def handle_like_comment(LikeComment, comment_id, current_user, db):
     like_ = LikeComment(user_id=current_user, comment_id=comment_id)
     db.session.add(like_)
     db.session.commit()
     if like_:
          return jsonify({"data":[{"liked_comment":comment_id,"status_code":201}]}), 201
     
     return jsonify({"error":"Unable to like comment!"}), 400

def handle_follow_user(username, User, current_user, Followers, db):
     if not username:
          return jsonify({"error":"Username required!"}), 400
     
     user_to_follow = User.query.filter_by(username=username).first()
     if not user_to_follow:
          return jsonify({"error":"User not found"}), 404
     
     if user_to_follow.id == current_user:
          return jsonify({"error":"You cannot follow yourself!"}), 400
     
     existing_follow = Followers.query.filter_by(follower_id=current_user, followed_id=user_to_follow.id).first()

     if existing_follow:
          return jsonify({"message":"already following this user"}), 400
     
     new_follow = Followers(follower_id=current_user, followed_id=user_to_follow.id)
     db.session.add(new_follow)
     db.session.commit()

     return jsonify({"message":f"You are now following {user_to_follow.username}"}), 201

def handle_unfollow_user(username, User, current_user, Followers, db):
     if not username:
          return jsonify({"error":"Username is required!"}), 400
     
     user_to_unfollow = User.query.filter_by(username=username).first()
     if not user_to_unfollow:
          return jsonify({"error":"User not found"}), 404
     
     follow = Followers.query.filter_by(follower_id=current_user, followed_id=user_to_unfollow.id).first()
     if not follow:
          return jsonify({"error":"You are not following this user"}), 400
     
     db.session.delete(follow)
     db.session.commit()
     return jsonify({"message":f"You have unfollowed {user_to_unfollow.username}"}), 200

def handle_view_followers(User, username):
     if not username:
          return jsonify({"error":"Username required!"}), 400
     
     user = User.query.filter_by(username=username).first()
     if not user:
          return jsonify({"error":"User not found"}), 404
     
     followers = [
          {"id":f.follower.id,"username":f.follower.username} for f in user.followers
     ]

     return jsonify({
          "followers":followers,
          "count":len(followers)
     }), 200

def handle_view_followings(User, username):
     if not username:
          return jsonify({"error":"Username required!"}), 400
     
     user = User.query.filter_by(username=username).first()
     if not user:
          return jsonify({"error":"User not found"}), 404
     
     followings = [
          {"id":f.followed.id, "username":f.followed.username} for f in user.following
     ]

     return jsonify({"followings":followings,"count":len(followings)}), 200

def handle_get_deepdown_database(User, Tweet, LikeTweet, Comment, LikeComment, Followers):
     users = User.query.all()
     tweets = Tweet.query.all()
     likes = LikeTweet.query.all()
     comments = Comment.query.all()
     like_comments = LikeComment.query.all()
     followers = Followers.query.all()

     return jsonify({
          "users":[{"id":u.id,"username":u.username,"email":u.email} for u in users],
          "tweets":[{"id":t.id,"tweet":t.tweet,"user_id":t.user_id} for t in tweets],
          "likes":[{"id":l.id,"user_id":l.user_id,"tweet_id":l.tweet_id} for l in likes],
          "comments":[{"id":c.id,"comment":c.comment,"user_id":c.user_id,"tweet_id":c.tweet_id} for c in comments],
          "like_comments":[{"id":lc.id,"user_id":lc.user_id,"comment_id":lc.comment_id} for lc in like_comments],
          "followers":[{"follower_id":f.follower_id,"followed_id":f.followed_id} for f in followers]
     }), 200

def handle_fetch_user_by_id(User, user_id):
     user = User.query.filter_by(id=user_id).first()
     if not user:
          return jsonify({"error": "User not found!"}), 404
     
     followers = [{"id": f.follower.id, "username": f.follower.username} for f in user.followers]
     
     return jsonify({
          "id": user.id,
          "username": user.username,
          "followers_count": len(followers),
          "followers": followers
     }), 200

def handle_trending_users(db, func, desc, User, Tweet, LikeTweet, Comment, LikeComment, Followers):
    # Get follower count per user
    follower_counts = db.session.query(
        Followers.followed_id.label('user_id'),
        func.count(Followers.follower_id).label('follower_count')
    ).group_by(Followers.followed_id).subquery()

    # Get tweet like count per user
    tweet_like_counts = db.session.query(
        Tweet.user_id.label('user_id'),
        func.count(LikeTweet.id).label('tweet_like_count')
    ).join(LikeTweet, Tweet.id == LikeTweet.tweet_id).group_by(Tweet.user_id).subquery()

    # Get comment like count per user
    comment_like_counts = db.session.query(
        Comment.user_id.label('user_id'),
        func.count(LikeComment.id).label('comment_like_count')
    ).join(LikeComment, Comment.id == LikeComment.comment_id).group_by(Comment.user_id).subquery()

    # Combine everything and calculate a "trending score"
    trending_users = db.session.query(
        User.id,
        User.username,
        func.coalesce(follower_counts.c.follower_count, 0).label('followers'),
        func.coalesce(tweet_like_counts.c.tweet_like_count, 0).label('tweet_likes'),
        func.coalesce(comment_like_counts.c.comment_like_count, 0).label('comment_likes'),
        (
            func.coalesce(follower_counts.c.follower_count, 0) * 2 +
            func.coalesce(tweet_like_counts.c.tweet_like_count, 0) * 1.5 +
            func.coalesce(comment_like_counts.c.comment_like_count, 0)
        ).label('trending_score')
    ).outerjoin(follower_counts, User.id == follower_counts.c.user_id
    ).outerjoin(tweet_like_counts, User.id == tweet_like_counts.c.user_id
    ).outerjoin(comment_like_counts, User.id == comment_like_counts.c.user_id
    ).order_by(desc('trending_score')).limit(10).all()

    # Format the result
    result = [{
        "user_id": u.id,
        "username": u.username,
        "followers": int(u.followers),
        "tweet_likes": int(u.tweet_likes),
        "comment_likes": int(u.comment_likes),
        "trending_score": float(u.trending_score)
    } for u in trending_users]

    return jsonify(result)

def handle_view_profile(User, username):
     user = User.query.filter_by(username=username).first()
     if not user:
          return jsonify({"error": "User not found"}), 404
     
     followers = [{"id": f.follower.id, "username": f.follower.username} for f in user.followers]
     followings = [{"id": f.followed.id, "username": f.followed.username} for f in user.following]
     tweets = [{"id": t.id, "tweet": t.tweet, "created_at": t.date_created} for t in user.tweets]

     return jsonify({
          "user_id": user.id,
          "username": user.username,
          "followers_count": len(followers),
          "followings_count": len(followings),
          "followers": followers,
          "followings": followings,
          "tweets": tweets
     }), 200

def handle_followers_count(User, username, Followers):
     if not username:
          return jsonify({"error":"Username required!"}), 400
     
     user = User.query.filter_by(username=username).first()
     if not user:
          return jsonify({"error":"User not found"}), 404
     
     followers_count = Followers.query.filter_by(followed_id=user.id).count()

     return jsonify({
          "followers_count":followers_count
     }), 200

def handle_get_most_followed_users(User, Followers, db, func, desc):
     most_followed_users = db.session.query(
          User.id,
          User.username,
          func.count(Followers.follower_id).label('followers_count')
     ).join(Followers, User.id == Followers.followed_id
     ).group_by(User.id
     ).order_by(desc('followers_count')).limit(10).all()

     result = [{
          "user_id": u.id,
          "username": u.username,
          "followers_count": int(u.followers_count)
     } for u in most_followed_users]

     return jsonify(result)

def handle_view_profile_integer(User, username):
     user = User.query.filter_by(id=username).first()
     if not user:
          return jsonify({"error": "User not found"}), 404
     
     followers = [{"id": f.follower.id, "username": f.follower.username} for f in user.followers]
     followings = [{"id": f.followed.id, "username": f.followed.username} for f in user.following]
     tweets = [{"id": t.id, "tweet": t.tweet, "created_at": t.date_created} for t in user.tweets]

     return jsonify({
          "user_id": user.id,
          "username": user.username,
          "followers_count": len(followers),
          "followings_count": len(followings),
          "followers": followers,
          "followings": followings,
          "tweets": tweets
     }), 200