<?php

namespace Database\Seeders;

use App\Models\Equipo;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class EquipoSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Equipo::create([
            'nombre' => 'Equipo Backend',
            'descripcion' => 'Equipo encargado del desarrollo backend',
            'miembros' => 3,
            'fecha_inicio' => now(),
            'id_empresa' => 1,
        ]);

        Equipo::create([
            'nombre' => 'Equipo Frontend',
            'descripcion' => 'Equipo encargado del desarrollo frontend',
            'miembros' => 2,
            'fecha_inicio' => now(),
            'id_empresa' => 1,
        ]);

        Equipo::create([
            'nombre' => 'Equipo QA',
            'descripcion' => 'Equipo de aseguramiento de calidad',
            'miembros' => 1,
            'fecha_inicio' => now(),
            'id_empresa' => 2,
        ]);
    }
}
