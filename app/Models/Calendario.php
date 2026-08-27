<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Calendario extends Model
{
    protected $table = 'calendario';
    protected $primaryKey = 'id_calendario';
    public $timestamps = false;

    protected $guarded = [];

    protected $casts = [
        'fecha_evento' => 'datetime',
    ];

    public function usuario(): BelongsTo
    {
        return $this->belongsTo(Usuario::class, 'id_usuario');
    }
}