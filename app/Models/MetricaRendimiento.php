<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class MetricaRendimiento extends Model
{
    protected $table = 'metrica_rendimiento';
    protected $primaryKey = 'id_metrica';
    public $timestamps = false;

    protected $guarded = [];

    protected $casts = [
        'valor' => 'decimal:4',
        'fecha_inicio_periodo' => 'date',
        'fecha_fin_periodo' => 'date',
    ];

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'id_usuario');
    }
}