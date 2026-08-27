<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('equipos', function (Blueprint $table) {
            $table->id('id_equipo')->unsigned();
            $table->string('nombre', 150);
            $table->text('descripcion')->nullable();
            $table->integer('miembros')->default(0);
            $table->timestamp('fecha_inicio')->nullable();
            $table->timestamp('fecha_fin')->nullable();
            $table->foreignId('id_empresa')->unsigned()->constrained('empresa', 'id_empresa')->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('equipos');
    }
};
