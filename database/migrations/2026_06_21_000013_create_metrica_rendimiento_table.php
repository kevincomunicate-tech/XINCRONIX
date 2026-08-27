<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('metrica_rendimiento', function (Blueprint $table) {
            $table->id('id_metrica')->unsigned();
            $table->string('tipo_metrica', 100);
            $table->decimal('valor', 12, 4);
            $table->date('fecha_inicio_periodo');
            $table->date('fecha_fin_periodo');
            $table->foreignId('id_usuario')->unsigned()->constrained('usuarios', 'id_usuario')->onDelete('cascade');

            $table->index('id_usuario');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('metrica_rendimiento');
    }
};
