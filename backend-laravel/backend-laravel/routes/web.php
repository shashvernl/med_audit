<?php

use App\Http\Controllers\ProfileController;
use App\Http\Controllers\EpisodeController;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Auth;

// Главная страница (доступна всем)
Route::get('/', function () {
    if (Auth::check()) {
        // Если пользователь авторизован, перенаправляем на общий дашборд
        return redirect()->route('dashboard');
    }
    
    // Если не авторизован, показываем страницу входа
    return view('auth.login');
});

// Группа маршрутов только для авторизованных пользователей
Route::middleware(['auth'])->group(function () {
    
    // Общий маршрут /dashboard работает как переключатель в зависимости от роли
    Route::get('/dashboard', function () {
        if (Auth::user()->isChief()) {
            return redirect('/dashboard/chief');
        }
        return redirect('/dashboard/doctor');
    })->name('dashboard');

    // Страница Главврача
    Route::get('/dashboard/chief', [EpisodeController::class, 'chiefIndex'])->name('dashboard.chief');

    // Страница Врача
    Route::get('/dashboard/doctor', [EpisodeController::class, 'doctorIndex'])->name('dashboard.doctor');

    // Загрузка нового эпикриза (доступно всем авторизованным)
    Route::post('/episodes', [EpisodeController::class, 'store'])->name('episodes.store');

    Route::get('/episodes/{episode}/download', [EpisodeController::class, 'download'])->name('episodes.download');
    
    // Просмотр конкретного эпикриза
    Route::get('/episodes/{episode}', [EpisodeController::class, 'show'])->name('episodes.show');

    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');

    Route::get('/episodes/{episode}/export', [App\Http\Controllers\EpisodeController::class, 'export'])->name('episodes.export');

    Route::middleware(['auth'])->prefix('admin')->group(function () {
    Route::get('/users', [App\Http\Controllers\Admin\UserController::class, 'index'])->name('admin.users.index');
    Route::patch('/users/{user}/role', [App\Http\Controllers\Admin\UserController::class, 'updateRole'])->name('admin.users.updateRole');
    Route::delete('/users/{user}', [App\Http\Controllers\Admin\UserController::class, 'destroy'])->name('admin.users.destroy');

    Route::delete('/episodes/{episode}', [App\Http\Controllers\EpisodeController::class, 'destroy'])->name('episodes.destroy');
});
});

require __DIR__.'/auth.php';