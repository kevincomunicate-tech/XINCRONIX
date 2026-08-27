<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('reuniones', function (Blueprint $table) {
            $table->id('id_reunion')->unsigned();
            $table->string('nombre', 150);
            $table->string('enlace', 300)->nullable();
            $table->timestamp('fecha');
            $table->string('estado', 50)->default('Programada');
            $table->string('grabacion_url', 500)->nullable();
            $table->foreignId('id_equipo')->unsigned()->nullable()->constrained('equipos', 'id_equipo')->onDelete('set null');
            $table->foreignId('id_usuario')->unsigned()->nullable()->constrained('usuarios', 'id_usuario')->onDelete('set null');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('reuniones');
    }
};
