function pluralize(count, one, two, five) {
    let n = Math.abs(count) % 100;
    let n1 = n % 10;
    if (n > 10 && n < 20) return five;
    if (n1 > 1 && n1 < 5) return two;
    if (n1 === 1) return one;
    return five;
}

function truncate(str, max = 70) {
    if (!str) return '';
    return str.length > max ? str.slice(0, max) + '...' : str;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

async function uploadPDF() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) { alert('Выберите PDF-файл'); return; }

    const formData = new FormData();
    formData.append('file', file);

    const btn = document.getElementById('uploadBtn');
    btn.disabled = true;
    btn.textContent = 'Обработка...';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').classList.remove('show');

    try {
        const res = await fetch('/check_epicrisis', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Ошибка сервера');
        displayResults(data);
    } catch(e) {
        alert('Ошибка: ' + e.message);
    } finally {
        document.getElementById('loading').style.display = 'none';
        btn.disabled = false;
        btn.textContent = 'Начать проверку';
    }
}

function displayResults(data) {
    const resultDiv = document.getElementById('result');
    let scoreClass = data.quality_score >= 80 ? 'compliant' : (data.quality_score >= 60 ? 'warning' : 'non-compliant');

    let html = `<h2>Результаты проверки</h2>
                <div class="score-container">
                    <div class="score ${scoreClass}">${data.quality_score}%</div>
                    <p style="color:#64748b;">Соответствие клиническим рекомендациям</p>
                </div>
                <h3>Детализация по группам и препаратам</h3>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th style="width: 22%;">Группа / Препарат</th>
                                <th style="width: 30%;">Требования / Дозировка</th>
                                <th style="width: 28%;">Условие применения</th>
                                <th style="width: 20%;">Статус</th>
                            </tr>
                        </thead>
                        <tbody>`;

    for (const rule of data.results) {
        let badgeClass, statusText;
        switch(rule.status) {
            case 'COMPLIANT': badgeClass='badge-success'; statusText='Соответствует'; break;
            case 'NON_COMPLIANT': badgeClass='badge-danger'; statusText='Не соответствует'; break;
            case 'CATEGORY_MISSING_REQUIRED': badgeClass='badge-danger'; statusText='Отсутствует обязательное'; break;
            case 'CATEGORY_OPTIONAL_NOT_PRESENT': badgeClass='badge-warning'; statusText='Необязательное'; break;
            case 'NOT_APPLICABLE': badgeClass='badge-info'; statusText='Не применимо'; break;
            default: badgeClass='badge-warning'; statusText=rule.status;
        }

        let conditionText = rule.condition || '';
        if (rule.drug.startsWith('[')) {
            conditionText = conditionText.replace(/\(\d+ вариантов\)/g, '').trim() || 'Группа препаратов';
            const match = conditionText.match(/\((\d+) вариантов\)/);
            if (match) {
                conditionText = conditionText.replace(`(${match[1]} вариантов)`, `(${match[1]} ${pluralize(match[1], 'вариант', 'варианта', 'вариантов')})`);
            }
        }

        html += `<tr>
                    <td><strong>${escapeHtml(rule.drug)}</strong></td>
                    <td class="cell-truncate" title="${escapeHtml(rule.dosage || '')}">${truncate(rule.dosage)}</td>
                    <td class="cell-truncate" title="${escapeHtml(conditionText)}">${truncate(conditionText)}</td>
                    <td><span class="badge ${badgeClass}">${statusText}</span></td>
                 </tr>`;
    }

    html += `</tbody></table></div>
             <div class="legend">
                <strong>Легенда статусов:</strong>
                <ul>
                    <li><span class="badge badge-success">Соответствует</span> — препарат назначен в корректной дозе</li>
                    <li><span class="badge badge-danger">Не соответствует</span> — доза отклоняется от рекомендаций</li>
                    <li><span class="badge badge-danger">Отсутствует обязательное</span> — критически важный класс не назначен</li>
                    <li><span class="badge badge-warning">Необязательное</span> — дополнительный препарат, не влияет на итог</li>
                    <li><span class="badge badge-info">Не применимо</span> — правило не относится к данному случаю</li>
                </ul>
             </div>`;

    resultDiv.innerHTML = html;
    resultDiv.classList.add('show');
}