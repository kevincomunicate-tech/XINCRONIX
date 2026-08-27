<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('solicitudes_pago', function (Blueprint $table) {
            $table->id('id_solicitud')->unsigned();
            $table->foreignId('id_empresa')->unsigned()->constrained('empresa', 'id_empresa')->onDelete('cascade');
            $table->string('plan', 50)->nullable();
            $table->string('metodo_pago', 50)->nullable();
            $table->string('referencia', 100)->nullable();
            $table->text('notas')->nullable();
            $table->string('ruta_comprobante', 300)->nullable();
            $table->string('estado', 30)->default('pendiente');
            $table->timestamp('fecha_creacion')->useCurrent();
            $table->timestamp('fecha_revision')->nullable();

            $table->index('id_empresa');
            $table->index('estado');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('solicitudes_pago');
    }
};
