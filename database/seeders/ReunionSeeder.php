<?php

namespace Database\Seeders;

use App\Models\Reunion;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class ReunionSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Reunion::create([
            'nombre' => 'Stand-up Equipo Backend',
            'enlace' => 'https://meet.google.com/ejemplo',
            'fecha' => now()->addDays(1)->setHour(10),
            'estado' => 'Programada',
            'id_equipo' => 1,
            'id_usuario' => 2,
        ]);

        Reunion::create([
            'nombre' => 'Retrospectiva Proyecto X',
            'enlace' => 'https://meet.google.com/ejemplo2',
            'fecha' => now()->addDays(7)->setHour(14),
            'estado' => 'Programada',
            'id_equipo' => 1,
            'id_usuario' => 2,
        ]);
    }
}
