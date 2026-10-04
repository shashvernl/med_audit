<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            {{ __('Панель Главного врача') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            
            <h3 class="text-lg font-medium mb-4">Рейтинг врачей по качеству эпикризов</h3>
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg mb-6">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead>
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Врач</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Количество проверок</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Среднее качество</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        @foreach($doctorsStats as $doctor)
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap font-medium">{{ $doctor->name }}</td>
                            <td class="px-6 py-4 whitespace-nowrap">{{ $doctor->total }}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="w-full bg-gray-200 rounded-full h-2.5">
                                    <div class="bg-blue-600 h-2.5 rounded-full" style="width: {{ $doctor->avg_score }}%"></div>
                                </div>
                                <span class="text-sm text-gray-600">{{ round($doctor->avg_score, 1) }}%</span>
                            </td>
                        </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>

            <h3 class="text-lg font-medium mb-4">Все эпикризы больницы</h3>
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900">
                     <table class="min-w-full divide-y divide-gray-200">
                        <thead>
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Врач</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Файл</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Диагноз</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Качество</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Действие</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            @foreach($episodes as $ep)
                            <tr>
                                <td class="px-6 py-4 whitespace-nowrap">{{ $ep->user->name }}</td>
                                <td class="px-6 py-4 whitespace-nowrap">{{ $ep->filename }}</td>
                                <td class="px-6 py-4 whitespace-nowrap">{{ $ep->diagnosis_code }}</td>
                                <td class="px-6 py-4 whitespace-nowrap">
                                     <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                        {{ $ep->quality_score >= 80 ? 'bg-green-100 text-green-800' : ($ep->quality_score >= 60 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800') }}">
                                        {{ $ep->quality_score }}%
                                    </span>
                                </td>
                                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                    <a href="{{ route('episodes.show', $ep) }}" class="text-indigo-600 hover:text-indigo-900">Просмотр</a>
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