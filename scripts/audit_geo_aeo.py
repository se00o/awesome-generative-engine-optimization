# -*- coding: utf-8 -*-
"""
SEO, GEO & AEO Automated Audit CLI Tool
Based on modern Generative Search Optimization (GEO) & Answer Engine Optimization (AEO) frameworks.
Evaluates websites across 3 dimensions:
1. SEO: Technical On-Page, Meta tags, Headings, Crawlability
2. GEO: E-E-A-T signals, Factual density, Entity clarity, Knowledge Graph
3. AEO: Direct answer formatting, Question-phrased headings, FAQ/HowTo schema, Voice readiness
"""

import sys
import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class SimpleHTMLAuditor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.meta_desc = ""
        self.h1_tags = []
        self.h2_tags = []
        self.h3_tags = []
        self.in_h1 = False
        self.in_h2 = False
        self.in_h3 = False
        self.schemas = []
        self.in_script = False
        self.script_type = ""
        self.script_buffer = ""
        self.links = []
        self.images_total = 0
        self.images_with_alt = 0
        self.text_content = []
        self.tables_count = 0
        self.lists_count = 0

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            name = attr_dict.get("name", "").lower()
            prop = attr_dict.get("property", "").lower()
            if name == "description" or prop == "og:description":
                if not self.meta_desc:
                    self.meta_desc = attr_dict.get("content", "")
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "h2":
            self.in_h2 = True
        elif tag == "h3":
            self.in_h3 = True
        elif tag == "script":
            self.in_script = True
            self.script_type = attr_dict.get("type", "").lower()
            self.script_buffer = ""
        elif tag == "a":
            href = attr_dict.get("href", "")
            if href:
                self.links.append(href)
        elif tag == "img":
            self.images_total += 1
            if attr_dict.get("alt", "").strip():
                self.images_with_alt += 1
        elif tag == "table":
            self.tables_count += 1
        elif tag in ("ul", "ol"):
            self.lists_count += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "h2":
            self.in_h2 = False
        elif tag == "h3":
            self.in_h3 = False
        elif tag == "script":
            self.in_script = False
            if "application/ld+json" in self.script_type:
                self.schemas.append(self.script_buffer)
            self.script_buffer = ""

    def handle_data(self, data):
        cleaned = data.strip()
        if self.in_title:
            self.title += data
        elif self.in_h1 and cleaned:
            self.h1_tags.append(cleaned)
        elif self.in_h2 and cleaned:
            self.h2_tags.append(cleaned)
        elif self.in_h3 and cleaned:
            self.h3_tags.append(cleaned)
        elif self.in_script:
            self.script_buffer += data
        else:
            if cleaned:
                self.text_content.append(cleaned)

