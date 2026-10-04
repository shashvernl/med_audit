<x-guest-layout title="Вход в систему">

    <div class="mb-8 text-center">
        <h2 class="text-3xl font-bold text-gray-800">МедАудит</h2>
        <p class="mt-2 text-sm text-gray-600">Система проверки клинических рекомендаций</p>
    </div>

    <!-- Session Status -->
    <x-auth-session-status class="mb-4" :status="session('status')" />

    <form method="POST" action="{{ route('login') }}" class="space-y-6">
        @csrf

        <!-- Email Address -->
        <div>
            <x-input-label for="email" :value="__('Email')" />
            <x-text-input id="email" class="block mt-1 w-full" type="email" name="email" :value="old('email')" required autofocus autocomplete="username" />
            <x-input-error :messages="$errors->get('email')" class="mt-2" />
        </div>

        <!-- Password -->
        <div class="relative">
            <x-input-label for="password" :value="__('Пароль')" />
            <x-text-input id="password" class="block mt-1 w-full"
                            type="password"
                            name="password"
                            required autocomplete="current-password" />
            <x-input-error :messages="$errors->get('password')" class="mt-2" />
        </div>

        <!-- Remember Me -->
        <div class="flex items-center justify-between">
            <label for="remember_me" class="inline-flex items-center">
                <input id="remember_me" type="checkbox" class="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500" name="remember">
                <span class="ms-2 text-sm text-gray-600">{{ __('Запомнить меня') }}</span>
            </label>

            @if (Route::has('password.request'))
                <a class="underline text-sm text-gray-600 hover:text-gray-900 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" href="{{ route('password.request') }}">
                    {{ __('Забыли пароль?') }}
                </a>
            @endif
        </div>

        <div class="flex items-center justify-end mt-4">
            <x-primary-button class="w-full justify-center py-3 bg-blue-600 hover:bg-blue-700 transition duration-150 ease-in-out">
                {{ __('Войти') }}
            </x-primary-button>
        </div>
        
        <div class="text-center mt-4 text-sm text-gray-600">
            Нет аккаунта? 
            <a href="{{ route('register') }}" class="font-medium text-blue-600 hover:text-blue-500 underline">Зарегистрироваться</a>
        </div>
    </form>
</x-guest-layout>