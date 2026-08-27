<?php

namespace Tests\Feature;

use App\Http\Controllers\Api\UsuarioController;
use Tests\TestCase;

class UsuarioControllerTest extends TestCase
{
    public function test_usuario_controller_is_available_for_api_routes(): void
    {
        $this->assertTrue(class_exists(UsuarioController::class));

        $controller = app(UsuarioController::class);

        $this->assertInstanceOf(UsuarioController::class, $controller);
    }
}
