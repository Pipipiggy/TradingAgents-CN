#!/usr/bin/env python3
"""
将自动生成的报告中开头不是"投资建议"的docx文件复制到指定目录中
目录格式为: /Users/liuqun/TradingAgents-CN/results/YYYY.MM.DD
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import sys

# 尝试导入python-docx库
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    print("⚠️  python-docx库未安装，将使用文件名方式判断")
    print("   如需完整功能，请运行: pip install python-docx")
    DOCX_AVAILABLE = False


def extract_first_paragraph(docx_path):
    """
    提取docx文件的第一段文本内容
    
    Args:
        docx_path (Path): docx文件路径
        
    Returns:
        str: 第一段文本内容，如果无法读取则返回空字符串
    """
    try:
        doc = Document(docx_path)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return paragraphs[0] if paragraphs else ""
    except Exception as e:
        print(f"⚠️  无法读取文件 {docx_path}: {e}")
        return ""


def is_investment_advice_by_filename(filename):
    """
    通过文件名判断是否为投资建议文件（备用方法）
    
    Args:
        filename (str): 文件名
        
    Returns:
        bool: 如果文件名包含投资建议相关关键词则返回True
    """
    filename_lower = filename.lower()
    investment_keywords = ['买入', '卖出', '持有', '投资', '建议']
    return any(keyword in filename_lower for keyword in investment_keywords)


def copy_non_investment_docx_files(single_file=None):
    """
    复制开头不是"投资建议"的docx文件到按日期命名的目录中
    
    Args:
        single_file (Path, optional): 单个文件路径，如果提供则只处理该文件
    """
    # 源目录 - 项目results目录
    project_root = Path(__file__).parent.parent
    
    # 目标目录 - /Users/liuqun/TradingAgents-CN/results/当前日期
    target_base_dir = Path("/Users/liuqun/TradingAgents-CN/results")
    current_date = datetime.now().strftime("%Y.%m.%d")
    target_dir = target_base_dir / current_date
    
    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 目标目录: {target_dir}")
    
    if single_file:
        # 只处理单个文件
        docx_files = [single_file]
        print(f"🔍 处理单个文件: {single_file.name}")
    else:
        # 收集所有docx文件
        source_dir = project_root / "results"
        if not source_dir.exists():
            print(f"❌ 源目录不存在: {source_dir}")
            return
        
        docx_files = list(source_dir.rglob("*.docx"))
        print(f"🔍 找到 {len(docx_files)} 个docx文件")
    
    if not DOCX_AVAILABLE:
        print("⚠️  使用文件名模式匹配作为替代方法")
    
    copied_count = 0
    
    for docx_file in docx_files:
        try:
            should_copy = True
            
            if DOCX_AVAILABLE:
                # 提取第一段内容
                first_paragraph = extract_first_paragraph(docx_file)
                
                # 检查是否以"投资建议"开头
                if first_paragraph.startswith("投资建议"):
                    should_copy = False
            else:
                # 使用文件名判断
                if is_investment_advice_by_filename(docx_file.name):
                    should_copy = False
            
            if should_copy:
                # 构造目标文件路径（只使用文件名，不保留目录结构）
                target_file = target_dir / docx_file.name
                
                # 如果文件已存在，添加时间戳避免覆盖
                if target_file.exists():
                    timestamp = datetime.now().strftime("%H%M%S")
                    name_part = target_file.stem
                    ext_part = target_file.suffix
                    target_file = target_dir / f"{name_part}_{timestamp}{ext_part}"
                
                # 复制文件
                shutil.copy2(docx_file, target_file)
                print(f"✅ 已复制: {docx_file.name}")
                copied_count += 1
            else:
                print(f"⏭️  跳过 (以'投资建议'开头): {docx_file.name}")
                
        except Exception as e:
            print(f"❌ 处理文件时出错 {docx_file.name}: {e}")
    
    print(f"\n🎉 完成! 共复制了 {copied_count} 个文件到 {target_dir}")


def main():
    """
    主函数
    """
    print("📄 TradingAgents-CN 非投资建议docx文件复制工具")
    print("=" * 50)
    
    if not DOCX_AVAILABLE:
        print("💡 提示: 安装python-docx库可获得更准确的判断结果")
        print("   运行命令: pip install python-docx")
        print()
    
    try:
        # 检查是否有命令行参数
        if len(sys.argv) > 1:
            file_path = Path(sys.argv[1])
            if file_path.exists() and file_path.suffix.lower() == '.docx':
                copy_non_investment_docx_files(single_file=file_path)
            else:
                print(f"❌ 无效的文件路径或非docx文件: {file_path}")
        else:
            copy_non_investment_docx_files()
    except KeyboardInterrupt:
        print("\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()