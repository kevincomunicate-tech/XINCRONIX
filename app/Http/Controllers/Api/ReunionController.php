<?php

namespace App\Http\Controllers\Api;

use App\Models\Reunion;

class ReunionController extends AbstractApiResourceController
{
    protected string $model = Reunion::class;
    protected ?string $userColumn = 'id_usuario';

    protected array $storeRules = [
        'nombre' => ['required', 'string', 'max:150'],
        'enlace' => ['nullable', 'string', 'max:300'],
        'fecha' => ['required', 'date'],
        'estado' => ['nullable', 'string', 'max:50'],
        'grabacion_url' => ['nullable', 'string', 'max:500'],
        'id_equipo' => ['nullable', 'integer'],
    ];

    protected array $updateRules = [
        'nombre' => ['sometimes', 'string', 'max:150'],
        'enlace' => ['nullable', 'string', 'max:300'],
        'fecha' => ['sometimes', 'date'],
        'estado' => ['nullable', 'string', 'max:50'],
        'grabacion_url' => ['nullable', 'string', 'max:500'],
        'id_equipo' => ['nullable', 'integer'],
    ];
}
