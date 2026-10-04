import re
import fitz
from typing import List, Dict
import warnings
warnings.filterwarnings("ignore")

try:
    from gliner import GLiNER
    GLINER_AVAILABLE = True
    model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")
    print(" GLiNER загружен")
except ImportError:
    GLINER_AVAILABLE = False
    print(" GLiNER не установлен, использую regex")
except Exception as e:
    GLINER_AVAILABLE = False
    print(f" Ошибка GLiNER: {e}")

EN_TO_RU_DRUGS = {
    "aspirin": "Ацетилсалициловая кислота",
    "acetylsalicylic acid": "Ацетилсалициловая кислота",
    "clopidogrel": "Клопидогрел",
    "ticagrelor": "Тикагрелор",
    "prasugrel": "Прасугрел",
    "atorvastatin": "Аторвастатин",
    "rosuvastatin": "Розувастатин",
    "metoprolol": "Метопролол",
    "bisoprolol": "Бисопролол",
    "carvedilol": "Карведилол",
    "lisinopril": "Лизиноприл",
    "valsartan": "Валсартан",
    "zofenopril": "Зофеноприл",
    "spironolactone": "Спиронолактон",
    "eplerenone": "Эплеренон",
    "omeprazole": "Омепразол",
    "pantoprazole": "Пантопразол",
}

RUSSIAN_SYNONYMS = {
    "ацетилсалициловая кислота": "Ацетилсалициловая кислота",
    "аспирин": "Ацетилсалициловая кислота",
    "сановаск": "Ацетилсалициловая кислота",
    "ацекардол": "Ацетилсалициловая кислота",
    "кардиомагнил": "Ацетилсалициловая кислота",
    "аск": "Ацетилсалициловая кислота",
    "клопидогрел": "Клопидогрел",
    "плавикс": "Клопидогрел",
    "зилт": "Клопидогрел",
    "атикард": "Клопидогрел",
    "аторвастатин": "Аторвастатин",
    "липримар": "Аторвастатин",
    "аторис": "Аторвастатин",
    "розувастатин": "Розувастатин",
    "крестор": "Розувастатин",
    "метопролол": "Метопролол",
    "беталок": "Метопролол",
    "эгилок": "Метопролол",
    "бисопролол": "Бисопролол",
    "конкор": "Бисопролол",
    "карведилол": "Карведилол",
    "дилатренд": "Карведилол",
    "лизиноприл": "Лизиноприл",
    "диротон": "Лизиноприл",
    "валсартан": "Валсартан",
    "диован": "Валсартан",
    "валз": "Валсартан",
    "зофеноприл": "Зофеноприл",
    "зокардис": "Зофеноприл",
    "спиронолактон": "Спиронолактон",
    "верошпирон": "Спиронолактон",
    "эплеренон": "Эплеренон",
    "инспра": "Эплеренон",
    "омепразол": "Омепразол",
    "омез": "Омепразол",
    "ультоп": "Омепразол",
    "пантопразол": "Пантопразол",
    "контролок": "Пантопразол",
    "метформин": "Метформин",
    "глюкофаж": "Метформин",
    "сиофор": "Метформин",

    "амлодипин": "Амлодипин",
    "норваск": "Амлодипин",
    "амлотоп": "Амлодипин",

    "моксонидин": "Моксонидин",
    "физиотенз": "Моксонидин",
    "тензотран": "Моксонидин",

    "нитроглицерин": "Нитроглицерин",
    "нитроспрей": "Нитроглицерин",
    "нитроминт": "Нитроглицерин",
    "нитрокор": "Нитроглицерин",

    "периндоприл": "Периндоприл",
    "престариум": "Периндоприл",
    "перинева": "Периндоприл",

    "торасемид": "Торасемид",
    "диувер": "Торасемид",
    "бритомар": "Торасемид",

    "амиодарон": "Амиодарон",
    "кордарон": "Амиодарон",

    "лерканидипин": "Лерканидипин",
    "леркамен": "Лерканидипин",

    "эмпаглифлозин": "Эмпаглифлозин",
    "джардинс": "Эмпаглифлозин",

    "гепарин": "Гепарин",

    "лозартан": "Лозартан",
    "лориста": "Лозартан",

    "ривароксабан": "Ривароксабан",
    "ксарелто": "Ривароксабан",

    "дапаглифлозин": "Дапаглифлозин",
    "форсига": "Дапаглифлозин",

    "изосорбида мононитрат": "Изосорбида мононитрат",
    "эфокс": "Изосорбида мононитрат",
    "моночинкве": "Изосорбида мононитрат",

    "гидрохлоротиазид": "Гидрохлоротиазид",
    "гипотиазид": "Гидрохлоротиазид",

    "апиксабан": "Апиксабан",
    "эликвис": "Апиксабан",

    "бисопролол": "Бисопролол",
    "конкор": "Бисопролол",

    "ирбесартан": "Ирбесартан + гидрохлоротиазид",
    "ко-апровель": "Ирбесартан + гидрохлоротиазид",
    "коапровель": "Ирбесартан + гидрохлоротиазид",

    "метформин": "Метформин",
    "сиофор": "Метформин",
    "глюкофаж": "Метформин",
}

