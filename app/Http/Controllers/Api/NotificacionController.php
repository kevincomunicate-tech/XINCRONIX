<?php

namespace App\Http\Controllers\Api;

use App\Models\Notificacion;

class NotificacionController extends AbstractApiResourceController
{
    protected string $model = Notificacion::class;
    protected ?string $userColumn = 'id_usuario';

    protected array $storeRules = [
        'titulo' => ['required', 'string', 'max:100'],
        'mensaje' => ['required', 'string'],
        'tipo' => ['nullable', 'string', 'max:50'],
        'estado' => ['nullable', 'boolean'],
        'leida' => ['nullable', 'boolean'],
    ];

    protected array $updateRules = [
        'titulo' => ['sometimes', 'string', 'max:100'],
        'mensaje' => ['sometimes', 'string'],
        'tipo' => ['nullable', 'string', 'max:50'],
        'estado' => ['nullable', 'boolean'],
        'leida' => ['nullable', 'boolean'],
    ];
}
