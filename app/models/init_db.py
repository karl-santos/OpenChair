from app.models.database import engine, Base
from app.models.models import SlotSnapshot, Subscription, NotificationLog

def init_database():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized!")

if __name__ == "__main__":
    init_database()