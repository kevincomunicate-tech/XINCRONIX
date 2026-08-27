<?php

namespace Database\Seeders;

use App\Models\Usuario;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class UsuarioSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        Usuario::create([
            'nombres' => 'Juan',
            'apellidos' => 'Administrador',
            'email' => 'admin@xincronix.com',
            'password' => Hash::make('password123'),
            'estado' => true,
            'id_empresa' => 1,
            'id_roles' => 1,
            'id_perfil' => 1,
            'fecha_creacion' => now(),
        ]);

        Usuario::create([
            'nombres' => 'María',
            'apellidos' => 'Manager',
            'email' => 'manager@xincronix.com',
            'password' => Hash::make('password123'),
            'estado' => true,
            'id_empresa' => 1,
            'id_roles' => 2,
            'id_perfil' => 3,
            'fecha_creacion' => now(),
        ]);

        Usuario::create([
            'nombres' => 'Carlos',
            'apellidos' => 'Desarrollador',
            'email' => 'carlos@xincronix.com',
            'password' => Hash::make('password123'),
            'estado' => true,
            'id_empresa' => 1,
            'id_roles' => 3,
            'id_perfil' => 1,
            'fecha_creacion' => now(),
        ]);

        Usuario::create([
            'nombres' => 'Ana',
            'apellidos' => 'Frontend',
            'email' => 'ana@xincronix.com',
            'password' => Hash::make('password123'),
            'estado' => true,
            'id_empresa' => 1,
            'id_roles' => 3,
            'id_perfil' => 2,
            'fecha_creacion' => now(),
        ]);

        Usuario::create([
            'nombres' => 'Pedro',
            'apellidos' => 'QA',
            'email' => 'pedro@xincronix.com',
            'password' => Hash::make('password123'),
            'estado' => true,
            'id_empresa' => 2,
            'id_roles' => 3,
            'id_perfil' => 4,
            'fecha_creacion' => now(),
        ]);
    }
}
