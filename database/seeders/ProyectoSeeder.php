<?php

namespace Database\Seeders;

use App\Models\Proyecto;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class ProyectoSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Proyecto::create([
            'nombre' => 'Proyecto X - Portal Web',
            'descripcion' => 'Desarrollo del portal web corporativo',
            'estado' => 'En Progreso',
            'fecha_inicio' => now()->subDays(30),
            'fecha_fin' => now()->addDays(60),
            'id_empresa' => 1,
            'id_equipo' => 1,
        ]);

        Proyecto::create([
            'nombre' => 'Proyecto Y - App Móvil',
            'descripcion' => 'Desarrollo de aplicación móvil para gestión',
            'estado' => 'Planeación',
            'fecha_inicio' => now()->addDays(10),
            'fecha_fin' => now()->addDays(120),
            'id_empresa' => 1,
            'id_equipo' => 2,
        ]);

        Proyecto::create([
            'nombre' => 'Proyecto Z - Testing',
            'descripcion' => 'Pruebas integral del sistema',
            'estado' => 'En Progreso',
            'fecha_inicio' => now(),
            'fecha_fin' => now()->addDays(15),
            'id_empresa' => 2,
            'id_equipo' => 3,
        ]);
    }
}
