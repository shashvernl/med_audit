import json

# Загружаем оригинальный JSON
with open("merged_rules_clean.json", "r", encoding="utf-8") as f:
    rules = json.load(f)

print(f"Оригиналов: {len(rules)}")

# Убираем дубликаты по комбинации (drug, dosage)
seen = set()
unique_rules = []

for rule in rules:
    key = (rule.get("drug", "").lower(), rule.get("dosage", "").lower())
    if key not in seen:
        seen.add(key)
        unique_rules.append(rule)

print(f"Уникальных: {len(unique_rules)}")
print(f"Удалено дублей: {len(rules) - len(unique_rules)}")

# Показываем, что осталось
print("\n📋 Уникальные правила:")
for rule in unique_rules:
    print(f"  - {rule['drug']}: {rule['dosage'][:50]}...")

# Сохраняем обратно
with open("merged_rules_clean.json", "w", encoding="utf-8") as f:
    json.dump(unique_rules, f, ensure_ascii=False, indent=2)

print("\n✅ Готово! Дубликаты удалены.")

# Слова, которые хотим исключить (ненужные препараты)
exclude_words = [
    "алтеплаза", "стрептокиназа", "тенектеплаза", "проурокиназа",
    "морфин", "атропин", "налоксон", "метоклопрамид",
    "адрено", "допамин", "транквилизатор", "диазепам", "галоперидол"
]

filtered_rules = []
for rule in unique_rules:
    drug_lower = rule.get("drug", "").lower()
    # Пропускаем, если есть запрещенное слово
    if not any(word in drug_lower for word in exclude_words):
        filtered_rules.append(rule)

print(f"После фильтрации ненужного: {len(filtered_rules)}")
unique_rules = filtered_rules