<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('empresa', function (Blueprint $table) {
            $table->id('id_empresa')->unsigned();
            $table->string('nombre', 200);
            $table->string('nit', 30)->unique();
            $table->string('email', 150)->unique();
            $table->string('telefono', 20)->nullable();
            $table->string('direccion', 300)->nullable();
            $table->string('industria', 100)->nullable();
            $table->string('plan_suscripcion', 50)->default('business');
            $table->string('sector', 50)->nullable();
            $table->string('administrador', 120)->nullable();
            $table->string('num_empleados', 30)->nullable();
            $table->string('comprobante', 250)->nullable();
            $table->timestamp('fecha_actualizacion')->useCurrent()->useCurrentOnUpdate();
            $table->timestamp('fecha_creacion')->useCurrent();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('empresa');
    }
};
