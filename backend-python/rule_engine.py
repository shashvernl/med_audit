import re
from typing import List, Dict
LAB_DEPENDENCIES = {
    "acei_arb": "Калий (K+)",       
    "aldosterone_antagonist": "Калий (K+)", 
    "anticoagulant": "МНО",        
    "statin": "ЛПНП (Холестерин)",  
}

def get_rules_for_diagnosis(all_rules_data: Dict, diagnosis_code: str) -> List[Dict]:
    """
    Ищет правила для диагноза. Если точного кода нет, 
    пробует найти родительский код (например, для I20.8 ищет I20).
    """
    # 1. Точное совпадение
    if diagnosis_code in all_rules_data:
        print(f" Найдены правила для точного кода: {diagnosis_code}")
        return all_rules_data[diagnosis_code]
    
    if '.' in diagnosis_code:
        parent_code = diagnosis_code.split('.')[0]
        if parent_code in all_rules_data:
            print(f" Найдены правила для родительского кода: {parent_code} (для диагноза {diagnosis_code})")
            return all_rules_data[parent_code]
            
    print(f" Правила для диагноза {diagnosis_code} не найдены.")
    return []

PROCEDURE_SYNONYMS = {
    "эхокг": ["эхокг", "узи сердца", "эхокардиография"],
    "каг": ["каг", "коронароангиография", "коронарная ангиография", "ангиография"],
    "рентген огк": ["рентген огк", "рентген легких", "флюорография", "ркг", "рентгенография"],
    "холтер": ["холтер", "хмон", "суточное мониторирование", "мониторирование экг"],
    "кт": ["кт", "компьютерная томография", "мсКТ", "мскт"],
    "мрт": ["мрт", "магнитно-резонансная томография"],
    "эгдс": ["эгдс", "гастроскопия", "фгдс", "фиброгастродуоденоскопия"]
}

def pluralize_ru(n, one, two, five):
    """Склоняет слова по правилам русского языка"""
    n = abs(int(n)) % 100
    n1 = n % 10
    if n > 10 and n < 20: return five
    if n1 > 1 and n1 < 5: return two
    if n1 == 1: return one
    return five

def dosage_in_range(actual_value: str, expected: str) -> bool:
    if not actual_value or actual_value == "":
        return False

    try:
        actual = float(actual_value)
    except:
        return False

    # Ищем числа, которые могут быть дозировками
    numbers = re.findall(r'(\d+(?:[.,]\d+)?)', expected)
    if not numbers:
        return True

    # Проверяем, есть ли диапазон
    if '–' in expected or '-' in expected:
        # Ищем только первые два числа (диапазон)
        range_matches = re.findall(r'(\d+(?:[.,]\d+)?)\s*[–-]\s*(\d+(?:[.,]\d+)?)', expected)
        if range_matches:
            low, high = float(range_matches[0][0]), float(range_matches[0][1])
            return low <= actual <= high

    # Если нет диапазона, проверяем точное значение с допуском
    for num_str in numbers:
        try:
            expected_val = float(num_str.replace(',', '.'))
            # Если это число > 1000 - это, скорее всего, год или номер страницы
            if expected_val > 1000:
                continue
            # Допуск ±30%
            if abs(actual - expected_val) / expected_val <= 0.3:
                return True
        except:
            continue

    return False

