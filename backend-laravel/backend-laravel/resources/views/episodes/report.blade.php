<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Отчет проверки эпикриза</title>
    <style>
        body { font-family: DejaVu Sans, sans-serif; font-size: 12px; color: #333; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }
        .header h1 { color: #2563eb; margin: 0; font-size: 18px; }
        .info-grid { display: table; width: 100%; margin-bottom: 20px; }
        .info-row { display: table-row; }
        .info-cell { display: table-cell; padding: 5px; }
        .label { font-weight: bold; color: #555; }
        
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th { background-color: #f3f4f6; text-align: left; padding: 8px; font-size: 10px; text-transform: uppercase; border: 1px solid #ddd; }
        td { padding: 8px; border: 1px solid #ddd; vertical-align: top; }
        
        .status-ok { color: #16a34a; font-weight: bold; }
        .status-fail { color: #dc2626; font-weight: bold; }
        .status-warn { color: #ea580c; font-weight: bold; }
        
        .footer { margin-top: 30px; text-align: center; font-size: 10px; color: #999; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
</head>
<body>

    <div class="header">
        <h1>МедАудит: Отчет проверки качества</h1>
        <p>Файл: {{ $episode->filename }}</p>
    </div>

    <div class="info-grid">
        <div class="info-row">
            <div class="info-cell"><span class="label">Врач:</span> {{ $episode->user->name }}</div>
            <div class="info-cell"><span class="label">Диагноз:</span> {{ $episode->diagnosis_code }}</div>
        </div>
        <div class="info-row">
            <div class="info-cell"><span class="label">Дата проверки:</span> {{ $episode->created_at->format('d.m.Y H:i') }}</div>
            <div class="info-cell"><span class="label">Итоговое качество:</span> 
                <span style="font-size: 14px; font-weight: bold; color: {{ $episode->quality_score >= 80 ? '#16a34a' : ($episode->quality_score >= 60 ? '#ca8a04' : '#dc2626') }}">
                    {{ $episode->quality_score }}%
                </span>
            </div>
        </div>
    </div>

    <h3>Детализация по правилам</h3>
    <table>
        <thead>
            <tr>
                <th width="25%">Препарат / Группа</th>
                <th width="55%">Требуемая доза / Условие</th>
                <th width="20%">Статус</th>
            </tr>
        </thead>
        <tbody>
            @foreach(($episode->check_results ?? []) as $result)
                @if($result['status'] != 'NOT_APPLICABLE')
                <tr>
                    <td>{{ $result['drug'] }}</td>
                    <td>
                        {{ $result['dosage'] }}
                        @if(!empty($result['condition']))
                            <br><small style="color: #777;">{{ $result['condition'] }}</small>
                        @endif
                    </td>
                    <td>
                        @if($result['status'] == 'COMPLIANT')
                            <span class="status-ok">Соответствует</span>
                        @elseif($result['status'] == 'NON_COMPLIANT')
                            <span class="status-fail">Не соответствует</span>
                        @elseif($result['status'] == 'CATEGORY_MISSING_REQUIRED')
                            <span class="status-warn">Отсутствует обязательное</span>
                        @else
                            {{ $result['status'] }}
                        @endif
                    </td>
                </tr>
                @endif
            @endforeach
        </tbody>
    </table>

    <div class="footer">
        Сформировано автоматически системой МедАудит<br>
        {{ date('Y') }}
    </div>

</body>
</html>