<?php

namespace Database\Seeders;

use App\Models\Mensaje;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class MensajeSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Mensaje::create([
            'contenido' => '¿Tengo una duda respecto a la estructura de la base de datos?',
            'estado' => true,
            'fecha_envio' => now(),
            'id_usuario' => 3,
            'id_destinatario' => 2,
        ]);

        Mensaje::create([
            'contenido' => 'El proyecto está avanzando según lo planeado',
            'estado' => true,
            'fecha_envio' => now()->subHours(2),
            'id_usuario' => 2,
            'id_destinatario' => 1,
        ]);
    }
}
