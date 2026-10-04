<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('episodes', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->onDelete('cascade'); // Связь с врачом
            $table->string('filename'); // Имя файла
            $table->string('diagnosis_code')->nullable(); // Код МКБ (I21, I50...)
            $table->json('extracted_facts')->nullable(); // Сырые данные из Python
            $table->json('check_results')->nullable();   // Результаты проверки
            $table->decimal('quality_score', 5, 2)->nullable(); // Процент качества
            $table->enum('status', ['pending', 'completed', 'failed'])->default('pending');
            $table->timestamps();
        });
    }
    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('episodes');
    }
};
