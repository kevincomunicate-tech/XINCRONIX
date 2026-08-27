<?php

namespace Database\Seeders;

use App\Models\PerfilEspecifico;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class PerfilEspecificoSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        PerfilEspecifico::create([
            'nombre' => 'Desarrollador Backend',
            'descripcion' => 'Especializado en desarrollo de APIs y bases de datos',
        ]);

        PerfilEspecifico::create([
            'nombre' => 'Desarrollador Frontend',
            'descripcion' => 'Especializado en interfaces de usuario',
        ]);

        PerfilEspecifico::create([
            'nombre' => 'Project Manager',
            'descripcion' => 'Gestiona proyectos y equipos',
        ]);

        PerfilEspecifico::create([
            'nombre' => 'QA Engineer',
            'descripcion' => 'Aseguramiento de calidad y pruebas',
        ]);
    }
}
