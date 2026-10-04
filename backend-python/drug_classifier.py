import json
from typing import List, Dict, Set

DRUG_CLASSES = {
    "antiplatelet": {
        "name": "Антиагреганты",
        "required": True,
        "drugs": ["ацетилсалициловая кислота", "клопидогрел", "тикагрелор", "прасугрел"],
        "synonyms": {
            "ацетилсалициловая кислота": ["аспирин", "сановаск", "ацекардол", "кардиомагнил", "аск"],
            "клопидогрел": ["плавикс", "зилт", "атикард"],
            "тикагрелор": ["брилинта"],
            "прасугрел": ["эфиент"]
        }
    },
    "statin": {
        "name": "Статины",
        "required": True,
        "drugs": ["аторвастатин", "розувастатин", "симвастатин"],
        "synonyms": {
            "аторвастатин": ["липримар", "аторис"],
            "розувастатин": ["крестор", "мертинил"]
        }
    },
    "beta_blocker": {
        "name": "Бета-блокаторы",
        "required": True,
        "drugs": ["метопролол", "бисопролол", "карведилол"],
        "synonyms": {
            "метопролол": ["беталок", "эгилок"],
            "бисопролол": ["конкор"],
            "карведилол": ["дилатренд"]
        }
    },
    "acei_arb": {
        "name": "иАПФ/БРА",
        "required": True,
        "drugs": ["лизиноприл", "валсартан", "зофеноприл", "периндоприл", "рамиприл", "эналаприл"],
        "synonyms": {
            "лизиноприл": ["диротон"],
            "валсартан": ["диован", "валз"],
            "зофеноприл": ["зокардис"],
            "периндоприл": ["престариум"],
            "эналаприл": ["энап"]
        }
    },
    "aldosterone_antagonist": {
        "name": "Антагонисты альдостерона",
        "required": False,
        "condition": "ФВ ЛЖ < 40%",
        "drugs": ["спиронолактон", "эплеренон"],
        "synonyms": {
            "спиронолактон": ["верошпирон"],
            "эплеренон": ["инспра"]
        }
    },
    "ppi": {
        "name": "Ингибиторы протонной помпы",
        "required": False,
        "drugs": ["омепразол", "пантопразол", "рабепразол"],
        "synonyms": {
            "омепразол": ["омез", "ультоп"],
            "пантопразол": ["контролок"]
        }
    },
    "diuretic": {
        "name": "Диуретики",
        "required": False,
        "condition": "Отеки",
        "drugs": ["торасемид", "фуросемид"],
        "synonyms": {}
    },
    "antidiabetic": {
        "name": "Сахаропонижающие",
        "required": False,
        "condition": "Сахарный диабет",
        "drugs": ["метформин", "дапаглифлозин", "эмпаглифлозин", "вилдаглиптин"],
        "synonyms": {
            "дапаглифлозин": ["форсига"],
            "эмпаглифлозин": ["джардинс"],
            "вилдаглиптин": ["галвус"]
        }
    }
}


def normalize_drug_name(drug_name: str) -> str:
    """Приводит название препарата к каноническому виду"""
    name_lower = drug_name.lower().strip()
    
    for class_id, class_info in DRUG_CLASSES.items():
        for canonical in class_info["drugs"]:
            if canonical in name_lower:
                return canonical
        
        for canonical, synonyms in class_info["synonyms"].items():
            for syn in synonyms:
                if syn in name_lower:
                    return canonical
    
    return None


def classify_found_drugs(facts: List[Dict]) -> Dict[str, Dict]:
    """Классифицирует найденные препараты по группам"""
    result = {}
    
    for fact in facts:
        if fact["fact_type"] != "drug":
            continue
        
        drug_name = fact["fact_name"].lower()
        normalized = normalize_drug_name(drug_name)
        
        if not normalized:
            continue
        
        # Находим класс препарата
        for class_id, class_info in DRUG_CLASSES.items():
            if normalized in class_info["drugs"]:
                result[class_id] = {
                    "name": normalized,
                    "dosage": fact.get("fact_value", ""),
                    "unit": fact.get("fact_unit", "")
                }
                break
    
    return result


