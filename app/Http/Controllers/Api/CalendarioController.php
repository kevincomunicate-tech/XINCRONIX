<?php

namespace App\Http\Controllers\Api;

use App\Models\Calendario;

class CalendarioController extends AbstractApiResourceController
{
    protected string $model = Calendario::class;
    protected ?string $userColumn = 'id_usuario';

    protected array $storeRules = [
        'fecha_evento' => ['required', 'date'],
        'nota' => ['nullable', 'string'],
    ];

    protected array $updateRules = [
        'fecha_evento' => ['sometimes', 'date'],
        'nota' => ['nullable', 'string'],
    ];
}
