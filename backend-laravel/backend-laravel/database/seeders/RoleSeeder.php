<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\User;
use Illuminate\Support\Facades\Hash;

class RoleSeeder extends Seeder
{
    public function run(): void
    {
        // Создаем или обновляем Главврача
        User::updateOrCreate(
            ['email' => 'chief@hospital.ru'],
            [
                'name' => 'Главный Врач',
                'password' => Hash::make('password'), // Пароль: password
                'role' => 'chief',
            ]
        );

        // Создаем или обновляем Обычного врача
        User::updateOrCreate(
            ['email' => 'doctor@hospital.ru'],
            [
                'name' => 'Иванов Иван',
                'password' => Hash::make('password'), // Пароль: password
                'role' => 'doctor',
            ]
        );
    }
}