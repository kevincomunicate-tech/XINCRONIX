<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('roles', function (Blueprint $table) {
            $table->id('id_roles');
            $table->string('nombre', 80)->unique();
            $table->text('descripcion')->nullable();
        });

        // Insertar roles predeterminados
        DB::table('roles')->insert([
            ['id_roles' => 1, 'nombre' => 'Administrador', 'descripcion' => 'Acceso completo a la plataforma'],
            ['id_roles' => 2, 'nombre' => 'Manager', 'descripcion' => 'Gestión de equipos y proyectos'],
            ['id_roles' => 3, 'nombre' => 'Colaborador', 'descripcion' => 'Acceso básico a tareas asignadas'],
        ]);
    }

    public function down(): void
    {
        Schema::dropIfExists('roles');
    }
};
