<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\AuthController;
use App\Http\Controllers\Api\EmpresaController;

Route::view('/', 'Login');

Route::middleware(['auth'])->group(function () {
    Route::get('/Admin_panel', [EmpresaController::class, 'index'])->name('admin.panel');
    Route::get('/admin/empresas', [EmpresaController::class, 'index']);
});

Route::view('/Agentes', 'Agentes')->name('agentes');
Route::view('/Proyecto', 'Proyecto')->name('proyecto');
Route::view('/Tareas', 'Tareas')->name('tareas');
Route::view('/Login', 'Login')->name('login');
Route::view('/Equipos', 'Equipos')->name('equipos');
Route::view('/Panel', 'Panel')->name('panel');
Route::view('/registro', 'registro')->name('registro');
Route::post('/registro', [AuthController::class, 'register']);
Route::view('/Analytics', 'Analytics')->name('analytics');
Route::view('/Asistente', 'Asistente')->name('asistente');
Route::view('/Automatizaciones', 'Automatizaciones')->name('automatizaciones');
