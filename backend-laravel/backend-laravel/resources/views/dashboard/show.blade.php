<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            Результаты проверки: {{ $episode->filename }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg p-6">
                
                <!-- Верхняя панель с общей информацией -->
                <div class="flex justify-between items-center mb-6 border-b pb-4">
                    <div>
                        <p class="text-sm text-gray-500">Врач: {{ $episode->user->name }}</p>
                        <p class="text-sm text-gray-500">Диагноз: <span class="font-bold text-black">{{ $episode->diagnosis_code }}</span></p>
                        
                        {{-- Перевод технического статуса на русский --}}
                        @php
                            $statusMap = [
                                'completed' => 'Завершен',
                                'pending' => 'В обработке',
                                'failed' => 'Ошибка'
                            ];
                            $ruStatus = $statusMap[$episode->status] ?? $episode->status;
                        @endphp
                        <p class="text-sm text-gray-500">Статус: {{ $ruStatus }}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm text-gray-500">Итоговое качество</p>
                        <p class="text-3xl font-bold {{ $episode->quality_score >= 80 ? 'text-green-600' : ($episode->quality_score >= 60 ? 'text-yellow-600' : 'text-red-600') }}">
                            {{ number_format($episode->quality_score, 1, ',', ' ') }}%
                        </p>
                    </div>
                </div>

                <!-- Таблица с результатами проверки -->
                <h3 class="text-lg font-medium mb-4">Детализация по правилам</h3>
                
                @if($episode->check_results || $episode->extracted_facts)
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead>
                            <tr>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase w-[25%]">Препарат / Группа</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase w-[55%]">Требуемая доза / Условие</th>
                                <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase w-[20%]">Статус</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            
                            {{-- 1. Выводим результаты проверки правил (Категории) --}}
                            @foreach(($episode->check_results ?? []) as $result)
                                {{-- Пропускаем "Не применимо" из правил, чтобы не засорять таблицу --}}
                                @if($result['status'] != 'NOT_APPLICABLE')
                                <tr>
                                    <td class="px-4 py-2 font-medium text-sm align-top capitalize">
                                        {{ $result['drug'] }}
                                    </td>
                                    <td class="px-4 py-2 text-sm text-gray-600 align-top">
                                        
                                        {{-- ИЗМЕНЕНИЕ: Проверка, нужно ли писать слово "Доза:" --}}
                                        @if(str_contains($result['drug'], 'Диагностика') || str_contains($result['drug'], 'Процедуры') || str_contains($result['drug'], 'Контроль:'))
                                            <div class="mb-1 font-medium text-gray-700">
                                                {{ $result['dosage'] }}
                                            </div>
                                        @else
                                            <div class="mb-1">
                                                Доза: {{ $result['dosage'] }}
                                            </div>
                                        @endif
                                        
                                        @if(!empty($result['condition']))
                                        <div class="text-xs text-gray-400">
                                            @php
                                                // Логика правильного склонения слова "вариант"
                                                $condText = $result['condition'];
                                                if (preg_match('/\((\d+) вариантов\)/', $condText, $matches)) {
                                                    $count = (int)$matches[1];
                                                    $word = 'вариантов';
                                                    
                                                    if ($count % 10 == 1 && $count % 100 != 11) {
                                                        $word = 'вариант';
                                                    } elseif (in_array($count % 10, [2, 3, 4]) && !in_array($count % 100, [12, 13, 14])) {
                                                        $word = 'варианта';
                                                    }
                                                    
                                                    $condText = str_replace($matches[0], "({$count} {$word})", $condText);
                                                }
                                            @endphp
                                            {{ $condText }}
                                        </div>
                                        @endif
                                    </td>
                                    <td class="px-4 py-2 align-top">
                                        @if($result['status'] == 'COMPLIANT')
                                            <span class="px-2 py-1 rounded text-xs bg-green-100 text-green-800 whitespace-nowrap inline-block">Соответствует</span>
                                        @elseif($result['status'] == 'NON_COMPLIANT')
                                            <span class="px-2 py-1 rounded text-xs bg-red-100 text-red-800 whitespace-nowrap inline-block">Не соответствует</span>
                                        @elseif($result['status'] == 'CATEGORY_MISSING_REQUIRED')
                                            <span class="px-2 py-1 rounded text-xs bg-orange-100 text-orange-800 whitespace-nowrap inline-block">Отсутствует обязательное</span>
                                        @endif
                                    </td>
                                </tr>
                                @endif
                            @endforeach

                            {{-- 2. Выводим найденные в эпикризе препараты и ПРОЦЕДУРЫ, которые НЕ попали в правила --}}
                            @foreach(($episode->extracted_facts ?? []) as $fact)
                                {{-- Показываем лекарства и процедуры --}}
                                @if(in_array($fact['fact_type'], ['drug', 'procedure']))
                                <tr class="bg-gray-50">
                                    <td class="px-4 py-2 text-sm text-gray-700 align-top capitalize">
                                        {{ $fact['fact_name'] }}
                                        @if(!empty($fact['fact_value']) && $fact['fact_value'] != 'выполнено')
                                            <span class="text-gray-500 font-normal">({{ $fact['fact_value'] }} {{ $fact['fact_unit'] ?? '' }})</span>
                                        @endif
                                    </td>
                                    <td class="px-4 py-2 text-sm text-gray-500 italic align-top">
                                        @if($fact['fact_type'] == 'procedure')
                                            Процедура обнаружена в тексте эпикриза.
                                        @else
                                            Препарат обнаружен в тексте, но не требуется по данному диагнозу.
                                        @endif
                                    </td>
                                    <td class="px-4 py-2 align-top">
                                        <span class="px-2 py-1 rounded text-xs bg-gray-100 text-gray-500 whitespace-nowrap inline-block">Не применимо / Найдено</span>
                                    </td>
                                </tr>
                                @endif
                            @endforeach

                        </tbody>
                    </table>
                </div>
                @else
                <p class="text-gray-500 italic">Результаты анализа отсутствуют или ошибка обработки.</p>
                @endif
                
                <div class="mt-6 pt-4 border-t flex justify-between items-center">
                    <a href="{{ url()->previous() }}" class="text-blue-600 hover:text-blue-800 font-medium">&larr; Вернуться назад</a>
                    
                    {{-- Кнопка скачивания оригинала --}}
                    <a href="{{ route('episodes.download', $episode) }}" target="_blank" class="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Скачать PDF
                    </a>
                </div>
            </div>
        </div>
    </div>
</x-app-layout>