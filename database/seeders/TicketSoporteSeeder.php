<?php

namespace Database\Seeders;

use App\Models\TicketSoporte;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class TicketSoporteSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        TicketSoporte::create([
            'asunto' => 'Error en la generación de reportes',
            'descripcion' => 'Los reportes no se generan correctamente en el módulo de análisis',
            'prioridad' => 'alta',
            'estado' => 'abierto',
            'id_empresa' => 1,
            'fecha_creacion' => now()->subDays(2),
        ]);

        TicketSoporte::create([
            'asunto' => 'Solicitud de nueva funcionalidad',
            'descripcion' => 'Se requiere agregar filtros avanzados al dashboard',
            'prioridad' => 'media',
            'estado' => 'en_progreso',
            'id_empresa' => 1,
            'fecha_creacion' => now()->subDays(1),
        ]);

        TicketSoporte::create([
            'asunto' => 'Problema de rendimiento',
            'descripcion' => 'La aplicación se ralentiza al cargar grandes volúmenes de datos',
            'prioridad' => 'alta',
            'estado' => 'cerrado',
            'id_empresa' => 2,
            'fecha_creacion' => now()->subDays(5),
            'fecha_cierre' => now()->subDays(1),
        ]);
    }
}