PROCEDURE_SYNONYMS = {
    "ЭхоКГ": [
        "эхокг",
        "узи сердца",
        "эхокардиография",
    ],
    "КАГ": [
        "каг",
        "коронароангиография",
        "коронарная ангиография",
        "ангиография",
    ],
    "Холтер": [
        "холтер",
        "холтеровское мониторирование",
        "холтеровское мониторирование экг",
        "хм-экг",
        "хм экг",
        "хмэкг",
        "хмон",
        "суточное мониторирование",
        "суточное мониторирование экг",
        "мониторирование экг",
    ],
    "Рентген ОГК": [
        "рентген огк",
        "рентген легких",
        "флюорография",
        "ркг",
        "рентгенография органов грудной клетки",
    ],
    "КТ": [
        "кт",
        "компьютерная томография",
        "мскт",
    ],
    "МРТ": [
        "мрт",
        "магнитно-резонансная томография",
    ],
    "ЭГДС": [
        "эгдс",
        "гастроскопия",
        "фгдс",
        "фиброгастродуоденоскопия",
    ],
}

STOP_WORDS = [
    "января", "февраля", "марта", "апреля", "мая", "июня", "июля",
    "августа", "сентября", "октября", "ноября", "декабря",
    "года", "схеме", "по", "до", "или", "равное", "количестве",
    "от", "мл", "г", "кг", "таблетка", "капсула", "раз", "сут"
]

def is_valid_drug_name(name: str) -> bool:
    """Проверяет, похоже ли название на реальный препарат"""
    name_lower = name.lower().strip()
    
    if len(name_lower) < 3 or len(name_lower) > 30:
        return False
    
    if name_lower in STOP_WORDS:
        return False
    
    if not re.search(r'[а-яё]', name_lower):
        return False
    
    return True

def normalize_drug_name(name: str) -> str:
    """Приводит название к каноническому виду"""
    name_lower = name.lower().strip()
    
    name_lower = re.sub(r'[^\wа-яё]', '', name_lower)
    
    if name_lower in EN_TO_RU_DRUGS:
        return EN_TO_RU_DRUGS[name_lower]
    
    for synonym, canonical in RUSSIAN_SYNONYMS.items():
        if synonym in name_lower or name_lower == synonym:
            return canonical
    
    return None

