<?php

namespace Database\Seeders;

use App\Models\Notificacion;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class NotificacionSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Notificacion::create([
            'titulo' => 'Nueva tarea asignada',
            'mensaje' => 'Se te ha asignado una nueva tarea: Crear endpoints API',
            'tipo' => 'Tarea',
            'fecha_envio' => now(),
            'estado' => true,
            'leida' => false,
            'id_usuario' => 3,
        ]);

        Notificacion::create([
            'titulo' => 'Vencimiento próximo',
            'mensaje' => 'La tarea Diseñar base de datos vence en 2 días',
            'tipo' => 'Alerta',
            'fecha_envio' => now(),
            'estado' => true,
            'leida' => false,
            'id_usuario' => 3,
        ]);
    }
}
