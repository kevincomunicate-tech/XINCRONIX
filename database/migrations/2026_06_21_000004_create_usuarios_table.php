<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('usuarios', function (Blueprint $table) {
            $table->id('id_usuario')->unsigned();
            $table->string('nombres', 100);
            $table->string('apellidos', 100);
            $table->string('email', 150)->unique();
            $table->string('password', 255);
            $table->string('cargo', 80)->nullable();
            $table->string('telefono', 20)->nullable();
            $table->string('avatar', 300)->nullable();
            $table->boolean('estado')->default(true);
            $table->timestamp('fecha_creacion')->useCurrent();
            $table->foreignId('id_empresa')->unsigned()->constrained('empresa', 'id_empresa')->onDelete('cascade');
            $table->foreignId('id_roles')->constrained('roles', 'id_roles')->default(3);
            $table->foreignId('id_perfil')->unsigned()->nullable()->constrained('perfiles_especificos', 'id_perfil')->onDelete('set null');

            $table->index('email');
            $table->index('id_empresa');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('usuarios');
    }
};
