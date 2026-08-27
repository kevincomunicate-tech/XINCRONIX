<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('tareas', function (Blueprint $table) {
            $table->id('id_tarea')->unsigned();
            $table->string('titulo', 200);
            $table->text('descripcion')->nullable();
            $table->string('estado', 50)->default('Por Hacer');
            $table->timestamp('fecha_creacion')->useCurrent();
            $table->date('fecha_vencimiento')->nullable();
            $table->foreignId('id_proyecto')->unsigned()->constrained('proyecto', 'id_proyecto')->onDelete('cascade');
            $table->foreignId('id_usuario')->unsigned()->nullable()->constrained('usuarios', 'id_usuario')->onDelete('set null');
            $table->foreignId('id_equipo')->unsigned()->nullable()->constrained('equipos', 'id_equipo')->onDelete('set null');

            $table->index('id_proyecto');
            $table->index('id_usuario');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('tareas');
    }
};
