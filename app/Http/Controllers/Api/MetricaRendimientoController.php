<?php

namespace App\Http\Controllers\Api;

use App\Models\MetricaRendimiento;

class MetricaRendimientoController extends AbstractApiResourceController
{
    protected string $model = MetricaRendimiento::class;
    protected ?string $userColumn = 'id_usuario';

    protected array $storeRules = [
        'tipo_metrica' => ['required', 'string', 'max:100'],
        'valor' => ['required', 'numeric'],
        'fecha_inicio_periodo' => ['required', 'date'],
        'fecha_fin_periodo' => ['required', 'date', 'after_or_equal:fecha_inicio_periodo'],
    ];

    protected array $updateRules = [
        'tipo_metrica' => ['sometimes', 'string', 'max:100'],
        'valor' => ['sometimes', 'numeric'],
        'fecha_inicio_periodo' => ['sometimes', 'date'],
        'fecha_fin_periodo' => ['sometimes', 'date', 'after_or_equal:fecha_inicio_periodo'],
    ];
}