def classify_drugs_by_category(facts: List[Dict]):
    """
    Классифицирует препараты и процедуры из эпикриза по категориям
    """
    category_map = {
        # Antiplatelet
        "ацетилсалициловая кислота": "antiplatelet",
        "аспирин": "antiplatelet",
        "сановаск": "antiplatelet",
        "ацекардол": "antiplatelet",
        "кардиомагнил": "antiplatelet",
        "аск": "antiplatelet",

        "клопидогрел": "antiplatelet",
        "плавикс": "antiplatelet",
        "зилт": "antiplatelet",
        "атикард": "antiplatelet",

        "тикагрелор": "antiplatelet",
        "тикагрелол": "antiplatelet",

        "прасугрел": "antiplatelet",

        # Statin
        "аторвастатин": "statin",
        "липримар": "statin",
        "аторис": "statin",

        "розувастатин": "statin",
        "крестор": "statin",

        # Beta Blocker
        "метопролол": "beta_blocker",
        "беталок": "beta_blocker",
        "эгилок": "beta_blocker",

        "бисопролол": "beta_blocker",
        "конкор": "beta_blocker",

        "карведилол": "beta_blocker",
        "дилатренд": "beta_blocker",

        # ACEI/ARB
        "лизиноприл": "acei_arb",
        "диротон": "acei_arb",

        "валсартан": "acei_arb",
        "диован": "acei_arb",
        "валз": "acei_arb",

        "зофеноприл": "acei_arb",
        "зокардис": "acei_arb",

        # Aldosterone antagonist
        "спиронолактон": "aldosterone_antagonist",
        "верошпирон": "aldosterone_antagonist",

        "эплеренон": "aldosterone_antagonist",
        "инспра": "aldosterone_antagonist",

        # Diuretics
        "фуросемид": "diuretic",
        "лазикс": "diuretic",
        "торасемид": "diuretic",
        "дихлотиазид": "diuretic",

        # Proton pump inhibitor
        "омепразол": "proton_pump_inhibitor",
        "омез": "proton_pump_inhibitor",
        "ультоп": "proton_pump_inhibitor",
        "пантопразол": "proton_pump_inhibitor",
        "контролок": "proton_pump_inhibitor",

        # Analgesics
        "морфин": "analgesic",
        "промедол": "analgesic",

        # Nitrates
        "нитроглицерин": "nitrate",
        "изосорбида динитрат": "nitrate",

        # Anticoagulants
        "варфарин": "anticoagulant",
        "апиксабан": "anticoagulant",
        "ривароксабан": "anticoagulant",
        "дабигатран": "anticoagulant",
        "эноксапарин": "anticoagulant",
        "гепарин": "anticoagulant",

        # Thrombolytics
        "алтеплаза": "thrombolytic",
        "стрептокиназа": "thrombolytic",
        "тенектеплаза": "thrombolytic",

        # SGLT2 inhibitors
        "дапаглифлозин": "sglt2_inhibitor",
        "эмпаглифлозин": "sglt2_inhibitor",

        # Biguanides
        "метформин": "biguanide",
        "глюкофаж": "biguanide",
        "сиофор": "biguanide",

        # Calcium channel blockers
        "амлодипин": "ccb",
        "норваск": "ccb",
        "верапамил": "ccb",
        "дилтиазем": "ccb",

        # Insulin
        "инсулин": "insulin",
        "инсулин аспарт": "insulin",
        "инсулин гларгин": "insulin",

        # Gliptins
        "ситаглиптин": "gliptin",
        "яндвиго": "gliptin",

        # Sulfonylureas
        "глибенкламид": "sulfonylurea",
        "манинил": "sulfonylurea",

        # Imidasoline
        "моксонидин": "imidasoline",
        "физиотенз": "imidasoline",

        # Anti-inflammatory
        "колхицин": "antiinflammatory",
        "колчамин": "antiinflammatory",

        # Supportive
        "кислород": "supportive",
        "оксигенотерапия": "supportive",
        "натрия хлорид": "supportive",

        # Процедуры / Диагностика
        "эхокг": "procedure",
        "узи сердца": "procedure",
        "эхокардиография": "procedure",
        
        "каг": "procedure",
        "коронароангиография": "procedure",
        "коронарная ангиография": "procedure",
        "ангиография": "procedure",
        
        "холтер": "procedure",
        "хмон": "procedure",
        "суточное мониторирование экг": "procedure",
        
        "кт головного мозга": "procedure",
        "мрт головного мозга": "procedure",
        "мсКТ": "procedure",
        
        "рентген огк": "procedure",
        "флюорография": "procedure",
        
        "эгдс": "procedure",
        "гастроскопия": "procedure",
        "фгдс": "procedure",
    }

    categories = {}
    for fact in facts:
        # Разрешаем брать не только drugs, но и другие типы фактов, если они есть
        # Но пока ориентируемся на fact_name
        drug_name = fact["fact_name"].lower()
        cat = category_map.get(drug_name)

        if cat:
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(fact)

    return categories

