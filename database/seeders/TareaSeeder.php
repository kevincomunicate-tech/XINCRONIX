<?php

namespace Database\Seeders;

use App\Models\Tarea;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class TareaSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Tarea::create([
            'titulo' => 'Diseñar base de datos',
            'descripcion' => 'Diseño de la estructura de la base de datos',
            'estado' => 'En Progreso',
            'prioridad' => 'Alta',
            'fecha_vencimiento' => now()->addDays(5),
            'id_proyecto' => 1,
            'id_usuario' => 3,
            'id_equipo' => 1,
            'fecha_creacion' => now(),
        ]);

        Tarea::create([
            'titulo' => 'Crear endpoints API',
            'descripcion' => 'Implementar los endpoints principales de la API',
            'estado' => 'Pendiente',
            'prioridad' => 'Alta',
            'fecha_vencimiento' => now()->addDays(10),
            'id_proyecto' => 1,
            'id_usuario' => 3,
            'id_equipo' => 1,
            'fecha_creacion' => now(),
        ]);

        Tarea::create([
            'titulo' => 'Diseño UI/UX',
            'descripcion' => 'Diseño de la interfaz de usuario',
            'estado' => 'Pendiente',
            'prioridad' => 'Media',
            'fecha_vencimiento' => now()->addDays(7),
            'id_proyecto' => 1,
            'id_usuario' => 4,
            'id_equipo' => 2,
            'fecha_creacion' => now(),
        ]);
    }
}
