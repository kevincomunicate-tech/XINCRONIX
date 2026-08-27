<?php

namespace Database\Seeders;

use App\Models\Calendario;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class CalendarioSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Calendario::create([
            'fecha_evento' => now()->addDays(5)->setHour(14),
            'nota' => 'Reunión de equipo Backend',
            'id_usuario' => 3,
        ]);

        Calendario::create([
            'fecha_evento' => now()->addDays(10)->setHour(10),
            'nota' => 'Entrega de hito 1 del proyecto',
            'id_usuario' => 2,
        ]);

        Calendario::create([
            'fecha_evento' => now()->addDays(15)->setHour(9),
            'nota' => 'Presentación al cliente',
            'id_usuario' => 1,
        ]);
    }
}