def evaluate_quality(rules: List[Dict], facts: List[Dict]) -> tuple:
    # Словарь для перевода технических названий категорий на русский
    category_names_ru = {
        "antiplatelet": "Антиагреганты",
        "statin": "Статины",
        "beta_blocker": "Бета-блокаторы",
        "acei_arb": "иАПФ / БРА",
        "aldosterone_antagonist": "Антагонисты альдостерона",
        "anticoagulant": "Антикоагулянты",
        "analgesic": "Обезболивающие",
        "nitrate": "Нитраты",
        "supportive": "Поддерживающая терапия",
        "antidiabetic": "Сахароснижающие",
        "antiinflammatory": "Противовоспалительные",
        "thrombolytic": "Тромболитики",
        "diuretic": "Диуретики",
        "proton_pump_inhibitor": "Ингибиторы протонной помпы",
        "ccb": "Блокаторы кальциевых каналов",
        "sglt2_inhibitor": "Ингибиторы SGLT2",
        "biguanide": "Бигуаниды",
        "insulin": "Инсулин",
        "gliptin": "Глиптины",
        "sulfonylurea": "Производные сульфонилмочевины",
        "imidasoline": "Имидазолиновые рецепторы",
        "procedure": "Диагностика / Процедуры",
    }

    results = []
    compliant_count = 0
    applicable_count = 0

    # Классифицируем препараты и процедуры из эпикриза
    epicrisis_categories = classify_drugs_by_category(facts)
    found_drugs = [f["fact_name"].lower() for f in facts if f["fact_type"] == "drug"]
    epicrisis_categories_set = set(epicrisis_categories.keys())

    print(f"\n🔍 Эпикриз содержит элементы из категорий: {list(epicrisis_categories_set)}")
    print(f"   Найденные препараты/процедуры: {found_drugs}")

    # Группируем правила по категориям
    category_rules = {}
    for rule in rules:
        category = rule.get("category")
        required = rule.get("required", False)

        # Правило проверяется, если:
        # 1. Его категория есть в эпикризе, ИЛИ
        # 2. Оно обязательное (required = true)
        if category in epicrisis_categories_set or required:
            if category not in category_rules:
                category_rules[category] = []
            category_rules[category].append(rule)

    # Проверяем каждую категорию
    for category, rules_for_category in category_rules.items():
        applicable_count += 1
        
        # Получаем русское название категории
        ru_name = category_names_ru.get(category, category)

        # Разделяем обязательные и необязательные правила в категории
        required_rules = [r for r in rules_for_category if r.get("required", False)]
        optional_rules = [r for r in rules_for_category if not r.get("required", False)]

        # --- СПЕЦИАЛЬНАЯ ЛОГИКА ДЛЯ ПРОЦЕДУР ---
        if category == "procedure":
            procedure_compliant = True
            
            # Для процедур мы проверяем каждое обязательное правило отдельно
            for rule in required_rules:
                target_keyword = rule["drug"].lower()
                synonyms = PROCEDURE_SYNONYMS.get(target_keyword, [target_keyword])
                
                # Ищем совпадение в найденных фактах
                found = False
                for fact in facts:
                    fact_name_lower = fact["fact_name"].lower()
                    if any(syn in fact_name_lower for syn in synonyms):
                        found = True
                        break
                
                if not found:
                    procedure_compliant = False
                    results.append({
                        "drug": f"Процедура: {rule['drug']}",
                        "dosage": rule["dosage"],
                        "condition": rule.get("condition", ""),
                        "status": "CATEGORY_MISSING_REQUIRED"
                    })
                    print(f"⚠️  FAIL [{ru_name}]: обязательная процедура '{rule['drug']}' не найдена")

            if procedure_compliant:
                 results.append({
                    "drug": ru_name,
                    "dosage": "Все обязательные исследования выполнены",
                    "condition": "",
                    "status": "COMPLIANT"
                })
                 print(f"✅ OK [{ru_name}]: все обязательные процедуры найдены")
            
            continue # Переходим к следующей категории, минуя стандартную логику лекарств

        # --- СТАНДАРТНАЯ ЛОГИКА ДЛЯ ЛЕКАРСТВ ---
        drugs_in_category = epicrisis_categories.get(category, [])

        # Если в категории есть препараты, проверяем их дозировку
        if drugs_in_category:
            category_compliant = False
            for drug_fact in drugs_in_category:
                actual_dosage = drug_fact.get("fact_value", "")
                # Проверяем, подходит ли хотя бы одна дозировка хотя бы к одному правилу
                for rule in rules_for_category:
                    if dosage_in_range(actual_dosage, rule["dosage"]):
                        category_compliant = True
                        break
                if category_compliant:
                    break

            if category_compliant:
                compliant_count += 1
                results.append({
                    "drug": ru_name,
                    "dosage": f"{len(required_rules)} {pluralize_ru(len(required_rules), 'обязательный', 'обязательных', 'обязательных')}, "
                              f"{len(optional_rules)} {pluralize_ru(len(optional_rules), 'опциональный', 'опциональных', 'опциональных')}",
                    "condition": f"({len(rules_for_category)} {pluralize_ru(len(rules_for_category), 'вариант', 'варианта', 'вариантов')})",
                    "status": "COMPLIANT"
                })
                print(f"✅ OK [{ru_name}]: препараты найдены и дозировка подходит")
            else:
                results.append({
                    "drug": ru_name,
                    "dosage": f"{len(required_rules)} {pluralize_ru(len(required_rules), 'обязательный', 'обязательных', 'обязательных')}, "
                              f"{len(optional_rules)} {pluralize_ru(len(optional_rules), 'опциональный', 'опциональных', 'опциональных')}",
                    "condition": f"({len(rules_for_category)} {pluralize_ru(len(rules_for_category), 'вариант', 'варианта', 'вариантов')})",
                    "status": "NON_COMPLIANT"
                })
                print(f"❌ FAIL [{ru_name}]: препараты есть, но дозировка не подходит")
        else:
            # Нет препаратов в категории
            if required_rules:
                # Обязательная категория, но препарат не назначен
                results.append({
                    "drug": ru_name,
                    "dosage": f"{len(required_rules)} {pluralize_ru(len(required_rules), 'обязательный', 'обязательных', 'обязательных')}, "
                              f"{len(optional_rules)} {pluralize_ru(len(optional_rules), 'опциональный', 'опциональных', 'опциональных')}",
                    "condition": f"({len(rules_for_category)} {pluralize_ru(len(rules_for_category), 'вариант', 'варианта', 'вариантов')})",
                    "status": "CATEGORY_MISSING_REQUIRED"
                })
                print(f"⚠️  FAIL [{ru_name}]: обязательная категория, препарат не найден")
            else:
                # Необязательная категория, всё ок
                compliant_count += 1
                results.append({
                    "drug": ru_name,
                    "dosage": f"{len(required_rules)} {pluralize_ru(len(required_rules), 'обязательный', 'обязательных', 'обязательных')}, "
                              f"{len(optional_rules)} {pluralize_ru(len(optional_rules), 'опциональный', 'опциональных', 'опциональных')}",
                    "condition": f"({len(rules_for_category)} {pluralize_ru(len(rules_for_category), 'вариант', 'варианта', 'вариантов')})",
                    "status": "CATEGORY_OPTIONAL_NOT_PRESENT"
                })
                print(f"ℹ️  SKIP [{ru_name}]: необязательная категория, препарат не найден")
        # ... (твой старый код проверки категорий) ...

    # --- ПРОВЕРКА ЛАБОРАТОРНОГО КОНТРОЛЯ (Безопасность) ---
    print("\n🧪 Проверка лабораторного контроля...")
    
    # Собираем все найденные лабораторные показатели в удобный список имен
    found_labs = [f["fact_name"] for f in facts if f.get("fact_type") == "lab"]
    print(f"   Найдены анализы: {found_labs}")

    # Проходим по всем категориям, которые были назначены врачу
    for category, rules_list in category_rules.items():
        # Если эта категория требует лабораторного контроля
        required_lab = LAB_DEPENDENCIES.get(category)
        
        if required_lab:
            # Проверяем, есть ли препараты этой категории в эпикризе
            if category in epicrisis_categories_set:
                # Если препараты есть, проверяем наличие анализа
                if required_lab not in found_labs:
                    results.append({
                        "drug": f"Контроль: {required_lab}",
                        "dosage": f"Требуется при приеме препаратов группы {category_names_ru.get(category, category)}",
                        "condition": "Безопасность терапии",
                        "status": "NON_COMPLIANT" # Или можно сделать отдельный статус LAB_MISSING
                    })
                    print(f"   ⚠️ ВНИМАНИЕ: Назначены препараты ({category}), но не найден анализ '{required_lab}'")
                else:
                    print(f"   ✅ OK: Анализ '{required_lab}' найден для категории {category}")

    # Пересчитываем качество (учитывая новые ошибки)
    actual_applicable = sum(1 for r in results if r["status"] != "NOT_APPLICABLE" and
                           r["status"] != "CATEGORY_OPTIONAL_NOT_PRESENT")

    actual_compliant = sum(1 for r in results if r["status"] == "COMPLIANT" or
                          r["status"] == "CATEGORY_OPTIONAL_NOT_PRESENT")

    quality_score = (actual_compliant / actual_applicable * 100) if actual_applicable > 0 else 0
    

    # Обрабатываем нерелевантные правила
    for rule in rules:
        category = rule.get("category")
        required = rule.get("required", False)

        if category not in epicrisis_categories_set and not required:
            results.append({
                "drug": rule["drug"],
                "dosage": rule["dosage"],
                "condition": rule.get("condition", ""),
                "status": "NOT_APPLICABLE"
            })
            print(f"⏭️  SKIP {rule['drug']}: не релевантно (категория: {category})")

    # Пересчитываем качество: только обязательные категории
    actual_applicable = sum(1 for r in results if r["status"] != "NOT_APPLICABLE" and
                           r["status"] != "CATEGORY_OPTIONAL_NOT_PRESENT")

    actual_compliant = sum(1 for r in results if r["status"] == "COMPLIANT" or
                          r["status"] == "CATEGORY_OPTIONAL_NOT_PRESENT")

    quality_score = (actual_compliant / actual_applicable * 100) if actual_applicable > 0 else 0

    print(f"\n📊 Результат:")
    print(f"   - Всего релевантных категорий: {actual_applicable}")
    print(f"   - Соблюдено: {actual_compliant}")
    print(f"   - Качество: {quality_score:.1f}%")

    return results, quality_score