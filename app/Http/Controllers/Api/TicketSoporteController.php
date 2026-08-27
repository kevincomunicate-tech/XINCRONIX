<?php

namespace App\Http\Controllers\Api;

use App\Models\TicketSoporte;

class TicketSoporteController extends AbstractApiResourceController
{
    protected string $model = TicketSoporte::class;
    protected ?string $companyColumn = 'id_empresa';

    protected array $storeRules = [
        'asunto' => ['required', 'string', 'max:200'],
        'descripcion' => ['nullable', 'string'],
        'prioridad' => ['nullable', 'string', 'max:20'],
        'estado' => ['nullable', 'string', 'max:30'],
        'fecha_cierre' => ['nullable', 'date'],
    ];

    protected array $updateRules = [
        'asunto' => ['sometimes', 'string', 'max:200'],
        'descripcion' => ['nullable', 'string'],
        'prioridad' => ['nullable', 'string', 'max:20'],
        'estado' => ['nullable', 'string', 'max:30'],
        'fecha_cierre' => ['nullable', 'date'],
    ];
}
