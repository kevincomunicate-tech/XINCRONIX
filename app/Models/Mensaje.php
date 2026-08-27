<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Mensaje extends Model
{
    protected $table = 'mensajes';
    protected $primaryKey = 'id_mensajes';
    public $timestamps = false;

    protected $guarded = [];

    protected $casts = [
        'estado' => 'boolean',
        'fecha_envio' => 'datetime',
    ];

    public function remitente(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'id_usuario');
    }

    public function destinatario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'id_destinatario');
    }
}
