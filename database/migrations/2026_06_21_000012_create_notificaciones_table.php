<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('notificaciones', function (Blueprint $table) {
            $table->id('id_notificaciones')->unsigned();
            $table->string('titulo', 100);
            $table->text('mensaje');
            $table->string('tipo', 50)->nullable();
            $table->timestamp('fecha_envio')->useCurrent();
            $table->boolean('estado')->default(false);
            $table->boolean('leida')->default(false);
            $table->foreignId('id_usuario')->unsigned()->constrained('usuarios', 'id_usuario')->onDelete('cascade');

            $table->index('id_usuario');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('notificaciones');
    }
};
