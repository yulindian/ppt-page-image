#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any


PLANNING_FILES = ("PPT内容大纲.txt", "风格提示词.txt", "字体说明.txt")


def _require_mapping(state: dict, key: str) -> dict:
    value = state.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    return value


def _require_list(state: dict, key: str) -> list:
    value = state.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    return value


def _text(value: Any) -> str:
    if isinstance(value, (list, dict)):
        raise ValueError("Expected scalar text value")
    return str(value if value is not None else "").strip()


def _items(values: Any) -> str:
    if not values:
        return "无"
    if isinstance(values, dict):
        return "；".join(f"{key}：{_items(value)}" for key, value in values.items())
    if isinstance(values, list):
        return "；".join(_items(value) for value in values)
    return _text(values)


def _render_outline(state: dict) -> str:
    deck = _require_mapping(state, "deck")
    style = _require_mapping(state, "style")
    families = _require_mapping(state, "families")
    pages = _require_list(state, "pages")
    lines = [
        "# PPT内容大纲",
        "",
        "## 项目信息",
        f"- PPT名称：{_text(deck.get('name'))}",
        f"- 受众：{_text(deck.get('audience'))}",
        f"- 使用场景：{_text(deck.get('scenario'))}",
        f"- 语言：{_text(deck.get('language'))}",
        f"- 页数：{_text(deck.get('expected_pages'))}",
        f"- 来源权威：{_text(deck.get('source_authority'))}",
        f"- 内容范围：{_text(deck.get('content_scope'))}",
        f"- 重要假设：{_items(deck.get('assumptions'))}",
        f"- 选定风格：{_text(style.get('summary'))}",
        "",
        "## 页面家族",
    ]
    for name, family in families.items():
        lines.extend(
            [
                f"### {name}",
                f"- 母页：{_text(family.get('mother_page'))}",
                f"- 页面：{_items(family.get('pages'))}",
                f"- 不变量：{_items(family.get('invariants'))}",
            ]
        )
        for specification in family.get("component_specifications") or []:
            lines.extend(
                [
                    f"- 组件：{_text(specification.get('name'))}",
                    f"  - 适用页：{_items(specification.get('applies_to'))}",
                    f"  - 固定：{_items(specification.get('fixed'))}",
                    f"  - 可变：{_items(specification.get('variable'))}",
                    f"  - 禁止：{_items(specification.get('forbidden'))}",
                ]
            )
        lines.append("")

    lines.append("## 逐页大纲")
    for page in pages:
        budget = page.get("element_budget") or {}
        zones = page.get("zones") or {}
        lines.extend(
            [
                "",
                f"### 第{page.get('index')}页｜{_text(page.get('title'))}",
                f"- 页面类型：{_text(page.get('type'))}",
                f"- 教学或沟通目标：{_text(page.get('goal'))}",
                f"- 精确可见文案：{_items(page.get('visible_copy'))}",
                f"- 必要事实：{_items(page.get('required_facts'))}",
                f"- 来源说明：{_items(page.get('source_notes'))}",
                f"- 内容依据：{_items(page.get('content_evidence'))}",
                f"- 设计理由：{_text(page.get('design_rationale'))}",
                f"- 核心元素：{_text(budget.get('focal'))}",
                f"- 辅助元素：{_items(budget.get('supporting'))}",
                f"- 装饰上限：{_text(budget.get('decoration_limit'))}",
                f"- 页面家族：{_text(page.get('family'))}",
                f"- 阅读顺序：{_items(page.get('reading_order'))}",
                f"- 密度风险：{_text(page.get('density_risk'))}",
                f"- 标题区：{_text(zones.get('title'))}",
                f"- 阅读区：{_text(zones.get('reading'))}",
                f"- 插图区：{_text(zones.get('illustration'))}",
                f"- 装饰区：{_text(zones.get('decoration'))}",
                f"- 视觉主体：{_text(page.get('visual_subject'))}",
                f"- 图文关系：{_text(page.get('image_text_relationship'))}",
                f"- 字体角色：{_items(page.get('font_roles'))}",
                f"- 页面负面约束：{_items(page.get('negative_constraints'))}",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_style(state: dict) -> str:
    style = _require_mapping(state, "style")
    families = _require_mapping(state, "families")
    pages = _require_list(state, "pages")
    enrichment = state.get("enrichment") or []
    delivery = _require_mapping(state, "delivery")
    lines = [
        "# 风格提示词",
        "",
        "## 选定风格",
        f"- 风格摘要：{_text(style.get('summary'))}",
        f"- 用户反馈：{_text(style.get('user_feedback'))}",
        f"- 保留特征：{_items(style.get('useful_traits'))}",
        f"- 拒绝特征：{_items(style.get('rejected_traits'))}",
        f"- 风格指纹：{_text(style.get('fingerprint'))}",
        f"- 色彩角色：{_items(style.get('palette_roles'))}",
        f"- 材质：{_text(style.get('material'))}",
        f"- 图像处理：{_text(style.get('image_treatment'))}",
        f"- 留白：{_text(style.get('whitespace'))}",
        f"- 装饰密度：{_text(style.get('decoration_density'))}",
        f"- 允许变化：{_items(style.get('permitted_variation'))}",
        f"- 字体方向：{_text(style.get('typography_direction'))}",
        f"- 全局负面约束：{_items(style.get('global_negatives'))}",
        "",
        "## 全局提示词",
        _text(style.get("global_prompt")),
        "",
        "## 页面家族规范",
    ]
    for name, family in families.items():
        lines.extend([f"### {name}", f"- 不变量：{_items(family.get('invariants'))}"])
        for specification in family.get("component_specifications") or []:
            lines.extend(
                [
                    f"- 组件：{_text(specification.get('name'))}",
                    f"  - 固定：{_items(specification.get('fixed'))}",
                    f"  - 可变：{_items(specification.get('variable'))}",
                    f"  - 禁止：{_items(specification.get('forbidden'))}",
                ]
            )
        lines.append("")

    lines.extend(["## 素材与内容增强", f"- 增强记录：{_items(enrichment)}"])
    for image in delivery.get("images") or []:
        lines.append(f"- 交付素材：{_items(image)}")
    lines.append("")
    lines.append("## 逐页完整提示词")
    for page in pages:
        lines.extend(["", f"### 第{page.get('index')}页｜{_text(page.get('title'))}", _text(page.get("prompt"))])
    return "\n".join(lines).rstrip() + "\n"


def _render_fonts(state: dict) -> str:
    fonts = _require_list(state, "fonts")
    pages = _require_list(state, "pages")
    lines = [
        "# 字体说明",
        "",
        "图片模型可能近似而不能保证精确使用指定字体；打包字体用于后续修复和可编辑重建。",
        "",
        "## 字体角色",
    ]
    for font in fonts:
        lines.extend(
            [
                f"### {_text(font.get('role'))}｜{_text(font.get('display_name'))}",
                f"- 字重：{_text(font.get('weight'))}",
                f"- 本地来源：{_text(font.get('source_path'))}",
                f"- 打包文件：{_text(font.get('packaged_filename'))}",
                f"- 替代字体：{_text(font.get('fallback'))}",
                f"- 可视特征：{_text(font.get('visual_traits'))}",
                f"- 许可状态：{_text(font.get('license_status'))}",
                "",
            ]
        )
    lines.append("## 逐页字体映射")
    for page in pages:
        lines.append(f"- 第{page.get('index')}页《{_text(page.get('title'))}》：{_items(page.get('font_roles'))}")
    return "\n".join(lines).rstrip() + "\n"


def render_documents(state: dict) -> dict[str, str]:
    if state.get("schema_version") != 2:
        raise ValueError("Planning documents require project-state schema_version 2")
    return {
        "PPT内容大纲.txt": _render_outline(state),
        "风格提示词.txt": _render_style(state),
        "字体说明.txt": _render_fonts(state),
    }


def write_documents(state: dict, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for filename, content in render_documents(state).items():
        path = output_dir / filename
        path.write_text(content, encoding="utf-8", newline="\n")
        outputs[filename] = path
    return outputs
