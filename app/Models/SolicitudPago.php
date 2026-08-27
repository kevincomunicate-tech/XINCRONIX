<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class SolicitudPago extends Model
{
    protected $table = 'solicitudes_pago';
    protected $primaryKey = 'id_solicitud';
    public $timestamps = false;

    protected $guarded = [];

    protected $casts = [
        'fecha_creacion' => 'datetime',
        'fecha_revision' => 'datetime',
    ];

    public function empresa(): BelongsTo
    {
        return $this->belongsTo(Empresa::class, 'id_empresa');
    }
}