def get_applicable_rules(found_classes: Set[str], facts: List[Dict]) -> List[Dict]:
    """Возвращает правила только для найденных классов"""
    applicable_rules = []
    
    # Извлекаем дополнительные данные (ФВ, диабет)
    has_diabetes = False
    lvef = None
    
    for fact in facts:
        if fact["fact_type"] == "lab":
            if fact["fact_name"] == "LVEF":
                try:
                    lvef = float(fact.get("fact_value", 0))
                except:
                    pass
            elif fact["fact_name"] == "diabetes":
                has_diabetes = True
    
    for class_id in found_classes:
        class_info = DRUG_CLASSES.get(class_id, {})
        
        condition = class_info.get("condition", "")
        if condition:
            if "ФВ" in condition and lvef is not None:
                if "40" in condition and lvef >= 40:
                    continue  # не применимо
            if "диабет" in condition.lower() and not has_diabetes:
                continue
        
        for drug in class_info["drugs"]:
            if class_id == "antiplatelet":
                dosage = "75-100 мг/сут" if "ацетилсалициловая" in drug else "75 мг/сут"
            elif class_id == "statin":
                dosage = "40-80 мг/сут" if "аторвастатин" in drug else "20-40 мг/сут"
            elif class_id == "beta_blocker":
                dosage = "25-100 мг/сут" if "метопролол" in drug else "2.5-10 мг/сут"
            elif class_id == "acei_arb":
                dosage = "5-20 мг/сут" if "лизиноприл" in drug else "40-160 мг/сут"
            else:
                dosage = "25 мг/сут" if class_id == "aldosterone_antagonist" else "20 мг/сут"
            
            applicable_rules.append({
                "drug": drug.capitalize(),
                "dosage": dosage,
                "condition": class_info.get("condition", ""),
                "class_id": class_id,
                "required": class_info.get("required", False)
            })
    
    return applicable_rules


def evaluate_quality_by_class(rules: List[Dict], facts: List[Dict]) -> tuple:
    """Оценивает качество по классам препаратов"""
    results = []
    compliant_count = 0
    applicable_count = len(rules)
    
    found_drugs = {}
    for fact in facts:
        if fact["fact_type"] == "drug":
            found_drugs[fact["fact_name"].lower()] = fact
    
    for rule in rules:
        drug_name = rule["drug"].lower()
        
        if drug_name in found_drugs:
            fact = found_drugs[drug_name]
            actual_dosage = fact.get("fact_value", "")
            
            if actual_dosage:
                compliant_count += 1
                results.append({
                    "drug": rule["drug"],
                    "dosage": rule["dosage"],
                    "condition": rule.get("condition", ""),
                    "status": "COMPLIANT",
                    "note": f"Назначен в дозе {actual_dosage} мг"
                })
            else:
                results.append({
                    "drug": rule["drug"],
                    "dosage": rule["dosage"],
                    "condition": rule.get("condition", ""),
                    "status": "NON_COMPLIANT",
                    "note": "Препарат найден, но дозировка не указана"
                })
        else:
            if rule.get("required", True):
                results.append({
                    "drug": rule["drug"],
                    "dosage": rule["dosage"],
                    "condition": rule.get("condition", ""),
                    "status": "NON_COMPLIANT",
                    "note": "Обязательный препарат не назначен"
                })
            else:
                results.append({
                    "drug": rule["drug"],
                    "dosage": rule["dosage"],
                    "condition": rule.get("condition", ""),
                    "status": "NOT_APPLICABLE",
                    "note": "Препарат не обязателен для данного пациента"
                })
    
    quality_score = (compliant_count / applicable_count * 100) if applicable_count > 0 else 0
    return results, quality_score