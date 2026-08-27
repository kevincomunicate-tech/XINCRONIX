<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('proyecto', function (Blueprint $table) {
            $table->id('id_proyecto')->unsigned();
            $table->string('nombre', 150);
            $table->text('descripcion')->nullable();
            $table->string('estado', 50)->default('Activo');
            $table->integer('nivel_importancia')->default(1);
            $table->string('tipo_proyecto', 50)->nullable();
            $table->date('fecha_inicio')->nullable();
            $table->date('fecha_fin')->nullable();
            $table->foreignId('id_empresa')->unsigned()->constrained('empresa', 'id_empresa')->onDelete('cascade');
            $table->foreignId('id_equipo')->unsigned()->nullable()->constrained('equipos', 'id_equipo')->onDelete('set null');

            $table->index('id_empresa');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('proyecto');
    }
};
