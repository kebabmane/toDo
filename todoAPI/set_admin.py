import argparse
from app import create_app, db
from models import User, UserRole

def set_admin(username):
    """Assigns admin role to a user."""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"Found user: {user.username} (current role: {user.role})")
            user.role = UserRole.ADMIN
            db.session.commit()
            print(f"User {user.username} has been updated to role: {user.role.value}")
        else:
            print(f"User with username '{username}' not found.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set a user as an admin.')
    parser.add_argument('username', type=str, help='The username of the user to promote to admin.')
    args = parser.parse_args()
    set_admin(args.username)
