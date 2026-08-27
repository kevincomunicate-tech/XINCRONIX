<?php

namespace Database\Seeders;

use App\Models\Empresa;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class EmpresaSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Empresa::create([
            'nombre' => 'Xincronix Solutions',
            'nit' => '1234567890',
            'email' => 'contacto@xincronix.com',
            'telefono' => '+57 1 1234567',
            'direccion' => 'Calle 123 #456-789',
            'industria' => 'Tecnología',
            'plan_suscripcion' => 'business',
            'sector' => 'Software',
            'administrador' => 'Juan Pérez',
            'num_empleados' => '50-100',
            'fecha_creacion' => now(),
        ]);

        Empresa::create([
            'nombre' => 'Tech Innovators',
            'nit' => '0987654321',
            'email' => 'info@techinnovators.com',
            'telefono' => '+57 1 9876543',
            'direccion' => 'Avenida 456 #789-012',
            'industria' => 'Consultoría',
            'plan_suscripcion' => 'enterprise',
            'sector' => 'IT Consulting',
            'administrador' => 'María García',
            'num_empleados' => '100-500',
            'fecha_creacion' => now(),
        ]);
    }
}
