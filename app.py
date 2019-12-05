from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow 
from datetime import datetime
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

class User(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  email = db.Column(db.String(100))
  description = db.Column(db.String(250))

  def __init__(self, name, email, description):
    self.name = name
    self.email = email
    self.description = description

class Post(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), unique=True)
  description = db.Column(db.String(250))
  category = db.Column(db.String(50))
  topic = db.Column(db.String(50))
  body = db.Column(db.String(5000))
  tags = db.Column(db.String(200))
  upvote = db.Column(db.Integer)
  registered = db.Column(db.DateTime, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __init__(self, name, description, category, topic, body, tags):
    self.name = name
    self.description = description
    self.category = category
    self.topic = topic
    self.body = body
    self.tags = tags

class Category(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), unique=True)

  def __init__(self, name):
    self.name = name

class Comment(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(150))
  body = db.Column(db.String)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
  upvote = db.Column(db.Integer)
  downvote = db.Column(db.Integer)

  def __init__(self, title, body, upvote, downvote):
    self.title = title
    self.body = body
    self.upvote = upvote
    self.downvote = downvote

# SCHEMA
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'description')

class PostSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description', 'category', 'topic', 'body', 'tags')

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

class CommentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'body', 'upvote', 'downvote')

# INIT SCHEMA
user_schema = UserSchema()
users_schema = PostSchema(many=True)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

# Create a user
@app.route('/user', methods=['POST'])
def add_user():
  name = request.json['name']
  email = request.json['email']
  description = request.json['description']

  new_user = User(name, email, description)

  db.session.add(new_user)
  db.session.commit()

  return user_schema.jsonify(new_user)

@app.route('/post', methods=['POST'])
def add_post():
  name = request.json['name']
  description = request.json['description']
  category = request.json['category']
  topic = request.json['topic']
  body = request.json['body']
  tags = request.json['tags']

  new_post = Post(name, description, category, topic, body, tags)

  db.session.add(new_post)
  db.session.commit()

  return post_schema.jsonify(new_post)

@app.route('/category', methods=['POST'])
def add_category():
  name = request.json['name']
  
  new_category = Category(name)

  db.session.add(new_category)
  db.session.commit()

  return category_schema.jsonify(new_category)

@app.route('/comment', methods=['POST'])
def add_comment():
  title = request.json['title']
  body = request.json['body']
  upvote = request.json['upvote']
  downvote = request.json['downvote']

  new_comment = Comment(title, body, upvote, downvote)

  db.session.add(new_comment)
  db.session.commit()

  return comment_schema.jsonify(new_comment)

@app.route('/post', methods=['GET'])
def get_posts():
  all_posts = Post.query.all()
  result_posts = posts_schema.dump(all_posts)
  return jsonify(result_posts)

@app.route('/comment', methods=['GET'])
def get_comments():
  all_comments = Comment.query.all()
  result_comments = comments_schema.dump(all_comments)
  return jsonify(result_comments)

@app.route('/post/<id>', methods=['GET'])
def get_post(id):
  post = Post.query.get(id)
  return post_schema.jsonify(post)

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
  user = User.query.get(id)
  return user_schema.jsonify(user)

@app.route('/post/<id>', methods=['PUT'])
def update_post(id):
  post = Post.query.get(id)

  name = request.json['name']
  description = request.json['description']
  category = request.json['category']
  topic = request.json['topic']
  body = request.json['body']
  tags = request.json['tags']

  post.name = name
  post.description = description
  post.category = category
  post.topic = topic
  post.body = body
  post.tags = tags

  db.session.commit()

  return post_schema.jsonify(post)

# Run Server
if __name__ == '__main__':
  app.run(debug=True)