<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('tickets_soporte', function (Blueprint $table) {
            $table->id('id_ticket')->unsigned();
            $table->string('asunto', 200);
            $table->text('descripcion')->nullable();
            $table->string('prioridad', 20)->default('media');
            $table->string('estado', 30)->default('abierto');
            $table->foreignId('id_empresa')->unsigned()->nullable()->constrained('empresa', 'id_empresa')->onDelete('set null');
            $table->timestamp('fecha_creacion')->useCurrent();
            $table->timestamp('fecha_cierre')->nullable();

            $table->index('id_empresa');
            $table->index('estado');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('tickets_soporte');
    }
};
