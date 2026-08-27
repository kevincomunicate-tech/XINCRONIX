<?php

namespace App\Http\Controllers\Api;

use App\Models\SolicitudPago;

class SolicitudPagoController extends AbstractApiResourceController
{
    protected string $model = SolicitudPago::class;
    protected ?string $companyColumn = 'id_empresa';

    protected array $storeRules = [
        'plan' => ['nullable', 'string', 'max:50'],
        'metodo_pago' => ['nullable', 'string', 'max:50'],
        'referencia' => ['nullable', 'string', 'max:100'],
        'notas' => ['nullable', 'string'],
        'ruta_comprobante' => ['nullable', 'string', 'max:300'],
        'estado' => ['nullable', 'string', 'max:30'],
        'fecha_revision' => ['nullable', 'date'],
    ];

    protected array $updateRules = [
        'plan' => ['sometimes', 'string', 'max:50'],
        'metodo_pago' => ['nullable', 'string', 'max:50'],
        'referencia' => ['nullable', 'string', 'max:100'],
        'notas' => ['nullable', 'string'],
        'ruta_comprobante' => ['nullable', 'string', 'max:300'],
        'estado' => ['nullable', 'string', 'max:30'],
        'fecha_revision' => ['nullable', 'date'],
    ];
}
