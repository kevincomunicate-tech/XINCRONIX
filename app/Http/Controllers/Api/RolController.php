<?php

namespace App\Http\Controllers\Api;

use App\Models\Rol;

class RolController extends AbstractApiResourceController
{
    protected string $model = Rol::class;
    protected bool $adminOnlyWrites = true;

    protected array $storeRules = [
        'nombre' => ['required', 'string', 'max:80'],
        'descripcion' => ['nullable', 'string'],
    ];

    protected array $updateRules = [
        'nombre' => ['sometimes', 'string', 'max:80'],
        'descripcion' => ['nullable', 'string'],
    ];
}
