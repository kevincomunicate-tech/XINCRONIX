<?php

namespace Database\Seeders;

use App\Models\SolicitudPago;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class SolicitudPagoSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        SolicitudPago::create([
            'id_empresa' => 1,
            'plan' => 'Plan Profesional',
            'metodo_pago' => 'Tarjeta de Crédito',
            'referencia' => 'TXN-2024-001',
            'notas' => 'Pago del primer mes de suscripción',
            'ruta_comprobante' => '/uploads/comprobantes/001.pdf',
            'estado' => 'completado',
            'fecha_creacion' => now()->subDays(5),
            'fecha_revision' => now()->subDays(4),
        ]);

        SolicitudPago::create([
            'id_empresa' => 2,
            'plan' => 'Plan Enterprise',
            'metodo_pago' => 'Transferencia Bancaria',
            'referencia' => 'TXN-2024-002',
            'notas' => 'Pago anual del plan enterprise',
            'ruta_comprobante' => '/uploads/comprobantes/002.pdf',
            'estado' => 'pendiente',
            'fecha_creacion' => now(),
        ]);
    }
}
