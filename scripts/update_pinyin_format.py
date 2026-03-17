#!/usr/bin/env python3
"""
拼音格式更新脚本

将方剂拼音从单词级格式（mahuang tang）转换为汉字级格式（ma huang tang）
并添加 pinyin_initials 字段

示例：
- 麻黄汤: "mahuang tang" -> "ma huang tang", initials: "mht"
- 桂枝汤: "guizhi tang" -> "gui zhi tang", initials: "gzt"
"""

import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pypinyin import pinyin, Style


def get_hanzi_pinyin(text: str) -> tuple[str, str]:
    """
    获取汉字的拼音（汉字级）和首字母
    
    Args:
        text: 汉字文本
    
    Returns:
        (pinyin_str, initials)
        pinyin_str: 汉字级拼音，如 "ma huang tang"
        initials: 首字母，如 "mht"
    """
    # 获取每个汉字的拼音
    pinyin_list = pinyin(text, style=Style.NORMAL)
    
    # 提取拼音字符串（去掉声调）
    pinyin_parts = [p[0] for p in pinyin_list]
    pinyin_str = " ".join(pinyin_parts)
    
    # 提取首字母
    initials = "".join(p[0] for p in pinyin_parts if p)
    
    return pinyin_str, initials


def update_formulas_pinyin(data_path: Path) -> None:
    """
    更新方剂数据的拼音格式
    
    Args:
        data_path: 数据文件路径
    """
    # 读取数据
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    formulas = data.get("formulas", [])
    updated_count = 0
    
    for formula in formulas:
        name = formula.get("name", "")
        old_pinyin = formula.get("pinyin", "")
        
        # 生成新的拼音格式
        new_pinyin, initials = get_hanzi_pinyin(name)
        
        # 更新数据
        formula["pinyin"] = new_pinyin
        formula["pinyin_initials"] = initials
        
        if new_pinyin != old_pinyin:
            updated_count += 1
            print(f"  {name}: '{old_pinyin}' -> '{new_pinyin}' (首字母: {initials})")
    
    # 更新元数据
    if "_metadata" in data:
        from datetime import datetime
        data["_metadata"]["updated_at"] = datetime.now().strftime("%Y-%m-%d")
        data["_metadata"]["pinyin_format"] = "hanzi-level"
    
    # 保存数据
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n完成！共更新 {updated_count} 首方剂的拼音格式")


def main():
    """主函数"""
    data_path = project_root / "data" / "formulas.json"
    
    if not data_path.exists():
        print(f"错误：数据文件不存在 {data_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("方剂拼音格式更新")
    print("=" * 60)
    print(f"数据文件: {data_path}")
    print()
    
    update_formulas_pinyin(data_path)
    
    print("\n说明：")
    print("  - pinyin: 汉字级拼音，如 'ma huang tang'")
    print("  - pinyin_initials: 首字母，如 'mht'")


if __name__ == "__main__":
    main()
