<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        $this->call([
            EmpresaSeeder::class,
            RolSeeder::class,
            PerfilEspecificoSeeder::class,
            UsuarioSeeder::class,
            EquipoSeeder::class,
            ProyectoSeeder::class,
            TareaSeeder::class,
            ReunionSeeder::class,
            MensajeSeeder::class,
            NotificacionSeeder::class,
            CalendarioSeeder::class,
            SolicitudPagoSeeder::class,
            TicketSoporteSeeder::class,
            MetricaRendimientoSeeder::class,
        ]);
    }
}
