#!/usr/bin/env python3
"""
《神农本草经》解析脚本

从 tcmoc 项目的 Markdown 文件中提取药材数据，转换为项目需要的 JSON 格式。

使用方法:
    python scripts/parse_shennong_bencao.py

数据来源: https://github.com/lab99x/tcmoc
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional


# 常用药材拼音映射（部分）
PINYIN_MAP = {
    "丹沙": "dansha",  # 朱砂
    "人参": "renshen",
    "甘草": "gancao",
    "干地黄": "gandihuang",
    "白术": "baizhu",
    "菟丝子": "tusizi",
    "牛膝": "niuxi",
    "柴胡": "chaihu",
    "麦门冬": "maimendong",
    "独活": "duhuo",
    "车前子": "cheqianzi",
    "木香": "muxiang",
    "薯蓣": "shuyu",  # 山药
    "薏苡仁": "yiyiren",
    "泽泻": "zexie",
    "远志": "yuanzhi",
    "龙胆": "longdan",
    "细辛": "xixin",
    "石斛": "shihu",
    "巴戟天": "bajitian",
    "黄连": "huanglian",
    "防风": "fangfeng",
    "蒲黄": "puhuang",
    "续断": "xuduan",
    "漏芦": "loulv",
    "决明子": "juemingzi",
    "丹参": "danshen",
    "茜根": "qiancao",  # 茜草
    "五味子": "wuweizi",
    "蛇床子": "shechuangzi",
    "地肤子": "difuzi",
    "茵陈": "yinchen",
    "沙参": "shashen",
    "徐长卿": "xuchangqing",
    "王不留行": "wangbuliuxing",
    "升麻": "shengma",
    "牡桂": "mugui",  # 肉桂
    "菌桂": "lingui",  # 桂枝
    "茯苓": "fuling",
    "柏实": "baishi",  # 柏子仁
    "酸枣": "suanzao",
    "杜仲": "duzhong",
    "女贞实": "nvzhenshi",  # 女贞子
    "橘柚": "juye",  # 陈皮
    "龙骨": "longgu",
    "麝香": "shexiang",
    "牛黄": "niuhuang",
    "阿胶": "ejiao",
    "牡蛎": "muli",
    "龟甲": "guijia",
    "海蛤": "haige",
    "藕实茎": "oushi",  # 莲子
    "大枣": "dazao",
    "葡萄": "putao",
    "鸡头实": "jitoushi",  # 芡实
    "胡麻": "huma",  # 黑芝麻
    "冬葵子": "dongkuizi",
    "瓜蒂": "guadi",
    "苦菜": "kucai",
    "雄黄": "xionghuang",
    "石钟乳": "shizhongru",
    "滑石": "huashi",
    "禹余粮": "yuyuliang",
    "白石英": "baishiying",
    "紫石英": "zishiying",
    "五色石脂": "wuseseshizhi",
}


def extract_nature(text: str) -> str:
    """提取性味"""
    # 匹配 "味甘，微寒" 或 "味甘、平" 等格式
    match = re.search(r'味([^，。、]+)[，。]?\s*([^，。\n]*)', text)
    if match:
        flavor = match.group(1).strip()
        nature = match.group(2).strip() if match.group(2) else ""
        if nature and nature not in ['主', '生', '一', '久']:
            return f"{flavor}，{nature}"
        return flavor
    return ""


def extract_efficacy(text: str) -> str:
    """提取功效主治"""
    # 匹配 "主..." 格式
    match = re.search(r'主([^。]+?)(?:。|$)', text)
    if match:
        return match.group(1).strip()
    return ""


def extract_grade(directory: str) -> str:
    """根据目录判断品级"""
    if "上经" in directory or "上品" in directory:
        return "上品"
    elif "中经" in directory or "中品" in directory:
        return "中品"
    elif "下经" in directory or "下品" in directory:
        return "下品"
    return ""


def clean_herb_name(name: str) -> str:
    """清理药名"""
    # 移除括号内容
    name = re.sub(r'[（(].*?[）)]', '', name)
    # 移除空格
    name = name.strip()
    return name


def parse_shennong_bencao(md_file: Path) -> List[Dict]:
    """解析《神农本草经》Markdown 文件"""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    herbs = []
    current_directory = ""
    herb_id = 1
    
    # 按段落分割
    sections = re.split(r'<目录>([^<]*)', content)
    
    for i, section in enumerate(sections):
        # 提取目录信息（判断品级）
        if i % 2 == 1:  # 这是目录内容
            current_directory = section.strip()
            continue
        
        # 查找所有药材
        # 格式: <篇名>药名</篇名> 或 <篇名>药名
        herb_pattern = r'<篇名>([^<\n]+)'
        matches = re.finditer(herb_pattern, section)
        
        for match in matches:
            herb_name = clean_herb_name(match.group(1))
            
            # 跳过非药材条目（如"上经"、"下经"等章节标题）
            skip_keywords = ['上经', '中经', '下经', '玉石', '草', '木', '兽', '禽', 
                           '虫鱼', '果', '菜', '米谷', '人', '序', '目录']
            if any(kw in herb_name for kw in skip_keywords):
                continue
            
            # 提取药材内容（从篇名到下一个篇名或目录）
            start_pos = match.end()
            next_herb = re.search(r'<篇名>', section[start_pos:])
            next_dir = re.search(r'<目录>', section[start_pos:])
            
            if next_herb and next_dir:
                end_pos = start_pos + min(next_herb.start(), next_dir.start())
            elif next_herb:
                end_pos = start_pos + next_herb.start()
            elif next_dir:
                end_pos = start_pos + next_dir.start()
            else:
                end_pos = len(section)
            
            herb_content = section[start_pos:end_pos].strip()
            
            # 提取核心内容（去掉《吴普》和《名医》的补充说明）
            core_match = re.search(r'^内容：(.+?)(?:(?:《吴普》|《名医》|$))', herb_content, re.DOTALL)
            if core_match:
                core_content = core_match.group(1)
            else:
                core_content = herb_content
            
            # 清理内容
            core_content = re.sub(r'\s+', ' ', core_content)
            core_content = re.sub(r'<[^>]+>', '', core_content)
            
            # 提取性味
            nature = extract_nature(core_content)
            
            # 提取功效主治
            efficacy = extract_efficacy(core_content)
            
            # 获取品级
            grade = extract_grade(current_directory)
            
            # 获取拼音
            pinyin = PINYIN_MAP.get(herb_name, "")
            
            herb = {
                "id": f"h{herb_id:03d}",
                "name": herb_name,
                "pinyin": pinyin,
                "nature": nature,
                "meridian": "",  # 《神农本草经》没有归经信息
                "efficacy": efficacy,
                "indications": efficacy,  # 主治与功效合并
                "dosage": "",  # 原文无用量
                "contraindications": "",  # 原文无禁忌
                "source": "神农本草经",
                "grade": grade,
                "classic_text": core_content[:200] if len(core_content) > 200 else core_content
            }
            
            herbs.append(herb)
            herb_id += 1
    
    return herbs


def merge_with_existing(new_herbs: List[Dict], existing_file: Path) -> List[Dict]:
    """与现有药材数据合并"""
    
    if not existing_file.exists():
        return new_herbs
    
    with open(existing_file, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
    
    existing_herbs = existing_data.get("herbs", [])
    existing_names = {h["name"] for h in existing_herbs}
    
    # 找出新增的药材
    new_unique = [h for h in new_herbs if h["name"] not in existing_names]
    
    # 重新编号
    start_id = len(existing_herbs) + 1
    for i, herb in enumerate(new_unique):
        herb["id"] = f"h{start_id + i:03d}"
    
    # 合并
    all_herbs = existing_herbs + new_unique
    
    return all_herbs


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    
    # 输入文件路径
    md_file = Path.home() / "Desktop/iflow-workspace/tcmoc/books/(6.1.1-02438.3).本草-本草经-本经辑本.《神农本草经》(三卷).吴普.魏.md"
    
    if not md_file.exists():
        print(f"❌ 文件不存在: {md_file}")
        return
    
    print("=" * 50)
    print("《神农本草经》药材数据解析")
    print("=" * 50)
    print(f"源文件: {md_file}")
    print()
    
    # 解析药材
    print("📚 解析药材数据...")
    herbs = parse_shennong_bencao(md_file)
    print(f"  提取到 {len(herbs)} 味药材")
    print()
    
    # 显示部分数据
    print("📝 数据样例:")
    for herb in herbs[:5]:
        print(f"  - {herb['name']} ({herb.get('grade', '')}): {herb.get('nature', '')}")
    print()
    
    # 与现有数据合并
    existing_file = project_root / "data/herbs.json"
    print("🔄 合并现有数据...")
    all_herbs = merge_with_existing(herbs, existing_file)
    print(f"  合并后共 {len(all_herbs)} 味药材")
    print()
    
    # 保存结果
    output_file = project_root / "data/herbs_shennong.json"
    
    output_data = {
        "_metadata": {
            "description": "中药材数据库 - TCM Herb Database (含《神农本草经》)",
            "source": "中国药典 + 神农本草经 (tcmoc)",
            "source_url": "https://github.com/lab99x/tcmoc",
            "license": "开源可用，遵循原项目许可",
            "last_updated": "2026-03-12",
            "total_herbs": len(all_herbs),
            "shennong_herbs": len(herbs),
        },
        "herbs": all_herbs
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据已保存到: {output_file}")
    print()
    
    # 统计品级分布
    grade_count = {"上品": 0, "中品": 0, "下品": 0, "": 0}
    for herb in herbs:
        grade = herb.get("grade", "")
        if grade in grade_count:
            grade_count[grade] += 1
        else:
            grade_count[""] += 1
    
    print("📊 《神农本草经》品级分布:")
    for grade, count in grade_count.items():
        if count > 0:
            print(f"  - {grade or '未知'}: {count} 味")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
