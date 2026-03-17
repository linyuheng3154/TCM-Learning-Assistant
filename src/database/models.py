"""
数据库模型 - Database Models

SQLite 数据库表结构定义。

AI协作说明：
- 使用 SQLAlchemy 风格的表定义
- 支持与 Pydantic 模型的转换
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


class FormulaDB(Base):
    """方剂表"""
    __tablename__ = "formulas"
    
    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    pinyin = Column(String(200))
    pinyin_initials = Column(String(50), index=True)  # 拼音首字母，如 'gzt'
    efficacy = Column(Text)
    indications = Column(Text)
    contraindications = Column(Text)
    usage = Column(Text)
    source = Column(String(200))
    category = Column(String(100), index=True)
    modern_research = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    compositions = relationship("HerbCompositionDB", back_populates="formula", cascade="all, delete-orphan")
    aliases = relationship("FormulaAliasDB", back_populates="formula", cascade="all, delete-orphan")
    clinical_cases = relationship("ClinicalCaseDB", back_populates="formula", cascade="all, delete-orphan")


class HerbDB(Base):
    """药材表"""
    __tablename__ = "herbs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    pinyin = Column(String(100))
    nature = Column(String(20))  # 寒热温凉
    flavor = Column(String(50))  # 酸苦甘辛咸
    meridian = Column(String(100))  # 归经
    efficacy = Column(Text)
    indications = Column(Text)
    contraindications = Column(Text)
    dosage = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class HerbCompositionDB(Base):
    """方剂组成表（方剂-药材关联表）"""
    __tablename__ = "herb_compositions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formula_id = Column(String(10), ForeignKey("formulas.id"), nullable=False)
    herb_name = Column(String(50), nullable=False, index=True)
    dosage = Column(String(30))
    role = Column(String(10))  # 君臣佐使
    note = Column(Text)
    
    # 关系
    formula = relationship("FormulaDB", back_populates="compositions")


class FormulaAliasDB(Base):
    """方剂别名表"""
    __tablename__ = "formula_aliases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formula_id = Column(String(10), ForeignKey("formulas.id"), nullable=False)
    alias = Column(String(100), nullable=False)
    
    # 关系
    formula = relationship("FormulaDB", back_populates="aliases")


class ClinicalCaseDB(Base):
    """医案引用表"""
    __tablename__ = "clinical_cases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    formula_id = Column(String(10), ForeignKey("formulas.id"), nullable=False)
    case_text = Column(Text, nullable=False)
    
    # 关系
    formula = relationship("FormulaDB", back_populates="clinical_cases")


class SyndromeDB(Base):
    """证型表"""
    __tablename__ = "syndromes"
    
    id = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    keywords = Column(Text)  # JSON 格式存储
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    formula_relations = relationship("SyndromeFormulaDB", back_populates="syndrome", cascade="all, delete-orphan")


class SyndromeFormulaDB(Base):
    """证型-方剂关联表"""
    __tablename__ = "syndrome_formulas"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    syndrome_id = Column(String(10), ForeignKey("syndromes.id"), nullable=False)
    formula_id = Column(String(10), ForeignKey("formulas.id"), nullable=False)
    
    # 关系
    syndrome = relationship("SyndromeDB", back_populates="formula_relations")


class DataMetadataDB(Base):
    """数据元信息表"""
    __tablename__ = "data_metadata"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# 数据库引擎和会话工厂
_engine = None
_SessionLocal = None


def get_engine(db_path: str = "data/tcm.db"):
    """获取数据库引擎"""
    global _engine
    if _engine is None:
        _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    return _engine


def get_session():
    """获取数据库会话"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()


def init_database(db_path: str = "data/tcm.db"):
    """初始化数据库（创建表）"""
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return engine