def extract_facts_from_pdf(pdf_path: str) -> List[Dict]:
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    
    drugs_dict = {}
    
    if GLINER_AVAILABLE:
        try:
            print("🔍 GLiNER: поиск препаратов...")
            entities = model.predict_entities(text, ["DRUG"])
            for entity in entities:
                if entity["label"] == "DRUG" and entity["score"] > 0.6:
                    drug_name = normalize_drug_name(entity["text"])
                    if drug_name and is_valid_drug_name(entity["text"]) and drug_name not in drugs_dict:
                        drugs_dict[drug_name] = {
                            "fact_type": "drug",
                            "fact_name": drug_name,
                            "fact_value": "",
                            "fact_unit": "",
                        }
                        print(f"   🤖 GLiNER: {drug_name} (уверенность: {entity['score']:.2f})")
        except Exception as e:
            print(f"    GLiNER ошибка: {e}")
    
    print("🔍 Regex: поиск препаратов с дозировками...")
    pattern = r'([А-Яа-я]+(?:[а-я]+)?)\s+(\d+(?:[.,]\d+)?)\s*(мг|мкг|г|мл)'
    
    for match in re.finditer(pattern, text, re.IGNORECASE):
        drug_raw = match.group(1)
        dose = match.group(2).replace(',', '.')
        unit = match.group(3)
        
        if not is_valid_drug_name(drug_raw):
            continue
        
        drug_name = normalize_drug_name(drug_raw)
        
        if not drug_name:
            continue
        
        try:
            if float(dose) > 500:
                continue
        except:
            pass
        
        if drug_name not in drugs_dict:
            drugs_dict[drug_name] = {
                "fact_type": "drug",
                "fact_name": drug_name,
                "fact_value": dose,
                "fact_unit": unit,
            }
            print(f"    {drug_name}: {dose} {unit}")
        else:
            # Если уже есть, но без дозы — добавим
            if not drugs_dict[drug_name]["fact_value"]:
                drugs_dict[drug_name]["fact_value"] = dose
                drugs_dict[drug_name]["fact_unit"] = unit
                print(f"    {drug_name}: добавлена доза {dose} {unit}")
    
    print(" Специальный поиск аспирина...")
    aspirin_patterns = [
        r'(Сановаск|Ацекардол|Кардиомагнил|Аспирин|Аспикор)\s+(\d+)\s*мг',
        r'(\d+)\s*мг\s+(Сановаск|Ацекардол|Кардиомагнил|Аспирин|Аспикор)'
    ]
    
    for pattern in aspirin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if match.group(1).isdigit():
                dose = match.group(1)
            else:
                dose = match.group(2)
            
            drugs_dict["Ацетилсалициловая кислота"] = {
                "fact_type": "drug",
                "fact_name": "Ацетилсалициловая кислота",
                "fact_value": dose,
                "fact_unit": "мг",
            }
            print(f"    Ацетилсалициловая кислота (аспирин): {dose} мг")
            break
    
    print("🔍 Поиск русскими синонимами лекарств...")
    for synonym, canonical in RUSSIAN_SYNONYMS.items():
        if canonical in drugs_dict:
            continue
        for match in re.finditer(rf'\b{re.escape(synonym)}\b', text, re.IGNORECASE):
            if not is_valid_drug_name(match.group()):
                continue
            
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            dose_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(мг|мкг|г|мл)', context)
            
            if dose_match:
                dose = dose_match.group(1).replace(',', '.')
                unit = dose_match.group(2)
                
                try:
                    if float(dose) > 500:
                        continue
                except:
                    pass
                
                drugs_dict[canonical] = {
                    "fact_type": "drug",
                    "fact_name": canonical,
                    "fact_value": dose,
                    "fact_unit": unit,
                }
                print(f"    {canonical}: {dose} {unit} (найден по синониму '{synonym}')")
                break

    print("🔍 Поиск процедур и диагностики...")
    for proc_name, synonyms in PROCEDURE_SYNONYMS.items():
        found = False
        for syn in synonyms:
            if re.search(rf'\b{re.escape(syn)}\b', text, re.IGNORECASE):
                found = True
                break
        
        if found:
            drugs_dict[proc_name] = {
                "fact_type": "procedure",
                "fact_name": proc_name,
                "fact_value": "выполнено", 
                "fact_unit": "",
            }
            print(f"    Найдена процедура: {proc_name}")

    print("🔍 Поиск лабораторных показателей...")
    
    lab_markers = {
        "калий": "Калий (K+)",
        "креатинин": "Креатинин",
        "лпнп": "ЛПНП",
        "мно": "МНО",
        "гликированный": "HbA1c"
    }

    for marker_key, marker_name in lab_markers.items():
        pattern = rf'{re.escape(marker_key)}.*?(\d+(?:[.,]\d+)?)'
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        
        if match:
            value = match.group(1).replace(',', '.')
            try:
                val_float = float(value)
                if 0.1 <= val_float <= 1000:
                    drugs_dict[marker_name] = {
                        "fact_type": "lab",
                        "fact_name": marker_name,
                        "fact_value": value,
                        "fact_unit": "",
                    }
                    print(f"    Найден анализ: {marker_name} = {value}")
            except:
                pass

    facts = list(drugs_dict.values())
    
    print(f"\n ИТОГО НАЙДЕНО: {len(facts)} фактов (лекарства + процедуры + анализы)")
    for f in facts:
        val = f.get('fact_value', '?')
        unit = f.get('fact_unit', '')
        print(f"   - [{f['fact_type']}] {f['fact_name']}: {val} {unit}")
    
    return facts