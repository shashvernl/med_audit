import sqlite3
import json
from typing import List, Dict
from datetime import datetime

DB_PATH = "quality_checker.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            drug TEXT NOT NULL,
            dosage TEXT NOT NULL,
            condition TEXT,
            contraindication TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            extracted_facts TEXT,
            quality_score REAL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_rule(rule: Dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO quality_criteria (drug, dosage, condition, contraindication)
        VALUES (?, ?, ?, ?)
    ''', (rule['drug'], rule['dosage'], rule.get('condition'), rule.get('contraindication')))
    conn.commit()
    conn.close()

def get_all_rules() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT drug, dosage, condition, contraindication FROM quality_criteria')
    rows = cursor.fetchall()
    conn.close()
    return [
        {"drug": row[0], "dosage": row[1], "condition": row[2], "contraindication": row[3]}
        for row in rows
    ]

def save_episode(filename: str, facts: List[Dict], quality_score: float) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO episodes (filename, extracted_facts, quality_score)
        VALUES (?, ?, ?)
    ''', (filename, json.dumps(facts, ensure_ascii=False), quality_score))
    episode_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return episode_id