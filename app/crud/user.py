from sqlalchemy.orm import Session
from app import models

def create_or_update(db: Session, user_data: dict):
    user = db.query(models.User).filter_by(spotify_id=user_data['spotify_id']).first()

    if user:
        user.display_name = user_data.get('display_name', user.display_name)
        user.email = user_data.get('email', user.email)
        user.access_token = user_data['access_token']
        user.refresh_token = user_data['refresh_token']
    else:
        user = models.User(**user_data)
        db.add(user)

    db.commit()
    db.refresh(user)
    return user