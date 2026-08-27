<?php

namespace Database\Seeders;

use App\Models\Rol;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class RolSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        // Los roles predeterminados se insertan en la migración
        // Este seeder solo agrega roles adicionales si es necesario
        
        Rol::firstOrCreate(
            ['nombre' => 'Administrador'],
            ['descripcion' => 'Acceso completo a la plataforma']
        );
        
        Rol::firstOrCreate(
            ['nombre' => 'Manager'],
            ['descripcion' => 'Gestión de equipos y proyectos']
        );
        
        Rol::firstOrCreate(
            ['nombre' => 'Colaborador'],
            ['descripcion' => 'Acceso básico a tareas asignadas']
        );
    }
}
