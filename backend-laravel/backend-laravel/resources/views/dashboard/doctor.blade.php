<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            {{ __('Кабинет врача') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            
            <!-- Форма загрузки -->
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6 p-6">
                <h3 class="text-lg font-medium mb-4">Загрузить эпикризы (PDF)</h3>
                
                <form action="{{ route('episodes.store') }}" method="POST" enctype="multipart/form-data" id="uploadForm">
                    @csrf
                    <div class="flex items-center gap-4">
                        <input type="file" name="files[]" accept=".pdf" multiple required 
                               class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none"
                               id="fileInput">
                        
                        <button type="submit" id="submitBtn" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition whitespace-nowrap">
                            Проверить файлы
                        </button>
                    </div>
                    
                    <!-- Список выбранных файлов -->
                    <div id="fileList" class="mt-4 text-sm text-gray-600 hidden">
                        <p class="font-medium">Выбрано файлов: <span id="fileCount">0</span></p>
                        <ul id="fileNames" class="list-disc pl-5 mt-2"></ul>
                    </div>

                    @error('files') <span class="text-red-500 text-sm mt-2 block">{{ $message }}</span> @enderror
                </form>

                @if (session('success'))
                    {{-- Добавлен класс text-sm для уменьшения шрифта --}}
                    <div class="mt-4 p-2 bg-green-100 text-green-700 rounded border border-green-200 text-sm">
                        {{ session('success') }}
                    </div>
                @endif
                
                @if ($errors->any())
                    <div class="mt-4 p-3 bg-red-100 text-red-700 rounded border border-red-200 text-sm">
                        <ul class="list-disc pl-5">
                            @foreach ($errors->all() as $error)
                                <li>{{ $error }}</li>
                            @endforeach
                        </ul>
                    </div>
                @endif
            </div>

            <!-- Статистика -->
            <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="bg-white p-4 rounded shadow border-l-4 border-blue-500">
                    <div class="text-gray-500">Всего проверок</div>
                    <div class="text-2xl font-bold">{{ $myStats->total ?? 0 }}</div>
                </div>
                <div class="bg-white p-4 rounded shadow border-l-4 border-green-500">
                    <div class="text-gray-500">Среднее качество</div>
                    <div class="text-2xl font-bold text-green-600">{{ round($myStats->avg_score ?? 0, 1) }}%</div>
                </div>
            </div>

            <!-- Список -->
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead>
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Файл</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Диагноз</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Качество</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Дата</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Действие</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            @foreach($episodes as $ep)
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <a href="{{ route('episodes.download', $ep) }}" 
                                    target="_blank" 
                                    class="text-blue-600 hover:text-blue-900 hover:underline flex items-center gap-1">

                                        {{ $ep->filename }}
                                    </a>
                                </td>

                                <td class="px-6 py-4 whitespace-nowrap">{{ $ep->diagnosis_code }}</td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                        {{ $ep->quality_score >= 80 ? 'bg-green-100 text-green-800' : ($ep->quality_score >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800') }}">
                                        {{ $ep->quality_score }}%
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap">{{ $ep->created_at->format('d.m.Y H:i') }}</td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <a href="{{ route('episodes.show', $ep) }}" class="text-indigo-600 hover:text-indigo-900">Просмотр</a>
                                    <form action="{{ route('episodes.destroy', $ep) }}" method="POST" class="inline-block" onsubmit="return confirm('Вы уверены, что хотите удалить этот эпикриз? Это действие нельзя отменить.');">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" class="text-red-600 hover:text-red-900">
                                        Удалить
                                    </button>
                                </form>
                                </td>
                            </tr>
                            @endforeach
                        </tbody>
                    </table>
                    <div class="mt-4">{{ $episodes->links() }}</div>
                </div>
            </div>
        </div>
    </div>
</x-app-layout>

<script>
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const fileNames = document.getElementById('fileNames');
    const fileCount = document.getElementById('fileCount');
    const submitBtn = document.getElementById('submitBtn');
    const form = document.getElementById('uploadForm');

    fileInput.addEventListener('change', function() {
        fileNames.innerHTML = '';
        if (this.files.length > 0) {
            fileList.classList.remove('hidden');
            fileCount.textContent = this.files.length;
            Array.from(this.files).forEach(file => {
                const li = document.createElement('li');
                li.textContent = file.name;
                fileNames.appendChild(li);
            });
        } else {
            fileList.classList.add('hidden');
        }
    });

    form.addEventListener('submit', function() {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Обработка... Пожалуйста, подождите';
        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
    });
</script>