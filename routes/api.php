<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\CalendarioController;
use App\Http\Controllers\Api\EmpresaController;
use App\Http\Controllers\Api\EquipoController;
use App\Http\Controllers\Api\MensajeController;
use App\Http\Controllers\Api\MetricaRendimientoController;
use App\Http\Controllers\Api\NotificacionController;
use App\Http\Controllers\Api\ProyectoController;
use App\Http\Controllers\Api\ReunionController;
use App\Http\Controllers\Api\RolController;
use App\Http\Controllers\Api\SolicitudPagoController;
use App\Http\Controllers\Api\TareaController;
use App\Http\Controllers\Api\TicketSoporteController;
use App\Http\Controllers\Api\UsuarioController;

Route::post('login', [AuthController::class, 'login']);
Route::post('registro', [AuthController::class, 'register']);

Route::middleware('auth:sanctum')->group(function () {
    Route::get('me', [AuthController::class, 'me']);
    Route::post('logout', [AuthController::class, 'logout']);

    Route::get('proyectos/{proyecto}/kanban', [ProyectoController::class, 'kanban']);
    Route::patch('proyectos/{proyecto}/estado', [ProyectoController::class, 'cambiarEstado']);
    Route::apiResource('proyectos', ProyectoController::class);

    Route::get('tareas/init', [TareaController::class, 'init']);
    Route::patch('tareas/{tarea}/mover', [TareaController::class, 'mover']);
    Route::apiResource('tareas', TareaController::class);

    Route::get('mensajes/equipo', [MensajeController::class, 'equipo']);
    Route::get('mensajes/no-leidos', [MensajeController::class, 'noLeidos']);
    Route::apiResource('mensajes', MensajeController::class);

    Route::apiResource('usuarios', UsuarioController::class);
    Route::apiResource('empresas', EmpresaController::class);
    Route::apiResource('equipos', EquipoController::class);
    Route::apiResource('calendario', CalendarioController::class);
    Route::apiResource('metricas-rendimiento', MetricaRendimientoController::class);
    Route::apiResource('notificaciones', NotificacionController::class);
    Route::apiResource('reuniones', ReunionController::class);
    Route::apiResource('roles', RolController::class);
    Route::apiResource('solicitudes-pago', SolicitudPagoController::class);
    Route::apiResource('tickets-soporte', TicketSoporteController::class);
});
