<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('mensajes', function (Blueprint $table) {
            $table->id('id_mensajes')->unsigned();
            $table->text('contenido');
            $table->timestamp('fecha_envio')->useCurrent();
            $table->boolean('estado')->default(false);
            $table->foreignId('id_usuario')->unsigned()->constrained('usuarios', 'id_usuario')->onDelete('cascade');
            $table->foreignId('id_destinatario')->unsigned()->nullable()->constrained('usuarios', 'id_usuario')->onDelete('set null');

            $table->index('id_usuario');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('mensajes');
    }
};
