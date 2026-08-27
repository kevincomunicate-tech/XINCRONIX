<?php

namespace Database\Seeders;

use App\Models\MetricaRendimiento;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class MetricaRendimientoSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        MetricaRendimiento::create([
            'tipo_metrica' => 'Tareas completadas',
            'valor' => 15.50,
            'fecha_inicio_periodo' => now()->subDays(30),
            'fecha_fin_periodo' => now(),
            'id_usuario' => 3,
        ]);

        MetricaRendimiento::create([
            'tipo_metrica' => 'Tasa de cumplimiento',
            'valor' => 92.30,
            'fecha_inicio_periodo' => now()->subDays(30),
            'fecha_fin_periodo' => now(),
            'id_usuario' => 3,
        ]);

        MetricaRendimiento::create([
            'tipo_metrica' => 'Horas productivas',
            'valor' => 156.75,
            'fecha_inicio_periodo' => now()->subDays(30),
            'fecha_fin_periodo' => now(),
            'id_usuario' => 4,
        ]);
    }
}
