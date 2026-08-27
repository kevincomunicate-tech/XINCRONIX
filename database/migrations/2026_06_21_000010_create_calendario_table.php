<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('calendario', function (Blueprint $table) {
            $table->id('id_calendario')->unsigned();
            $table->timestamp('fecha_evento');
            $table->text('nota')->nullable();
            $table->foreignId('id_usuario')->unsigned()->constrained('usuarios', 'id_usuario')->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('calendario');
    }
};
