#!/usr/bin/env python3
"""
数据迁移脚本 - Data Migration Script

将 JSON 数据迁移到 SQLite 数据库。

使用方法:
    python scripts/migrate_to_sqlite.py [--db-path data/tcm.db]

AI协作说明：
- 从 formulas.json 迁移方剂数据
- 从 herbs.json 迁移药材数据
- 从 syndrome_formulas.json 迁移证型数据
- 保持 JSON 文件作为备份
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import sys

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import (
    init_database,
    get_session,
    FormulaDB,
    HerbDB,
    HerbCompositionDB,
    FormulaAliasDB,
    ClinicalCaseDB,
    SyndromeDB,
    SyndromeFormulaDB,
    DataMetadataDB,
)


def migrate_formulas(session, data_dir: Path):
    """迁移方剂数据"""
    formulas_file = data_dir / "formulas.json"
    
    if not formulas_file.exists():
        print(f"⚠️  方剂数据文件不存在: {formulas_file}")
        return 0
    
    with open(formulas_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    formulas = data.get("formulas", [])
    count = 0
    
    for item in formulas:
        # 检查是否已存在
        existing = session.query(FormulaDB).filter_by(id=item["id"]).first()
        if existing:
            continue
        
        # 创建方剂记录
        formula = FormulaDB(
            id=item["id"],
            name=item["name"],
            pinyin=item.get("pinyin", ""),
            pinyin_initials=item.get("pinyin_initials", ""),
            efficacy=item.get("efficacy", ""),
            indications=item.get("indications", ""),
            contraindications=item.get("contraindications", ""),
            usage=item.get("usage", ""),
            source=item.get("source", ""),
            category=item.get("category", ""),
            modern_research=item.get("modern_research", ""),
        )
        session.add(formula)
        
        # 添加组成药材
        for comp in item.get("composition", []):
            composition = HerbCompositionDB(
                formula_id=item["id"],
                herb_name=comp["herb"],
                dosage=comp.get("dosage", ""),
                role=comp.get("role", ""),
                note=comp.get("note", ""),
            )
            session.add(composition)
        
        # 添加别名
        for alias in item.get("alias", []):
            alias_record = FormulaAliasDB(
                formula_id=item["id"],
                alias=alias,
            )
            session.add(alias_record)
        
        # 添加医案
        for case in item.get("clinical_cases", []):
            case_record = ClinicalCaseDB(
                formula_id=item["id"],
                case_text=case,
            )
            session.add(case_record)
        
        count += 1
        print(f"  ✅ {item['id']}: {item['name']}")
    
    session.commit()
    return count


def migrate_herbs(session, data_dir: Path):
    """迁移药材数据"""
    herbs_file = data_dir / "herbs.json"
    
    if not herbs_file.exists():
        print(f"⚠️  药材数据文件不存在: {herbs_file}")
        return 0
    
    with open(herbs_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    herbs = data.get("herbs", data) if isinstance(data, dict) else data
    count = 0
    
    for item in herbs:
        if isinstance(item, str):
            continue
        
        herb_name = item.get("name", item.get("herb", ""))
        if not herb_name:
            continue
        
        # 检查是否已存在
        existing = session.query(HerbDB).filter_by(name=herb_name).first()
        if existing:
            continue
        
        herb = HerbDB(
            name=herb_name,
            pinyin=item.get("pinyin", ""),
            nature=item.get("nature", ""),
            flavor=item.get("flavor", ""),
            meridian=item.get("meridian", ""),
            efficacy=item.get("efficacy", ""),
            indications=item.get("indications", ""),
            contraindications=item.get("contraindications", ""),
            dosage=item.get("dosage", ""),
        )
        session.add(herb)
        count += 1
        print(f"  ✅ 药材: {herb_name}")
    
    session.commit()
    return count


def migrate_syndromes(session, data_dir: Path):
    """迁移证型数据"""
    syndromes_file = data_dir / "syndrome_formulas.json"
    
    if not syndromes_file.exists():
        print(f"⚠️  证型数据文件不存在: {syndromes_file}")
        return 0
    
    with open(syndromes_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    syndromes = data.get("syndromes", [])
    count = 0
    
    for item in syndromes:
        # 检查是否已存在
        existing = session.query(SyndromeDB).filter_by(id=item["id"]).first()
        if existing:
            continue
        
        syndrome = SyndromeDB(
            id=item["id"],
            name=item["name"],
            description=item.get("description", ""),
            keywords=json.dumps(item.get("keywords", []), ensure_ascii=False),
        )
        session.add(syndrome)
        
        # 添加证型-方剂关联
        for formula_id in item.get("formulas", []):
            relation = SyndromeFormulaDB(
                syndrome_id=item["id"],
                formula_id=formula_id,
            )
            session.add(relation)
        
        count += 1
        print(f"  ✅ 证型: {item['name']}")
    
    session.commit()
    return count


def save_metadata(session, key: str, value: str):
    """保存元数据"""
    existing = session.query(DataMetadataDB).filter_by(key=key).first()
    if existing:
        existing.value = value
        existing.updated_at = datetime.utcnow()
    else:
        metadata = DataMetadataDB(key=key, value=value)
        session.add(metadata)
    session.commit()


def main():
    parser = argparse.ArgumentParser(description="将 JSON 数据迁移到 SQLite")
    parser.add_argument(
        "--db-path",
        default="data/tcm.db",
        help="SQLite 数据库路径 (默认: data/tcm.db)"
    )
    parser.add_argument(
        "--data-dir",
        default="data",
        help="JSON 数据目录 (默认: data)"
    )
    args = parser.parse_args()
    
    # 确定路径
    project_root = Path(__file__).parent.parent
    db_path = project_root / args.db_path
    data_dir = project_root / args.data_dir
    
    print("=" * 50)
    print("中医学习助手 - 数据迁移工具")
    print("=" * 50)
    print(f"数据库路径: {db_path}")
    print(f"数据目录: {data_dir}")
    print()
    
    # 初始化数据库
    print("📦 初始化数据库...")
    init_database(str(db_path))
    print("  ✅ 数据库初始化完成")
    print()
    
    # 获取会话
    session = get_session()
    
    # 迁移方剂数据
    print("📋 迁移方剂数据...")
    formula_count = migrate_formulas(session, data_dir)
    print(f"  迁移了 {formula_count} 首方剂")
    print()
    
    # 迁移药材数据
    print("🌿 迁移药材数据...")
    herb_count = migrate_herbs(session, data_dir)
    print(f"  迁移了 {herb_count} 味药材")
    print()
    
    # 迁移证型数据
    print("🏥 迁移证型数据...")
    syndrome_count = migrate_syndromes(session, data_dir)
    print(f"  迁移了 {syndrome_count} 个证型")
    print()
    
    # 保存元数据
    save_metadata(session, "last_migration", datetime.now().isoformat())
    save_metadata(session, "formula_count", str(formula_count))
    save_metadata(session, "herb_count", str(herb_count))
    save_metadata(session, "syndrome_count", str(syndrome_count))
    
    print("=" * 50)
    print("✅ 迁移完成！")
    print(f"  - 方剂: {formula_count} 首")
    print(f"  - 药材: {herb_count} 味")
    print(f"  - 证型: {syndrome_count} 个")
    print("=" * 50)
    
    session.close()


if __name__ == "__main__":
    main()
