from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. تحديد مسار قاعدة البيانات (سيتم إنشاء ملف باسم sql_app.db تلقائياً في مشروعك)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# 2. إنشاء محرك الاتصال (Engine)
# ملاحظة: connect_args مطلوبة فقط مع SQLite لحمايته عند عمل عدة طلبات في نفس الوقت
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. إنشاء جلسة عمل (Session) مستقرة للتعامل مع العمليات (إضافة، تعديل، حذف)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. الفئة الأساسية (Base) التي سترث منها كل جداول المتجر لاحقاً
Base = declarative_base()

# 5. دالة مساعدة لفتح الاتصال بقاعدة البيانات وإغلاقه تلقائياً بعد انتهاء كل طلب (API Request)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()