def audit_url(url):
    print(f"\n========================================================")
    print(f"🚀 ЗАПУСК АУДИТА: {url}")
    print(f"========================================================")

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ModernSEOGEOAuditor/1.0; +https://github.com/se00o/awesome-generative-engine-optimization)"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"❌ Ошибка загрузки URL: {e}")
        return

    parser = SimpleHTMLAuditor()
    parser.feed(html)

    full_text = " ".join(parser.text_content)
    word_count = len(full_text.split())

    # --- 1. SEO EVALUATION ---
    seo_score = 10.0
    seo_findings = []

    # Title check
    title = parser.title.strip()
    if not title:
        seo_score -= 2.5
        seo_findings.append(("Title Tag", "Отсутствует тег <title>", "CRITICAL"))
    elif len(title) < 20 or len(title) > 75:
        seo_score -= 1.0
        seo_findings.append(("Title Tag", f"Длина {len(title)} знаков (оптимально: 45-65)", "WARNING"))
    else:
        seo_findings.append(("Title Tag", f"Корректный ({len(title)} знаков): '{title[:50]}...'", "GOOD"))

    # Meta Description check
    meta_desc = parser.meta_desc.strip()
    if not meta_desc:
        seo_score -= 2.0
        seo_findings.append(("Meta Description", "Отсутствует meta description", "CRITICAL"))
    elif len(meta_desc) < 70 or len(meta_desc) > 180:
        seo_score -= 0.5
        seo_findings.append(("Meta Description", f"Длина {len(meta_desc)} знаков (оптимально: 120-160)", "WARNING"))
    else:
        seo_findings.append(("Meta Description", f"Корректный ({len(meta_desc)} знаков)", "GOOD"))

    # Headings check
    if len(parser.h1_tags) == 0:
        seo_score -= 2.0
        seo_findings.append(("H1 Heading", "Отсутствует заголовок H1", "CRITICAL"))
    elif len(parser.h1_tags) > 1:
        seo_score -= 1.0
        seo_findings.append(("H1 Heading", f"Обнаружено несколько H1 ({len(parser.h1_tags)})", "WARNING"))
    else:
        seo_findings.append(("H1 Heading", f"Корректный единичный H1: '{parser.h1_tags[0][:50]}'", "GOOD"))

    # Content length
    if word_count < 300:
        seo_score -= 2.0
        seo_findings.append(("Content Depth", f"Малый объем текста ({word_count} слов)", "WARNING"))
    else:
        seo_findings.append(("Content Depth", f"Достаточный объем контента ({word_count} слов)", "GOOD"))

    seo_score = max(1.0, min(10.0, seo_score))

    # --- 2. GEO EVALUATION (Generative Engine Optimization) ---
    geo_score = 10.0
    geo_findings = []

    # E-E-A-T & Author signals
    author_signals = ["автор", "эксперт", "команда", "руководитель", "основатель", "about", "team", "credentials"]
    has_author = any(re.search(rf"\b{s}\b", full_text, re.IGNORECASE) for s in author_signals)
    if not has_author:
        geo_score -= 2.0
        geo_findings.append(("E-E-A-T Author", "Не обнаружены явные указания на экспертов/авторов", "WARNING"))
    else:
        geo_findings.append(("E-E-A-T Author", "Найдены маркеры персоналий и авторства", "GOOD"))

    # Structured Data / Schema.org
    if not parser.schemas:
        geo_score -= 3.0
        geo_findings.append(("JSON-LD Schema", "Отсутствует микроразметка Schema.org (критично для RAG)", "CRITICAL"))
    else:
        schema_types = []
        for s in parser.schemas:
            types = re.findall(r'"@type"\s*:\s*"([^"]+)"', s)
            schema_types.extend(types)
        geo_findings.append(("JSON-LD Schema", f"Обнаружены схемы: {', '.join(set(schema_types)) or 'Custom'}", "GOOD"))

    # Factual density (numbers, statistics, metrics)
    numbers_count = len(re.findall(r'\b\d+(?:[\.,]\d+)?%?|\b(?:\d{4})\b', full_text))
    if numbers_count < 5:
        geo_score -= 2.0
        geo_findings.append(("Factual Density", "Низкая плотность фактов/цифр для цитирования в LLM", "WARNING"))
    else:
        geo_findings.append(("Factual Density", f"Высокая плотность числовых фактов ({numbers_count}+ маркеров)", "GOOD"))

    # Entity Clarity & Links
    has_social_links = any(re.search(r't\.me|vk\.com|github\.com|youtube\.com|habr\.com|vc\.ru', l) for l in parser.links)
    if not has_social_links:
        geo_score -= 1.0
        geo_findings.append(("Entity sameAs", "Мало внешних ссылок на профили бренда в графе знаний", "WARNING"))
    else:
        geo_findings.append(("Entity sameAs", "Присутствуют ссылки на сущности бренда в соцсетях/медиа", "GOOD"))

    geo_score = max(1.0, min(10.0, geo_score))

    # --- 3. AEO EVALUATION (Answer Engine Optimization) ---
    aeo_score = 10.0
    aeo_findings = []

    # Question-phrased headings
    all_h2_h3 = parser.h2_tags + parser.h3_tags
    question_headings = [h for h in all_h2_h3 if re.search(r'\?|как |что |почему |сколько |зачем |где ', h, re.IGNORECASE)]
    if not question_headings:
        aeo_score -= 2.5
        aeo_findings.append(("Question Headings", "Нет вопросительных H2/H3 для прямого захвата PAA/сводки", "WARNING"))
    else:
        aeo_findings.append(("Question Headings", f"Найдено {len(question_headings)} вопросительных заголовков", "GOOD"))

    # Lists & Tables for Featured Snippets
    if parser.lists_count == 0 and parser.tables_count == 0:
        aeo_score -= 2.5
        aeo_findings.append(("Structured Answers", "Отсутствуют списки и таблицы для сниппетов/ответов", "WARNING"))
    else:
        aeo_findings.append(("Structured Answers", f"Найдено списков: {parser.lists_count}, таблиц: {parser.tables_count}", "GOOD"))

    # FAQ Schema
    has_faq_schema = any("FAQPage" in s for s in parser.schemas)
    if not has_faq_schema:
        aeo_score -= 2.0
        aeo_findings.append(("FAQ Schema", "Отсутствует разметка FAQPage (снижает шансы в Zero-Click)", "WARNING"))
    else:
        aeo_findings.append(("FAQ Schema", "Обнаружена микроразметка FAQPage", "GOOD"))

    aeo_score = max(1.0, min(10.0, aeo_score))

    # --- PRINT SUMMARY REPORT ---
    print("\n📊 РЕЗУЛЬТАТЫ СВОДНОГО АУДИТА:")
    print("--------------------------------------------------------")
    print(f"🔹 SEO (Традиционный поиск):        {seo_score:.1f} / 10.0")
    print(f"🔹 GEO (Генеративный поиск LLM):    {geo_score:.1f} / 10.0")
    print(f"🔹 AEO (Прямые ответы и сниппеты):  {aeo_score:.1f} / 10.0")
    print(f"⭐ ОБЩИЙ ИНДЕКС ЗРЕЛОСТИ:           {(seo_score + geo_score + aeo_score):.1f} / 30.0")
    print("--------------------------------------------------------")

    print("\n🔍 ДЕТАЛИЗАЦИЯ ПО НАПРАВЛЕНИЯМ:")
    for section, findings in [("SEO", seo_findings), ("GEO", geo_findings), ("AEO", aeo_findings)]:
        print(f"\n[{section}]:")
        for signal, finding, status in findings:
            badge = "✅" if status == "GOOD" else ("⚠️" if status == "WARNING" else "❌")
            print(f"  {badge} [{signal}] {finding}")

    print("\n🎯 МАТРИЦА ТОП-ПРИОРИТЕТОВ:")
    priority_items = []
    for section, findings in [("SEO", seo_findings), ("GEO", geo_findings), ("AEO", aeo_findings)]:
        for signal, finding, status in findings:
            if status == "CRITICAL":
                priority_items.append((f"🔴 КРИТИЧНО ({section})", f"{signal}: {finding}", "Высокое влияние на видимость"))
            elif status == "WARNING":
                priority_items.append((f"🟠 ВАЖНО ({section})", f"{signal}: {finding}", "Быстрый рост (Quick Win)"))

    if not priority_items:
        print("  🎉 Критических замечаний не выявлено! Сайт подготовлен образцово.")
    else:
        for p, desc, imp in priority_items[:5]:
            print(f"  {p} -> {desc} [{imp}]")
    print("\n========================================================\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        audit_url(sys.argv[1])
    else:
        print("Использование: python audit_geo_aeo.py <URL>")
        print("Пример: python audit_geo_aeo.py https://dreaper.ru")
